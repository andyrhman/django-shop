import traceback
from rest_framework import status
from rest_framework.exceptions import NotFound, ValidationError
import stripe
from decouple import config
from django.db import transaction
from django.db.models import Q
from rest_framework import generics, serializers
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from authorization.authentication import JWTAuthentication
from core.models import Address, Cart, Order, OrderItem, OrderItemStatus, User
from order.serializers import OrderSerializer
from order.signals import order_completed

class OrderListAPIView(generics.ListAPIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    
    def get_queryset(self):
        
        queryset = super().get_queryset().prefetch_related('order_items_order')
        
        search = self.request.query_params.get("search", "").strip()
        if search:
            queryset = queryset.filter(
                Q(order_items_order__product_title__icontains=search) | 
                Q(name__icontains=search) |
                Q(email__icontains=search)
            )
            
        return queryset
    
    def get(self, _):
        queryset = self.get_queryset()
        serializer = self.serializer_class(queryset, many=True)
        return Response(serializer.data)
    
class CreateOrderAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    
    @transaction.atomic
    def post(self, request):
        user = request.user
        
        cart_payload = request.data.get("carts", [])
                
        address = Address.objects.filter(user=user).first()
        
        if not address:
            return Response({"message": "Please create your shipping address first"})
        
        # Extract cart_ids, fetch them all in one go
        cart_ids = [c.get("cart_id") for c in cart_payload]
        carts = list(Cart.objects.filter(id__in=cart_ids, user=user))

        # Check for missing carts
        if len(carts) != len(cart_ids):
            # someone passed an invalid cart_id
            raise NotFound("One or more carts were not found.")

        # Check none are already completed
        already_done = [c for c in carts if c.completed]
        if already_done:
            raise ValidationError("One or more carts have already been checked out.")
        
        order = Order.objects.create(
            name=user.fullName,
            email=user.email,
            user=user
        )
        
        line_items = []
        
        for cart in carts:
            OrderItem.objects.create(
                order=order,
                product_title=cart.product_title,
                price=cart.price,
                quantity=cart.quantity,
                product=cart.product,
                variant=cart.variant,
                status=OrderItemStatus.SEDANG_DIKEMAS,
            )
            # attach the cart to the order too
            cart.order = order
            cart.completed = False  # or leave as-is until confirm
            cart.save()

            line_items.append({
                'price_data': {
                    'currency': 'idr',
                    'unit_amount': int(cart.price),
                    'product_data': {
                        'name': f"{cart.product_title} - Variant {cart.variant.name}",
                        'description': cart.product.description,
                        'images': [cart.product.image],
                    },
                },
                'quantity': cart.quantity
            })

        stripe.api_key = config('STRIPE_SECRET_KEY')
        session = stripe.checkout.Session.create(
            success_url='http://localhost:5000/success?source={CHECKOUT_SESSION_ID}',
            cancel_url='http://localhost:5000/error',
            payment_method_types=['card'],
            line_items=line_items,
            mode='payment'
        )

        order.transaction_id = session['id']
        order.save()

        return Response(session, status=status.HTTP_201_CREATED)
            
class ConfirmOrderAPIVIew(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    
    def post(self, request, *args, **kwargs):
        user = request.user
        
        order = Order.objects.filter(transaction_id=request.data.get("source")).first()
        
        if not order:
            raise serializers.ValidationError("Order not found")
        
        carts = Cart.objects.filter(order=order, user=user)
        
        order_items = OrderItem.objects.filter(order=order)
        
        if len(carts) == 0:
            return Response({"message": "Forbidden"}, status=status.HTTP_403_FORBIDDEN)
        
        for cart in carts:
            cart.completed = True
            cart.save()
            
        for order_item in order_items:
            order_item.status = OrderItemStatus.SELESAI
            order_item.save()
            
        order.completed = True
        
        order.save()
        
        order_completed.send(sender=self.__class__, order=order)
        return Response(self.serializer_class(order).data, status=status.HTTP_202_ACCEPTED)
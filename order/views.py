import traceback
import stripe
from decouple import config
from django.db import transaction
from django.db.models import Q
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from authorization.authentication import JWTAuthentication
from core.models import Address, Cart, Order, OrderItem, User
from order.serializers import OrderSerializer


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
    
class OrderCreateAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    
    @transaction.atomic
    def post(self, request):
        user = request.user
        
        data = request.data
        
        address = Address.objects.filter(user=user).first()
        
        if not address:
            return Response({"message": "Please create your shipping address first"})
        
        try:
            order = Order()
            order.name = user.fullName
            order.email = user.email
            order.user = user
            order.save()
            
            line_items = []
            
            for c in data["carts"]:
                cart = Cart.objects.filter(id=c["cart_id"], user=user)
                
                if not cart:
                    return Response({"message": "Cart not found"})
                
                if cart[0].completed == True:
                    return Response({"message": "Invalid order, please add new order."})
                
                orderItem = OrderItem()
                orderItem.order = order
                orderItem.product_title = cart[0].product_title
                orderItem.price = cart[0].price
                orderItem.quantity = cart[0].quantity
                orderItem.product = cart[0].product
                orderItem.variant = cart[0].variant
                orderItem.save()
                
                cart[0].order = order
                cart[0].save()
                
                line_items.append({
                    'price_data': {
                        'currency': 'idr',
                        'unit_amount': int(cart[0].price),
                        'product_data': {
                            'name': cart[0].product_title + ' - Variant ' + cart[0].variant.name,
                            'description': cart[0].product.description,
                            'images': [
                                cart[0].product.image
                            ],
                        },
                    },
                    'quantity': cart[0].quantity
                })

            stripe.api_key = config('STRIPE_SECRET_KEY')

            source = stripe.checkout.Session.create(
                success_url='http://localhost:5000/success?source={CHECKOUT_SESSION_ID}',
                cancel_url='http://localhost:5000/error',
                payment_method_types=['card'],
                line_items=line_items,
                mode='payment'
            )

            order.transaction_id = source['id']
            order.save()

            return Response(source)

        except Exception:
            traceback.print_exc()
            transaction.rollback()
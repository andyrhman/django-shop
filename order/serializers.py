from decouple import config
from django.core.exceptions import BadRequest
from django.db import transaction
from rest_framework import serializers
from order.signals import order_completed
from rest_framework.exceptions import NotFound, PermissionDenied, ValidationError
import stripe

from core.models import Address, Cart, Order, OrderItem, OrderItemStatus, Product, ProductVariation

class ProductSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Product
        fields = "__all__"

class ProductVariationSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductVariation
        fields = "__all__"
        
class OrderItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    variant = ProductVariationSerializer(read_only=True)

    class Meta:
        model = OrderItem
        fields = "__all__"

class OrderSerializer(serializers.ModelSerializer):
    order_items_order = OrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = "__all__"

class ChangeOrderStatusSerializer(serializers.ModelSerializer):
    status = serializers.ChoiceField(
        choices=OrderItemStatus.choices,
        error_messages={
            "invalid_choice": "Status tidak valid. Pilihan yang tersedia adalah: Sedang Dikemas, Dikirim, atau Selesai."
        }
    )
    
    class Meta:
        model = OrderItem
        fields = ['status']
    
    def update(self, instance, validated_data):
        instance.status = validated_data.get("status", instance.status)
        instance.save()
        
        return instance

# ? This is how it look likse using generics.CreateAPIView for create order 
class OrderCreateSerializer(serializers.Serializer):
    carts = serializers.ListField(
        child=serializers.DictField(child=serializers.IntegerField()),
        write_only=True
    )

    class Meta:
        model = Order
        fields = ("carts",)

    def validate_carts(self, carts_payload):
        user = self.context['request'].user
        cart_ids = [c.get("cart_id") for c in carts_payload]

        # bulk-fetch and validate existence
        carts = list(Cart.objects.filter(id__in=cart_ids, user=user))
        if len(carts) != len(cart_ids):
            raise NotFound("One or more carts were not found.")

        # ensure none are already completed
        already_done = [c for c in carts if c.completed]
        if already_done:
            raise ValidationError("One or more carts have already been checked out.")
        return carts

    @transaction.atomic
    def create(self, validated_data):
        request  = self.context['request']
        user     = request.user
        carts    = validated_data['carts']  # this is actually the queryset returned by validate_carts()

        # make sure user has an address
        address = Address.objects.filter(user=user).first()
        if not address:
            raise ValidationError({"detail": "Please create your shipping address first."})

        # create the Order
        order = Order.objects.create(
            user=user,
            name=user.fullName,
            email=user.email,
        )

        # prepare line items for Stripe
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
            cart.order     = order
            cart.completed = False
            cart.save()

            line_items.append({
                "price_data": {
                    "currency": "idr",
                    "unit_amount": int(cart.price),
                    "product_data": {
                        "name": f"{cart.product_title} - Variant {cart.variant.name}",
                        "description": cart.product.description,
                        "images": [cart.product.image],
                    },
                },
                "quantity": cart.quantity,
            })

        # create a Stripe checkout session
        stripe.api_key = config("STRIPE_SECRET_KEY")
        session = stripe.checkout.Session.create(
            success_url="http://localhost:5000/success?source={CHECKOUT_SESSION_ID}",
            cancel_url="http://localhost:5000/error",
            payment_method_types=["card"],
            line_items=line_items,
            mode="payment",
        )

        order.transaction_id = session["id"]
        order.save()
        return session
    
class ConfirmOrderSerializer(serializers.ModelSerializer):
    source = serializers.CharField(write_only=True)
    class Meta:
        model = Order
        fields = ['source']
        
    def validate(self, data):
        user = self.context['request'].user
        
        try:
            order = Order.objects.get(transaction_id=data['source'])
        except Order.DoesNotExist:
            raise NotFound({"message": "Order not found"})
        
        data['source'] = order
        
        if order.completed:
            raise ValidationError({"message": "Your order already completed"})
    
        if not Cart.objects.filter(order=data['source'], user=user).exists():
            raise PermissionDenied({"message": "You are not allowed to do that"})
        
        return data
        
    def create(self, validated_data):
        user = self.context['request'].user
        
        order = validated_data.pop('source')
        
        carts = Cart.objects.filter(order=order, user=user)
        
        order_items = OrderItem.objects.filter(order=order)
        
        for cart in carts:
            cart.completed = True
            cart.save()
            
        for order_item in order_items:
            order_item.status = OrderItemStatus.SEDANG_DIKEMAS
            order_item.save()
            
        order.completed = True
        
        order.save()
        
        order_completed.send(sender=self.__class__, order=order)
        
        return order
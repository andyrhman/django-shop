from rest_framework import serializers

from core.models import Order, OrderItem, Product

class ProductSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Product
        fields = "__all__"

class OrderItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer()
    
    class Meta:
        model = OrderItem
        fields = "__all__"

class OrderSerializer(serializers.ModelSerializer):
    order_items_order = OrderItemSerializer(many=True)
    
    class Meta:
        model = Order
        fields = "__all__"
from rest_framework import serializers

from core.models import Order, OrderItem, OrderItemStatus, Product, ProductVariation

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
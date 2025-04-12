from rest_framework import serializers

from core.models import Cart, Product, ProductVariation, User


class UserSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = User
        fields = "__all__"
        
class ProductVariantSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = ProductVariation
        fields = "__all__"
        
class ProductSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Product
        fields = "__all__"
        
class CartSerializer(serializers.ModelSerializer):
    variant = ProductVariantSerializer()
    product = ProductSerializer()
    
    class Meta:
        model = Cart
        fields = "__all__"
        
class CartAdminSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    
    class Meta:
        model = Cart
        fields = "__all__"
        
class CartCreateSerializer(serializers.ModelSerializer):
    product = serializers.UUIDField()
    
    variant = serializers.UUIDField()
    
    class Meta:
        model = Cart
        fields = ['quantity', 'product', 'variant']
        
    def validate_product(self, value):
        if not Product.objects.filter(id=value).exists():
            raise serializers.ValidationError("Product does not exists")
        return value
    
    def validate_variant(self, value):
        if not ProductVariation.objects.filter(id=value).exists():
            raise serializers.ValidationError("Product variation does not exists")
        return value
    
    def create(self, validated_data):
        request = self.context.get("request")
        user = request.user

        product_id = validated_data.pop("product", [])
        product = Product.objects.get(id=product_id)
        
        input_quantity = validated_data.pop("quantity", 1)
        
        variant_id = validated_data.pop("variant", [])
        variant = ProductVariation.objects.get(id=variant_id)
        
        defaults = {
            "quantity": input_quantity,
            "price": validated_data.get("price", product.price),
            "product_title": validated_data.get("product_title", product.title),
        }
        
        cart_item, created = Cart.objects.get_or_create(
            product=product,
            variant=variant,
            user=user,
            defaults=defaults
        )
        
        if not created:
            cart_item.quantity += input_quantity
            cart_item.save()
            
        return cart_item

class CartQuantityUpdateSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Cart
        fields = ['quantity']
        
    def update(self, instance, validated_data):
        instance.quantity = validated_data.get('quantity', instance.quantity)
        instance.save()
        
        return instance
        
        
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.status import HTTP_404_NOT_FOUND

from core.models import Cart, Product, ProductVariation, User

class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ['id', 'fullName', 'email', 'username', 'password', 'is_user', 'is_verified', 'created_at', 'updated_at']
        extra_kwargs = {
            'password': {'write_only': True}
        }    
          
    def create(self, validated_data):
        password = validated_data.pop('password', None)
        
        email = validated_data.get('email', '').lower()
        username = validated_data.get('username', '').lower()
        
        validated_data['email'] = email
        validated_data['username'] = username

        instance = self.Meta.model(**validated_data)
        
        if password is not None:
            instance.set_password(password)
        instance.save()
        return instance
        
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
        
    def validate(self, data):
        # 1) ensure product exists
        try:
            product = Product.objects.get(id=data['product'])
        except Product.DoesNotExist:
            raise ValidationError({"product": "Product does not exist."})

        # 2) ensure variant exists *and* belongs to that product
        try:
            variant = ProductVariation.objects.get(id=data['variant'], product=product)
        except ProductVariation.DoesNotExist:
            raise ValidationError({"variant": "Product variant does not exist for this product."})

        # stash the actual instances for create()
        data['product_obj'] = product
        data['variant_obj'] = variant
        return data
    
    def create(self, validated_data):
        request = self.context.get("request")
        user = request.user

        product_id = validated_data.pop("product", [])
        product = Product.objects.get(id=product_id)
        
        input_quantity = validated_data.pop("quantity", 1)
        
        variant_id = validated_data.pop("variant", [])
        variant = ProductVariation.objects.get(id=variant_id, product=product_id)

        if not variant:
            return Response({"message": "Product variant does not exists"}, status=HTTP_404_NOT_FOUND)
        
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
        
        
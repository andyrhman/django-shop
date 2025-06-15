import cloudinary.uploader
from rest_framework import exceptions, serializers
from decouple import config
from core.models import Order, Product, ProductVariation, Review, User

class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ['id', 'fullName', 'email', 'username', 'password', 'is_user', 'is_verified', 'created_at', 'updated_at']
        extra_kwargs = {
            'password': {'write_only': True}
        }    
          
    def create(self, validated_data):
        password = validated_data.pop('password', None)
        
        # Convert email and username to lowercase
        email = validated_data.get('email', '').lower()
        username = validated_data.get('username', '').lower()
        
        # Update the dictionary with lowercase values
        validated_data['email'] = email
        validated_data['username'] = username

        instance = self.Meta.model(**validated_data)
        
        if password is not None:
            instance.set_password(password)
        instance.save()
        return instance

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = "__all__"

class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = "__all__"

class ProductVariationSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductVariation
        fields = "__all__"

class ReviewSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    product = ProductSerializer(read_only=True)

    class Meta:
        model = Review
        fields = "__all__"

cloudinary.config(
    cloud_name = config('CLOUDINARY_CLOUD_NAME'),
    api_key    = config('CLOUDINARY_API_KEY'),
    api_secret = config('CLOUDINARY_API_SECRET')
)

class CreateReviewSerializer(serializers.ModelSerializer):
    order_id    = serializers.UUIDField(write_only=True)
    product_id  = serializers.UUIDField(write_only=True)
    variant_id  = serializers.UUIDField(write_only=True)
    image       = serializers.FileField(write_only=True, required=False)

    class Meta:
        model  = Review
        fields = ['star','comment','image','product_id','variant_id','order_id']

    def validate(self, data):
        request = self.context['request']

        image_file = request.FILES.get('image')
        if image_file:
            try:
                result = cloudinary.uploader.upload(
                    image_file,
                    folder='djangoshop/reviews'
                )
                url = result.get('secure_url')
                if not url:
                    raise Exception('No URL returned from Cloudinary')
                data['image'] = url
            except Exception as e:
                raise serializers.ValidationError({
                    'image': f'Upload failed: {str(e)}'
                })

        try:
            order = Order.objects.get(id=data['order_id'])
        except Order.DoesNotExist:
            raise exceptions.NotFound({"message": "Order not found"})

        try:
            product = Product.objects.get(id=data['product_id'])
        except Product.DoesNotExist:
            raise exceptions.NotFound({"message": "Product not found"})

        try:
            variant = ProductVariation.objects.get(id=data['variant_id'])
        except ProductVariation.DoesNotExist:
            raise exceptions.NotFound({"message": "Product variant not found"})

        user = request.user
        if order.user != user or not order.completed:
            raise exceptions.PermissionDenied("You're not allowed to review that order.")

        if not (1 <= data['star'] <= 5):
            raise serializers.ValidationError("Star must be between 1 and 5.")

        if Review.objects.filter(
            user=user, order=order, product=product, variants=variant
        ).exists():
            raise serializers.ValidationError("Already reviewed.")

        data['order_id']   = order
        data['product_id'] = product
        data['variant_id'] = variant

        return data

    def create(self, validated_data):
        user = self.context['request'].user

        return Review.objects.create(
            user       = user,
            order      = validated_data.pop('order_id'),
            variants   = validated_data.pop('variant_id'),
            product    = validated_data.pop('product_id'),
            **validated_data
        )
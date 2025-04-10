from django.db.migrations import serializer
from django.utils.text import slugify
from rest_framework import serializers
from rest_framework.response import Response

from core.models import Category, Product, ProductImages, ProductVariation, Review


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = "__all__"
        
class ProductVariationSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductVariation
        fields = "__all__"
        
class ProductImagesSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImages
        fields = "__all__"

class ReviewSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField()
    class Meta:
        model = Review
        fields = ['id', 'star', 'comment', 'image', 'created_at', 'user']
        
class ProductSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    products_images = ProductImagesSerializer(many=True, read_only=True)
    products_variation = ProductVariationSerializer(many=True, read_only=True)
    review_products     = ReviewSerializer(many=True, read_only=True)
    averageRating       = serializers.SerializerMethodField()
    reviewCount         = serializers.SerializerMethodField()

    class Meta:
        model  = Product
        fields = [
            'id','title','slug','description','image','price',
            'category','products_images','products_variation',
            'created_at', 'updated_at',
            'review_products','averageRating','reviewCount',
        ]

    def get_averageRating(self, obj):
        qs = obj.review_products.all()
        if not qs.exists():
            return 0
        return round(sum(r.star for r in qs) / qs.count(), 2)

    def get_reviewCount(self, obj):
        return obj.review_products.count()
    
class ProductAdminSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    products_images = ProductImagesSerializer(many=True, read_only=True)
    products_variation = ProductVariationSerializer(many=True, read_only=True)

    class Meta:
        model  = Product
        fields = [
            'id','title','slug','description','image','price',
            'category','products_images','products_variation',
        ]

class ProductCreateSerializer(serializers.ModelSerializer):
    # * The body request for foreign keys, category, product images, product variations
    
    # ? We use serializers.UUIDField since the body request only needs single uuid
    category = serializers.UUIDField(write_only=True)
    
    # ? We use serializers.ListField here because the body request needs multiple objects inside the array
    images = serializers.ListField(
        child=serializers.CharField(), write_only=True
    )
    
    variants = serializers.ListField(
        child=serializers.CharField(), write_only=True
    )
    
    class Meta:
        model = Product
        fields = ['title', 'description', 'image', 'price', 'category', 'images', 'variants']
        
    def validate_category(self, value): # ? the function name should follow the name of the variables above, example --> validate_thevariablename
        if not Category.objects.filter(id=value).exists():
            raise serializers.ValidationError("Category does not exist")
        return value
    
    def create(self, validated_data):
        # ? Just to make sure inside the pop bracket should be the same as the serializer ListField
        # ? you could say this look like a body request
        images = validated_data.pop('images', [])
        variants = validated_data.pop('variants', [])
        
        # ? Just to make sure inside the pop bracket should be the same as the serializer UUIDField
        cat_id = validated_data.pop('category', [])
        category = Category.objects.filter(id=cat_id)
        
        # ? Title to slug
        title = validated_data.get('title')
        slug = slugify(title)
        
        product = Product.objects.create(
            slug=slug,
            category=category,
            **validated_data
        )
        
        for img in images:
            ProductImages.objects.create(
                product=product,
                name=img
            )
        
        for variant in variants:
            ProductVariation.objects.create(
                product=product,
                name=variant
            )
        
        return product

    # ? If you have a foreign key that needs to be updated then use this function, besides that ignore this function
    def update(self, instance, validated_data):
        # Handle the category update conversion
        cat_id = validated_data.pop('category', None)
        if cat_id is not None:
            try:
                instance.category = Category.objects.get(id=cat_id)
            except Category.DoesNotExist:
                raise serializers.ValidationError("Category does not exist")
        
        # Update the rest of the fields normally
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance

class ProductVariationCreateSerializer(serializers.ModelSerializer):
    name = serializers.ListField(
        child=serializers.CharField()
    )
    
    product = serializers.UUIDField()

    class Meta:
        model = ProductVariation
        fields = "__all__"
        
    def validate_product(self, value):
        if not Product.objects.filter(id=value).exists():
            raise serializers.ValidationError("Product does not exists")
        return value
        
    def create(self, validated_data):
        name = validated_data.pop('name', [])
        product_id = validated_data.pop('product', [])
        product = Product.objects.get(id=product_id)
        
        variants = []
        for n in name:
            variant = ProductVariation.objects.create(
                name=n,
                product=product
            )
            
            variants.append(variant)
            
        return variants
            
class ProductImagesCreateSerializer(serializers.ModelSerializer):
    name = serializers.ListField(
        child=serializers.CharField()
    )
    
    product = serializers.UUIDField()
    class Meta:
        model = ProductImages
        fields = "__all__"
    
    def validate_product(self, value):
        if not Product.objects.filter(id=value).exists():
            raise serializers.ValidationError("Product does not exists")
        return value
     
    def create(self, validated_data):
        name = validated_data.pop('name', [])
        
        product_id = validated_data.pop('product', [])
        product = Product.objects.get(id=product_id)
        
        images = []
        for n in name:
            image = ProductImages.objects.create(
                name=n,
                product=product
            )
            images.append(image)

        return images
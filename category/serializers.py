from rest_framework import serializers

from core.models import Category, Product

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = "__all__"
        
class CategorySerializer(serializers.ModelSerializer):
    product_categories = ProductSerializer(many=True, read_only=True)
    
    class Meta:
        model = Category
        fields = "__all__"
    
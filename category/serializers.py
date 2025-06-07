from rest_framework import serializers

from core.models import Category, Product

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = "__all__"
        
class CategorySerializer(serializers.ModelSerializer):
    product_total = serializers.IntegerField(read_only=True)

    class Meta:
        model = Category
        fields = ["id", "name", "product_total"]
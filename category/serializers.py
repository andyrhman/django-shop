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
        
class ProductCategorySerializer(serializers.ModelSerializer):
    product_categories = serializers.SerializerMethodField()

    class Meta:
        model  = Category
        fields = "__all__"

    def get_product_categories(self, obj):
        latest_8 = (
            obj.product_categories
               .order_by('-created_at')
               .all()[:8]
        )
        return ProductSerializer(latest_8, many=True).data
from django.urls import path

from product.views import ProductImagesCDAPIView, ProductListCreateAPIView, ProductRUDAPIView, ProductVariantCDAPIView

urlpatterns = [
    path('products', ProductListCreateAPIView.as_view()),
    path('products/<str:id>', ProductRUDAPIView.as_view()),
    path('product-variants', ProductVariantCDAPIView.as_view()),
    path('product-variants/<str:id>', ProductVariantCDAPIView.as_view()),
    path('product-images', ProductImagesCDAPIView.as_view()),
    path('product-images/<str:id>', ProductImagesCDAPIView.as_view()),
]
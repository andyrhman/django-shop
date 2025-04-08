from django.urls import path

from product.views import ProductListCreateAPIView, ProductRUDAPIView

urlpatterns = [
    path('products', ProductListCreateAPIView.as_view()),
    path('products/<str:id>', ProductRUDAPIView.as_view()),
    # path('product-variants', ProductVariationUpdateAPIView.as_view()),
]
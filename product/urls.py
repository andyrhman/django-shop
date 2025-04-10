
from django.urls import path

from product.views import ProductAPIView, ProductAvgRatingAPIView, ProductVariantsAPIView, ProductsAPIView

urlpatterns = [
    path('products', ProductsAPIView.as_view()),
    path('product/<str:slug>', ProductAPIView.as_view()),
    path('product/rating/<str:id>', ProductAvgRatingAPIView.as_view()),
    path('variants', ProductVariantsAPIView.as_view()),
]
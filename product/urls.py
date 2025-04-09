
from django.urls import path

from product.views import ProductsAPIView

urlpatterns = [
    path('products', ProductsAPIView.as_view()),
]
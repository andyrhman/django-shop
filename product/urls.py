
from django.urls import path

from product.views import ProductListCreateAPIView, ProductRUDAPIView

urlpatterns = [
    path('products', ProductListCreateAPIView.as_view()),
]
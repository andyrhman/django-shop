from django.urls import path

from product.views import ProductsPageView

urlpatterns = [
    path('products/', ProductsPageView.as_view(), name='products')
]
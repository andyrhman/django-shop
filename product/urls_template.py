from django.urls import path

from product.views import ProductDetailPageView, ProductsPageView

urlpatterns = [
    path('products/', ProductsPageView.as_view(), name='products'),
    path('products/<slug:slug>/', ProductDetailPageView.as_view(), name='products-detail')
]
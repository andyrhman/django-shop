
from django.urls import path

from product.views import BestSellingProductAPIView, NewlyAddedProductAPIView, ProductAPIView, ProductAvgRatingAPIView, ProductPriceFilterAPIView, ProductVariantsAPIView, ProductsAPIView

urlpatterns = [
    path('products', ProductsAPIView.as_view(), name='api-products'),
    path('product/<str:slug>/', ProductAPIView.as_view()),
    path('product/rating/<str:id>', ProductAvgRatingAPIView.as_view()),
    path('variants', ProductVariantsAPIView.as_view()),
    path('newly-added', NewlyAddedProductAPIView.as_view(), name='api-newlyadded'),
    path('best-selling', BestSellingProductAPIView.as_view(), name='api-bestselling'),    
    path("products/filter-by-price", ProductPriceFilterAPIView.as_view(), name="filter-by-price"),
]
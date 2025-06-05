
from django.urls import path

from product.views import BestSellingProductAPIView, NewlyAddedProductAPIView, ProductAPIView, ProductAvgRatingAPIView, ProductVariantsAPIView, ProductsAPIView

urlpatterns = [
    path('products', ProductsAPIView.as_view()),
    path('product/<str:slug>', ProductAPIView.as_view()),
    path('product/rating/<str:id>', ProductAvgRatingAPIView.as_view()),
    path('variants', ProductVariantsAPIView.as_view()),
    path('newly-added', NewlyAddedProductAPIView.as_view(), name='api-newlyadded'),
    path('best-selling', BestSellingProductAPIView.as_view(), name='api-bestselling'),
]
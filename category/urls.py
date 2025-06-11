from django.urls import path

from category.views import CategoriesAPIView, CategoriesWithProductsAPIView

urlpatterns = [
    path('categories', CategoriesAPIView.as_view(), name='api-categories'),
    path('categories/product-related/<str:id>', CategoriesWithProductsAPIView.as_view(), name='api-productrelated'),
]
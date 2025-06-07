from django.urls import path

from category.views import CategoriesAPIView

urlpatterns = [
    path('categories', CategoriesAPIView.as_view(), name='api-categories'),
]
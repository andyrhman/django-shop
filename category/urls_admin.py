from django.urls import path

from category.views import CategoryGenericAPIView


urlpatterns = [
    path("category", CategoryGenericAPIView.as_view()),
    path("category/<str:id>", CategoryGenericAPIView.as_view()),
]

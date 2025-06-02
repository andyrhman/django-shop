
from django.urls import path

from review.views import AdminReviewAPIView

urlpatterns = [
    path('reviews', AdminReviewAPIView.as_view()),
    path('reviews/<str:id>', AdminReviewAPIView.as_view())
]
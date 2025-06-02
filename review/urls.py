from django.urls import path

from review.views import UserReviewAPIView

urlpatterns = [
    path('review', UserReviewAPIView.as_view()),
    path('reviews/<str:id>', UserReviewAPIView.as_view())
]
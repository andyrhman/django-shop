from django.urls import path

from review.views import UserReviewAPIView


urlpatterns = [
    path('review', UserReviewAPIView.as_view())
]
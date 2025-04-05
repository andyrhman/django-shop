from django.urls import path

from authorization.views import ResendVerifyAPIView, VerifyAccountAPIView

urlpatterns = [
    path("verify", ResendVerifyAPIView.as_view()),
    path("verify/<str:token>", VerifyAccountAPIView.as_view())
]
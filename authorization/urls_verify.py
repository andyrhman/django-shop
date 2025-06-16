from django.urls import path

from authorization.views import ResendVerifyAPIView, VerifyAccountAPIView

urlpatterns = [
    path("verify", ResendVerifyAPIView.as_view(), name='api-resend-verify'),
    path("verify/<str:token>", VerifyAccountAPIView.as_view(), name='api-verify-account'),
]
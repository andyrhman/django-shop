from django.urls import path

from authorization.views import LoginPageView, RegisterPageView, VerifyPageView

urlpatterns = [
    path('register/', RegisterPageView.as_view(), name='register'),
    path('login/', LoginPageView.as_view(), name='login'),
    path('verify/<str:token>/', VerifyPageView.as_view(), name='verify'),
]
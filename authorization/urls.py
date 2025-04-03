from django.urls import path

from authorization.views import LoginAPIView, RegisterAPIView, UserAPIView

urlpatterns = [
    path("register", RegisterAPIView.as_view()),
    path("login", LoginAPIView.as_view()),
    path("", UserAPIView.as_view())
]

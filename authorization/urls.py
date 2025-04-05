from django.urls import path

from authorization.views import LoginAPIView, LogoutAPIView, RegisterAPIView, ResendVerifyAPIView, UpdateInfoAPIView, UpdatePasswordAPIView, UserAPIView, VerifyAccountAPIView

urlpatterns = [
    path("register", RegisterAPIView.as_view()),
    path("login", LoginAPIView.as_view()),
    path("", UserAPIView.as_view()),
    path("logout", LogoutAPIView.as_view()),
    path("info", UpdateInfoAPIView.as_view()),
    path("password", UpdatePasswordAPIView.as_view()),
]

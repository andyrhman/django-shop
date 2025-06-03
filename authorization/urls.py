from django.urls import path

from authorization.views import LoginAPIView, LogoutAPIView, RegisterAPIView, UpdateInfoAPIView, UpdatePasswordAPIView, UserAPIView 

urlpatterns = [
    path("register", RegisterAPIView.as_view(), name='api-register'),
    path("login", LoginAPIView.as_view(), name='api-login'),
    path("", UserAPIView.as_view()),
    path("logout", LogoutAPIView.as_view()),
    path("info", UpdateInfoAPIView.as_view()),
    path("password", UpdatePasswordAPIView.as_view()),
]

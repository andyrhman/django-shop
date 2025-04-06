from django.urls import path

from user.views import TotalUsersAPIView, UsersAPIView


urlpatterns = [
    path("users", UsersAPIView.as_view()),
    path("total-users", TotalUsersAPIView.as_view())
]
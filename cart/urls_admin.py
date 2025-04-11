from django.urls import path

from cart.views import CartAdminListAPIView, CartsAdminRetriveAPIView


urlpatterns = [
    path('carts', CartAdminListAPIView.as_view()),
    path('carts/<str:id>', CartsAdminRetriveAPIView.as_view()),
]
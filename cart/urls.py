
from django.urls import path

from cart.views import CartCRUDAPIView, TotalCartAPIView

urlpatterns = [
    path('cart', CartCRUDAPIView.as_view()),
    path('cart/<str:id>', CartCRUDAPIView.as_view()),
    path('cart-total', TotalCartAPIView.as_view()),
]
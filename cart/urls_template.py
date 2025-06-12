from django.urls import path

from cart.views import CartPageView

urlpatterns = [
    path('cart', CartPageView.as_view(), name='cart')
]
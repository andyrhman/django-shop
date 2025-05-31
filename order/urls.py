
from django.urls import path

from order.views import ConfirmOrderAPIVIew, CreateOrderAPIView, GetUserOrder

urlpatterns = [
    path('checkout/orders', CreateOrderAPIView.as_view()),
    path('checkout/orders/confirm', ConfirmOrderAPIVIew.as_view()),
    path('order-user', GetUserOrder.as_view()),
]
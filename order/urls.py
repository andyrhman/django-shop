
from django.urls import path

from order.views import ConfirmOrderAPIVIew, CreateOrderAPIView, OrderListAPIView

urlpatterns = [
    path('orders', OrderListAPIView.as_view()),
    path('checkout/orders', CreateOrderAPIView.as_view()),
    path('checkout/orders/confirm', ConfirmOrderAPIVIew.as_view())
]
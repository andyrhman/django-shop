
from django.urls import path

from order.views import ConfirmOrderGenericAPIView, CreateOrderAPIView, GetUserOrder

urlpatterns = [
    path('checkout/orders', CreateOrderAPIView.as_view()),
    path('checkout/orders/confirm', ConfirmOrderGenericAPIView.as_view()),
    path('order-user', GetUserOrder.as_view()),
]
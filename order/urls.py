
from django.contrib.messages import api
from django.urls import path

from order.views import ConfirmOrderGenericAPIView, CreateOrderAPIView, GetUserOrder

urlpatterns = [
    path('checkout/orders', CreateOrderAPIView.as_view(), name='api-create-order'),
    path('checkout/orders/confirm', ConfirmOrderGenericAPIView.as_view(), name='api-confirm-order'),
    path('order-user', GetUserOrder.as_view(), name='api-get-user-order'),
]
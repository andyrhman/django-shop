
from django.urls import path

from order.views import OrderCreateAPIView, OrderListAPIView

urlpatterns = [
    path('orders', OrderListAPIView.as_view()),
    path('checkout/orders', OrderCreateAPIView.as_view())
]
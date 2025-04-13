from django.urls import path

from order.views import OrderListAPIView

urlpatterns = [
    path('orders', OrderListAPIView.as_view())
]
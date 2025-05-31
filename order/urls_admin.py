from django.urls import path

from order.views import ChangeOrderStatus, GetOrderItem, OrderListAPIView

urlpatterns = [
    path('orders', OrderListAPIView.as_view()),
    path('order-items/<str:id>', GetOrderItem.as_view()),
    path('orders/<str:id>', ChangeOrderStatus.as_view())
]
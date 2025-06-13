from django.urls import path

from order.views import UserOrderPageView

urlpatterns = [
    path('my-order', UserOrderPageView.as_view(), name='my-order')
]
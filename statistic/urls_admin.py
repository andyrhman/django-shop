from django.urls import path

from statistic.views import CartsStatAPIView, OrdersStatAPIView, StatsAPIView, UsersStatAPIView

urlpatterns = [
    path('stats', StatsAPIView().as_view()),
    path('order-chart', OrdersStatAPIView.as_view(), name='orders-stats'),
    path('cart-chart',  CartsStatAPIView.as_view(),  name='carts-stats'),
    path('user-chart',  UsersStatAPIView.as_view(),  name='users-stats'), 
]
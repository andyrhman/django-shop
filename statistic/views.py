from django.db.models import F, Count, Sum
from django.db.models.functions import TruncDate
from rest_framework.authentication import get_user_model
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions

from authorization.authentication import JWTAuthentication
from core.models import Cart, Order, OrderItem, Product, Review

User = get_user_model()

class StatsAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes     = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        data = {
            'user_total':       User.objects.count(),
            'product_total':    Product.objects.count(),
            'order_total':      Order.objects.count(),
            'order_item_total': OrderItem.objects.count(),
            'review_total':     Review.objects.count(),
            'cart_total':       Cart.objects.count(),
        }
        return Response(data, status=status.HTTP_200_OK)


class OrdersStatAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes     = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        qs = (
            OrderItem.objects
            .filter(order__completed=True)
            .annotate(date=TruncDate('order__created_at'))
            .values('date')
            .annotate(sum=Sum(F('price') * F('quantity')))
            .order_by('date')
        )
        data = [
            {'date': entry['date'].strftime('%Y-%m-%d'),
                'sum': str(entry['sum'] or 0)}
            for entry in qs
        ]
        return Response(data, status=status.HTTP_200_OK)


class CartsStatAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes     = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        qs = (
            Cart.objects
            .annotate(date=TruncDate('created_at'))
            .values('date')
            .annotate(sum=Sum('quantity'))
            .order_by('date')
        )
        data = [
            {'date': entry['date'].strftime('%Y-%m-%d'),
                'sum': str(entry['sum'] or 0)}
            for entry in qs
        ]
        return Response(data, status=status.HTTP_200_OK)

class UsersStatAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes     = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        qs = (
            User.objects
            .annotate(date=TruncDate('created_at'))
            .values('date')
            .annotate(count=Count('id'))
            .order_by('date')
        )
        data = [
            {'date': entry['date'].strftime('%Y-%m-%d'),
                'count': str(entry['count'] or 0)}
            for entry in qs
        ]
        return Response(data, status=status.HTTP_200_OK)

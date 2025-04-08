from django.shortcuts import render
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from authorization.authentication import JWTAuthentication
from core.models import Product, ProductVariation
from product.serializers import ProductCreateSerializer, ProductSerializer, ProductVariationSerializer

# Create your views here.
class ProductListCreateAPIView(generics.ListCreateAPIView):
    """
    GET  /api/products/      → list all products
    POST /api/products/      → create new product
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = Product.objects.all()
    
    def get_serializer_class(self):
        if self.request.method == 'POST': # ? If the request is POST go with product creaet serializer
            return ProductCreateSerializer
        return ProductSerializer
    
class ProductRUDAPIView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET    /api/products/<slug>/   → retrieve single by slug
    PUT    /api/products/<slug>/   → update
    DELETE /api/products/<slug>/   → delete
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = Product.objects.all()
    lookup_field = 'id'
    
    def get_serializer_class(self):
        if self.request.method in ('PUT', 'PATCH'):
            return ProductCreateSerializer
        return ProductSerializer

    def put(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)
    
    def perform_destroy(self, instance):
        return super().perform_destroy(instance)
    

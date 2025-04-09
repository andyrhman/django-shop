from django.shortcuts import render
from rest_framework import generics, mixins, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from authorization.authentication import JWTAuthentication
from core.models import Product, ProductImages, ProductVariation
from product.serializers import ProductAdminSerializer, ProductCreateSerializer, ProductImagesCreateSerializer, ProductImagesSerializer, ProductSerializer, ProductVariationCreateSerializer, ProductVariationSerializer

# Create your views here.
class ProductListCreateAPIView(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    generics.GenericAPIView
):
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
        return ProductAdminSerializer
    
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)
    
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)
    
class ProductRUDAPIView(
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    generics.GenericAPIView
):
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
        return ProductAdminSerializer

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)
    
    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)

class ProductVariantCDAPIView(
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    generics.GenericAPIView
):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = ProductVariation.objects.all()
    lookup_field = 'id'
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return ProductVariationCreateSerializer
        return ProductSerializer
    
    def post(self, request, *args, **kwargs):
        # ? defining the serializer variable and getting the request data using self.get_serializer()
        serializer = self.get_serializer(data=request.data)
        
        serializer.is_valid(raise_exception=True)

        # ? saving the data to the database
        saved_variants = serializer.save()
        
        response_variants = ProductVariationSerializer(saved_variants, many=True)
        return Response(response_variants.data)
        
    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)
    
class ProductImagesCDAPIView(
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    generics.GenericAPIView
):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = ProductImagesCreateSerializer
    queryset = ProductImages.objects.all()
    lookup_field = 'id'
    
    def get_serializer_class(self):
        return super().get_serializer_class()
    
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        saved_images = serializer.save()
        
        images_serializer = ProductImagesSerializer(saved_images, many=True)
        return Response(images_serializer.data)
    
class ProductsAPIView(generics.ListAPIView):
    serializer_class = ProductSerializer
    queryset = Product.objects.all().order_by('-updated_at')
    
    def get(self, request, *args, **kwargs):
        products = self.get_queryset()
        
        s = request.query_params.get("search", "")
        if s:
            products = list(
                [
                    p
                    for p in products
                    if (s.lower() in p.title.lower())
                    or (s.lower() in p.description.lower())
                ]
            )
            
        serializer = self.serializer_class(products, many=True)
        
        return Response(serializer.data)
from django.shortcuts import render
from rest_framework import generics, mixins, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db.models import Q
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
    queryset = Product.objects.all()

    def get_queryset(self):
        # Start with the base queryset and include related objects if needed.
        queryset = super().get_queryset().select_related('category').prefetch_related('products_variation')
        
        # --- SEARCH ---
        search = self.request.query_params.get("search", "").strip()
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) | Q(description__icontains=search)
            )
        
        # --- FILTER BY VARIANT ---
        filter_by_variant = self.request.query_params.get("filterByVariant", "").strip()
        if filter_by_variant:
            variants = [v.strip() for v in filter_by_variant.split(",") if v.strip()]
            queryset = queryset.filter(products_variation__name__in=variants).distinct()
        
        # --- FILTER BY CATEGORY ---
        filter_by_category = self.request.query_params.get("filterByCategory", "").strip()
        if filter_by_category:
            categories = [c.strip() for c in filter_by_category.split(",") if c.strip()]
            queryset = queryset.filter(category__name__in=categories)
        
        # --- SORTING ---
        sort_by_price = self.request.query_params.get("sortByPrice", "").strip().lower()
        sort_by_date = self.request.query_params.get("sortByDate", "").strip().lower()
        
        if sort_by_price:

            if sort_by_price == "asc":
                queryset = queryset.order_by("-price")
            else:
                queryset = queryset.order_by("price")
        elif sort_by_date:
            if sort_by_date == "newest":
                queryset = queryset.order_by("-created_at")
            else:
                queryset = queryset.order_by("created_at")
        else:
            queryset = queryset.order_by("-updated_at")
        
        return queryset

    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.serializer_class(queryset, many=True)
        return Response(serializer.data)
    
class ProductAvgRatingAPIView(generics.RetrieveAPIView):
    queryset = Product.objects.all()
    lookup_field = 'id'
    serializer_class = ProductSerializer
    
    def get(self, request, *args, **kwargs):
        response = super().retrieve(request, *args, **kwargs)
        
        # ? We will fetch only the averageRating to show in the response
        average_rating = response.data.get('averageRating')
        
        return Response({"averageRating": average_rating})
    
class ProductVariantsAPIView(generics.ListAPIView):
    serializer_class = ProductVariationSerializer
    queryset = ProductVariation.objects.all()
    
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)
    
class ProductAPIView(generics.RetrieveAPIView):
    serializer_class = ProductSerializer
    queryset = Product.objects.all()
    lookup_field = 'slug'
    
    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)
import math
from django.core.cache import cache
from django.db.models.functions import Coalesce
from django.views.generic import TemplateView
from rest_framework import generics, mixins, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db.models import Sum, Q, IntegerField, Value
from authorization.authentication import JWTAuthentication
from core.models import Product, ProductImages, ProductVariation
from core.utils import TenPerPagePagination
from product.serializers import OnlyProductSerializer, ProductAdminSerializer, ProductCreateSerializer, ProductImagesCreateSerializer, ProductImagesSerializer, ProductSerializer, ProductVariationCreateSerializer, ProductVariationSerializer

# Create your views here.
class ProductListCreateAPIView(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    generics.GenericAPIView
):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = Product.objects.all()
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return ProductCreateSerializer
        return ProductAdminSerializer
    
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)
    
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)
    
    def perform_create(self, serializer):
        product = serializer.save()
        cache.delete_pattern("products:*")
        return product
    
class ProductRUDAPIView(
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    generics.GenericAPIView
):

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
    
    def perform_update(self, serializer):
        product = serializer.save()
        cache.delete_pattern("products:*")
        return product

    def perform_destroy(self, instance):
        instance.delete()
        cache.delete_pattern("products:*")
    
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
        serializer = self.get_serializer(data=request.data)
        
        serializer.is_valid(raise_exception=True)

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
    serializer_class = ProductAdminSerializer
    pagination_class = TenPerPagePagination

    def get_queryset(self):
        qs = Product.objects.all().select_related("category")

        search = self.request.query_params.get("search", "").strip()
        if search:
            qs = qs.filter(
                Q(title__icontains=search) | 
                Q(description__icontains=search) |
                Q(category__name__icontains=search)
            )

        fbc = self.request.query_params.get("filterByCategory", "").strip()
        if fbc:
            cats = [c.strip() for c in fbc.split(",") if c.strip()]
            qs = qs.filter(category__name__in=cats)

        sbp = self.request.query_params.get("sortByPrice", "").strip().lower()
        sbd = self.request.query_params.get("sortByDate", "").strip().lower()
        if sbp:
            qs = qs.order_by("price" if sbp == "desc" else "-price")
        elif sbd:
            qs = qs.order_by("-created_at" if sbd == "newest" else "created_at")
        else:
            qs = qs.order_by("-updated_at")

        return qs

    def list(self, request, *args, **kwargs):
        cache_key = f"products:{request.get_full_path()}"
        cached = cache.get(cache_key)
        if cached is not None:
            return Response(cached)

        qs    = self.filter_queryset(self.get_queryset())
        total = qs.count()

        page_qs    = self.paginate_queryset(qs)
        serializer = self.get_serializer(page_qs, many=True)
        data       = serializer.data

        per_page     = self.paginator.page_size
        current_page = int(request.query_params.get(self.paginator.page_query_param, 1))
        last_page    = math.ceil(total / per_page)

        payload = {
            "data": data,
            "meta": {
                "total": total,
                "page": current_page,
                "last_page": last_page,
            }
        }

        cache.set(cache_key, payload, timeout=60 * 30)

        return Response(payload)
    
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
    
class NewlyAddedProductAPIView(generics.ListAPIView):
    serializer_class = OnlyProductSerializer

    def get_queryset(self):
        return Product.objects.order_by('-created_at')[:8]

class BestSellingProductAPIView(generics.ListAPIView):
    serializer_class = OnlyProductSerializer

    def get_queryset(self):
        qs = Product.objects.annotate(
            total_sold=Coalesce(
                Sum(
                    'order_items_products__quantity',
                    filter=Q(order_items_products__order__completed=True)
                ),
                Value(0),
                output_field=IntegerField()
            )
        ).order_by('-total_sold')

        return qs[:6]
    
class ProductPriceFilterAPIView(generics.ListAPIView):
    serializer_class = ProductSerializer

    def get_queryset(self):
        price_param = self.request.data.get("price")
        try:
            price_value = float(price_param)
        except (TypeError, ValueError):
            return Product.objects.none()

        return Product.objects.filter(price__gte=price_value).order_by("price")

    def post(self, request, *args, **kwargs):
        if "price" not in request.data:
            return Response(
                {"detail": "Field 'price' is required."},
                status=status.HTTP_400_BAD_REQUEST
            )
        try:
            float(request.data["price"])
        except (TypeError, ValueError):
            return Response(
                {"detail": "Invalid price; must be a number."},
                status=status.HTTP_400_BAD_REQUEST
            )

        return self.list(request, *args, **kwargs)
    
class ProductsPageView(TemplateView):
    template_name = "products.html"
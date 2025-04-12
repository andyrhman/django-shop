from functools import partial
from rest_framework import exceptions, generics, mixins, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from django.db.models import Q
from authorization.authentication import JWTAuthentication
from cart.serializers import CartAdminSerializer, CartCreateSerializer, CartQuantityUpdateSerializer, CartSerializer
from core.models import Cart, User

class CartAdminListAPIView(generics.ListAPIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = Cart.objects.all()
    serializer_class = CartAdminSerializer
    
    def get_queryset(self):
        queryset = super().get_queryset().select_related('user')
        
        search = self.request.query_params.get("search", "").strip()
        if search:
            queryset = queryset.filter(
                Q(user__fullName__icontains=search) | 
                Q(user__email__icontains=search) |
                Q(user__username__icontains=search)
            )
            
        sort_by_completed = self.request.query_params.get("sortByCompleted", "").strip().lower()
        sort_by_date = self.request.query_params.get("sortByDate", "").strip().lower()
        
        if sort_by_completed:
            if sort_by_completed == "asc":
                # Ascending order: by default, False < True.
                queryset = queryset.order_by("completed")
            else:
                queryset = queryset.order_by("-completed")
        elif sort_by_date:
            if sort_by_date == "newest":
                queryset = queryset.order_by("-created_at")
            else:
                queryset = queryset.order_by("created_at")
        else:
            queryset = queryset.order_by("-created_at")
        
        return queryset
    
    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.serializer_class(queryset, many=True)
        return Response(serializer.data)

class CartsAdminRetriveAPIView(
    generics.RetrieveAPIView
):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = Cart.objects.all()
    serializer_class = CartAdminSerializer
    lookup_field = 'id'
    
    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)
    
class CartCRUDAPIView(
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.DestroyModelMixin,
    generics.GenericAPIView
):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = Cart.objects.all()
    lookup_field = 'id'
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return CartCreateSerializer
        elif self.request.method in ('PUT', 'PATCH'):
            return CartQuantityUpdateSerializer
        return CartSerializer
    
    def post(self, request):
        return self.create(request)
    
    def get(self, request):
        user = request.user
        
        get_user = Cart.objects.filter(user=user)
        
        serializer = self.get_serializer(get_user, many=True)
        
        return Response(serializer.data)
    
    def put(self, request, id):
        user = request.user
        
        check_cart = Cart.objects.filter(id=id, user=user).first()
        
        if not check_cart:
            return Response({"message": "Not Allowed"}, status=status.HTTP_403_FORBIDDEN)
        
        serializer = self.get_serializer(check_cart, data=request.data, context={'request': request}, partial=True)
        
        serializer.is_valid(raise_exception=True)
        
        updated_data = serializer.save()
        
        response = CartQuantityUpdateSerializer(updated_data)
        
        return Response(response.data)
    
    def delete(self, request, id):
        user = request.user
        
        cart = Cart.objects.filter(id=id, user=user).first()
        
        if not cart:
            return Response({"message": "Not Allowed"}, status=status.HTTP_403_FORBIDDEN)
        
        response = super().destroy(request)
        response.status = status.HTTP_204_NO_CONTENT
        
        return response
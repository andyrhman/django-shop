from django.db.models import Q
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from authorization.authentication import JWTAuthentication
from core.models import Review
from review.serializers import CreateReviewSerializer, ReviewSerializer

class UserReviewAPIView(generics.CreateAPIView, generics.ListAPIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = Review.objects.all()
    lookup_field = 'id'

    def get_serializer_class(self):
        if self.request.method == "POST":
            return CreateReviewSerializer
        return ReviewSerializer
    
    def get_queryset(self):
        return Review.objects.filter(user=self.request.user)
    
class AdminReviewAPIView(generics.ListAPIView, generics.RetrieveAPIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    lookup_field = 'id'
    
    def get_queryset(self):
        
        queryset = super().get_queryset().select_related('product')
        
        search = self.request.query_params.get("search", "").strip()
        if search:
            queryset = queryset.filter(
                Q(product__title=search) | 
                Q(product__description=search)
            )
            
        return queryset
    
    def get(self, request, *args, **kwargs):
        if 'id' in kwargs:
            return self.retrieve(request, *args, **kwargs)
        
        queryset = self.get_queryset()
        serializer = self.serializer_class(queryset, many=True)
        return Response(serializer.data)
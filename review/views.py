from django.shortcuts import render
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from authorization.authentication import JWTAuthentication
from core.models import Review
from review.serializers import CreateReviewSerializer, ReviewSerializer

# Create your views here.
class UserReviewAPIView(generics.CreateAPIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = Review.objects.all()
    lookup_field = 'id'
    serializer_class = CreateReviewSerializer
    
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        saved = serializer.save()
        
        return Response(ReviewSerializer(saved).data, status=status.HTTP_201_CREATED)
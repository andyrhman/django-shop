from django.shortcuts import render
from rest_framework import generics, mixins, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from authorization.authentication import JWTAuthentication
from category.serializers import CategorySerializer
from core.models import Category

# Create your views here.
class CategoriesAPIView(APIView):
    def get(self, _):
        categories = Category.objects.all()
        
        serializer = CategorySerializer(categories, many=True)
        
        return Response(serializer.data)
    
class CategoryGenericAPIView(
    generics.GenericAPIView, mixins.CreateModelMixin, mixins.UpdateModelMixin, 
    mixins.ListModelMixin, mixins.RetrieveModelMixin, mixins.DestroyModelMixin
):
    authentication_classes= [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = CategorySerializer
    queryset = Category.objects.all()
    lookup_field = 'id'
    
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)
        
    def get(self, request, *args, **kwargs):
        if 'id' in kwargs:
            return self.retrieve(request, *args, **kwargs)
        
        return self.list(request, *args, **kwargs)
        
    def put(self, request, *args, **kwargs):
        response = super().partial_update(request, *args, **kwargs)
        response.status_code = status.HTTP_202_ACCEPTED
        return response
        
    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)
    
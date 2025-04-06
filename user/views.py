from django.shortcuts import render
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework.views import APIView

from authorization.authentication import JWTAuthentication
from core.models import User
from user.serializers import UserSerializer

# Create your views here.
class UsersAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        users = User.objects.all()
        
        s = request.query_params.get("search", "")
        if s:
            users = list(
                [
                    u
                    for u in users
                    if (s.lower() in u.fullName.lower())
                    or (s.lower() in u.username.lower())
                ]
            )
            
        serializer = UserSerializer(users, many=True)
        
        return Response(serializer.data)
    
class TotalUsersAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        users = User.objects.all()
        
        total = len(users)
        
        return Response({"total": total})
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import exceptions, status
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework.views import APIView

from authorization.authentication import JWTAuthentication
from authorization.serializers import UserSerializer
from core.models import User

# Create your views here.
class RegisterAPIView(APIView):
    def post(self, request):
        data = request.data

        if data["password"] != data["confirm_password"]:
            raise exceptions.APIException("Password do not match!")

        serializer = UserSerializer(data=data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response({'message': "Successfully Registered"})

class LoginAPIView(APIView):
    def post(self, request):
        data = request.data
        
        if "email" in data:
            try:
                user = User.objects.get(email=data["email"].lower())
            except ObjectDoesNotExist:
                return Response(
                    {"message": "Invalid email!"}, status=status.HTTP_400_BAD_REQUEST
                )
        elif "username" in data:
            try:
                user = User.objects.get(username=data["username"].lower())
            except ObjectDoesNotExist:
                return Response(
                    {"message": "Invalid username!"}, status=status.HTTP_400_BAD_REQUEST
                )

        if not user.check_password(data["password"]):
            return Response(
                {"message": "Invalid password"}, status=status.HTTP_400_BAD_REQUEST
            )

        scope = 'user' if 'api/user' in request.path else 'admin'

        if user.is_user and scope == 'admin':
            raise exceptions.AuthenticationFailed('Unauthorized')

        token = JWTAuthentication.generate_jwt(user.id, scope)
        response = Response()
        response.set_cookie(key="user_session", value=token, httponly=True)
        response.data = {"message": "Successfully logged in!"}

        return response    

class UserAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        user = request.user
        
        serializer = UserSerializer(user)
        
        # if 'api/admin' in request.path:
        #     return Response(serializer.data)
        
        return Response(serializer.data)
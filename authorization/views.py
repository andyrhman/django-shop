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
        
        return Response(serializer.data)
    
class LogoutAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    
    def post(self, _):
        response = Response()
        response.delete_cookie(key="user_session")
        response.data = {"message": "Success"}
        return response
    
class UpdateInfoAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    
    def put(self, request, pk=None):
        try:
            data = request.data
            user = request.user 
            serializer = UserSerializer(user, data=data, context={"request": request}, partial=True) # ! is_user request needs to be removed
            
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)
        except exceptions.ValidationError as e:
            if isinstance(e.detail, dict):
                errors = {key: value[0] for key, value in e.detail.items()}
                first_field = next(iter(errors))
                field_name = first_field.replace("_", " ").capitalize()
                if "already exists" in errors[first_field]:
                    message = f"{field_name} already exists."
                else:
                    message = f"{field_name} error: {errors[first_field]}"
            else:
                message = str(e.detail)
            return Response({"message": message}, status=status.HTTP_400_BAD_REQUEST)           
            

class UpdatePasswordAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    
    def put(self, request, pk=None):
        data = request.data
        user = request.user
    
        user.set_password(data['password']) 
        user.save()
        
        return Response(status=status.HTTP_204_NO_CONTENT)
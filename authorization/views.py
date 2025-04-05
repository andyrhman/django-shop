from datetime import timedelta, timezone
import datetime
import random
import secrets
import string
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.core.mail import send_mail
from django.template.loader import render_to_string
from rest_framework import exceptions, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from authorization.authentication import JWTAuthentication
from authorization.serializers import UserSerializer
from core.models import Token, User
from decouple import config
from google.oauth2 import id_token
from google.auth.transport.urllib3 import Request as GoogleRequest
from authorization.signals import user_registered

# Create your views here.
class RegisterAPIView(APIView):
    def post(self, request):
        data = request.data

        if data["password"] != data["confirm_password"]:
            raise exceptions.APIException("Password do not match!")

        serializer = UserSerializer(data=data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        user = serializer.save() # * Declaring user variable for email send listener

        # Emit only for registration
        user_registered.send(sender=self.__class__, user=user)

        return Response({"message": "Successfully Registered"})


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

        scope = "user" if "api/user" in request.path else "admin"

        if user.is_user and scope == "admin":
            raise exceptions.AuthenticationFailed("Unauthorized")

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
            serializer = UserSerializer(
                user,
                data={
                    "fullName": data.get("fullName", user.fullName),
                    "email": data.get("email", user.email),
                    "username": data.get("username", user.username),
                },
                context={"request": request},
                partial=True,
            )

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
        
        if data['password'] != data['confirm_password']:
            raise exceptions.APIException('Password do not match')

        user.set_password(data["password"])
        user.save()

        return Response(status=status.HTTP_204_NO_CONTENT)
            
class ResendVerifyAPIView(APIView):
    def post(self, request):
        data = request.data
        
        if not data['email']:
            raise exceptions.APIException("Provide your email address")

        user = User.objects.filter(email=data['email']).first()
        
        if not user:
            raise exceptions.APIException("Email not found")
        
        if user.is_verified:
            raise exceptions.APIException("Your account has already been verified")
        
        token_str = secrets.token_hex(16)
        expiresAt = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(minutes=1)

        Token.objects.create(
            token=token_str,
            email=user.email,
            user=user,
            expiresAt=expiresAt ,
            used=False,
        )

        #Build verification URL
        origin = config('ORIGIN_2')
        verify_url = f"{origin}/verify/{token_str}"

        # Render email HTML from a template (e.g. templates/auth.html)
        html_content = render_to_string(
            "email_template.html",
            {
                "name": user.fullName,
                "url": verify_url,
            },
        )

        send_mail(
            subject="Verify your email",
            message="",  # no plain-text body
            from_email="service@mail.com",
            recipient_list=[user.email],
            html_message=html_content,
            fail_silently=False,
        )

        return Response(
            {"message": "Email has been sent successfully"},
            status=status.HTTP_200_OK,
        ) 


class VerifyAccountAPIView(APIView):
   
    def put(self, _, token=''):
        user_token = Token.objects.filter(token=token).first()
        
        if not user_token or user_token.expiresAt < datetime.datetime.now(datetime.timezone.utc) :
            return Response({'message': 'Token is invalid or expired'}, status=status.HTTP_400_BAD_REQUEST)
        
        if not user_token:
            return Response({'message': 'Invalid verify ID'}, status=status.HTTP_400_BAD_REQUEST)
        
        if user_token.used:
            return Response({'message': 'Verify ID has already been used'}, status=status.HTTP_400_BAD_REQUEST)
        
        user = User.objects.filter(email=user_token.email, pk=user_token.user.id).first()
        
        if not user:
            return Response({'message': 'User not found'}, status=status.HTTP_400_BAD_REQUEST)
        elif user.is_verified:
            return Response({'message': 'Your account has already been verified'}, status=status.HTTP_400_BAD_REQUEST)
        elif user.email != user_token.email and user.id != user_token.user:
            return Response({'message': 'Invalid Verify ID or email'}, status=status.HTTP_400_BAD_REQUEST)
        
        user_token.used = True
        user_token.save()
        user.is_verified = True
        user.save()
        
        return Response({"message": "Account Verified Successfully"}, status=status.HTTP_202_ACCEPTED)

class GoogleAuthAPIView(APIView):
    def post(self, request):
        token = request.data.get("token")
        remember_me = request.data.get("rememberMe", False)

        if not token:
            return Response(
                {"message": "Token is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # 1) Verify the Google ID token
        try:
            idinfo = id_token.verify_oauth2_token(
                token,
                GoogleRequest(),
                config("GOOGLE_CLIENT_ID"),
            )
        except ValueError:
            return Response(
                {"message": "Unauthorized"},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        email = idinfo.get("email")
        if not email:
            return Response(
                {"message": "Unauthorized"},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        # 2) Find or create the user
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            # generate random credentials
            random_username = f"user{random.randint(1000, 9999)}"
            random_password = "".join(
                secrets.choice(string.ascii_letters + string.digits) for _ in range(10)
            )
            user = User(
                fullName=random_username,
                username=random_username,
                email=email,
            )
            user.set_password(random_password)
            user.save()

        # 3) Issue JWT
        scope = "user"  # or detect from path if you need admin vs user
        jwt_token = JWTAuthentication.generate_jwt(user.id, scope)

        # 4) Set cookie with correct expiration
        max_age = 365 * 24 * 60 * 60 if remember_me else 7 * 24 * 60 * 60
        expires = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(seconds=max_age)

        response = Response(
            {"message": "Successfully logged in"},
            status=status.HTTP_200_OK,
        )
        response.set_cookie(
            key="user_session",
            value=jwt_token,
            httponly=True,
            expires=expires,
            secure=not settings.DEBUG,  # optional: only send over HTTPS in prod
            samesite="Lax",
        )
        return response

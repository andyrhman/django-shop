import datetime
import random
import secrets
import string
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.views.generic import TemplateView
import requests
from rest_framework import exceptions, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from authorization.authentication import JWTAuthentication
from authorization.serializers import UserSerializer
from authorization.services import UserService
from core.models import Token, User
from decouple import config
from google.oauth2 import id_token
from google.auth.transport.urllib3 import Request as GoogleRequest
from django.views.generic import TemplateView

# Create your views here.
def _detect_scope_from_path(path: str) -> str:
    """
    Return 'admin' if the monolith request path starts with /api/admin/,
    else 'user'.
    """
    return 'admin' if path.lower().startswith('/api/admin/') else 'user'

class RegisterAPIView(APIView):
    def post(self, request):
        data = request.data
        remote = UserService.post(
            'user/register/',
            json=data,
            timeout=5
        )

        try:
            payload = remote.json()
        except ValueError:
            return Response(
                {"message": "Invalid response from user service"},
                status=status.HTTP_502_BAD_GATEWAY
            )

        return Response(payload, status=remote.status_code)


class LoginAPIView(APIView):
    def post(self, request):
        scope = _detect_scope_from_path(request.path)

        data = request.data.copy()
        data['scope'] = scope

        remote = UserService.post(
            f'{scope}/login',
            json=data,
            timeout=5
        )

        try:
            payload = remote.json()
        except ValueError:
            return Response({"message": "Invalid response from auth service"}, status=status.HTTP_502_BAD_GATEWAY)

        if not remote.ok:
            return Response(payload, status=remote.status_code)

        token = payload.get('jwt')
        if token is None:
            return Response({"message": "Auth service did not return a token"}, status=status.HTTP_502_BAD_GATEWAY)

        response = Response({"message": "Successfully logged in!"}, status=status.HTTP_200_OK)
        
        response.set_cookie(
            key="user_session",
            value=token,
            httponly=True,
        )
        
        return response


class UserAPIView(APIView):
    def get(self, request):
        scope = _detect_scope_from_path(request.path)
        token = request.COOKIES.get('user_session')
        if not token:
            return Response({"message": "Unauthenticated"}, status=status.HTTP_401_UNAUTHORIZED)

        resp = UserService.get(
            f'{scope}',
            cookies={'user_session': token},
            timeout=5
        )

        try:
            payload = resp.json()
        except ValueError:
            return Response(
                {"message": "Invalid response from auth service"},
                status=502
            )

        if not resp.ok:
            return Response(payload, status=resp.status_code)

        return Response(payload, status=resp.status_code)

class LogoutAPIView(APIView):
    def post(self, request):
        scope = _detect_scope_from_path(request.path)
        token = request.COOKIES.get('user_session')
        if not token:
            return Response({'message': 'No session'}, status=status.HTTP_401_UNAUTHORIZED)

        remote = UserService.post(
            f'{scope}/logout',
            cookies={'user_session': token},
            timeout=5
        )

        try:
            payload = remote.json()
        except ValueError:
            return Response({'message': 'Bad response from auth service'}, status=status.HTTP_502_BAD_GATEWAY)

        if not remote.ok:
            return Response(payload, status=remote.status_code)

        resp = Response({'message': 'Successfully logged out'}, status=status.HTTP_200_OK)
        resp.delete_cookie('user_session')
        return resp

class UpdateInfoAPIView(APIView):
    def put(self, request, pk=None):
        scope = _detect_scope_from_path(request.path)
        token = request.COOKIES.get('user_session')
        if not token:
            return Response({"message": "Unauthenticated"}, status=status.HTTP_401_UNAUTHORIZED)

        payload = {
            k: v for k, v in {
                "fullName": request.data.get("fullName"),
                "email":    request.data.get("email"),
                "username": request.data.get("username"),
            }.items() if v is not None
        }

        remote = UserService.put(
            f'{scope}/info',
            json=payload,
            cookies={'user_session': token},
            timeout=5
        )

        try:
            data = remote.json()
        except ValueError:
            return Response(
                {"message": "Invalid response from user service"},
                status=status.HTTP_502_BAD_GATEWAY
            )

        if not remote.ok:
            return Response(data, status=remote.status_code)

        return Response(data, status=status.HTTP_200_OK)


class UpdatePasswordAPIView(APIView):
    def put(self, request, pk=None):
        scope = _detect_scope_from_path(request.path)
        token = request.COOKIES.get('user_session')
        if not token:
            return Response({"message": "Unauthenticated"}, status=status.HTTP_401_UNAUTHORIZED)

        pwd = request.data.get('password')
        cpwd = request.data.get('confirm_password')
        if pwd != cpwd:
            return Response(
                {"message": "Password do not match"},
                status=status.HTTP_400_BAD_REQUEST
            )

        remote = UserService.put(
            f'{scope}/password',
            json={'password': pwd, 'confirm_password': cpwd},
            cookies={'user_session': token},
            timeout=5
        )

        # Try to parse JSON, but if there's no body just set payload to None
        payload = None
        if remote.text:
            try:
                payload = remote.json()
            except ValueError:
                return Response(
                    {"message": "Invalid response from user service"},
                    status=status.HTTP_502_BAD_GATEWAY
                )

        if not remote.ok:
            return Response(payload or {"message": "Error from user service"},
                            status=remote.status_code)

        return Response(status=remote.status_code)
            
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

        origin = config('ORIGIN')
        verify_url = f"{origin}/verify/{token_str}"

        html_content = render_to_string(
            "email_template.html",
            {
                "name": user.fullName,
                "url": verify_url,
            },
        )

        send_mail(
            subject="Verify your email",
            message="",
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
    def put(self, request, token: str):
        remote = UserService.put(
            f'verify/{token}/',
            timeout=5
        )

        try:
            payload = remote.json()
        except ValueError:
            return Response(
                {"message": "Invalid response from user service"},
                status=status.HTTP_502_BAD_GATEWAY
            )

        if not remote.ok:
            return Response(payload, status=remote.status_code)

        return Response(payload, status=remote.status_code)

class RegisterPageView(TemplateView):
    template_name = "auth/register.html"

class LoginPageView(TemplateView):
    template_name = "auth/login.html"

class VerifyPageView(TemplateView):
    template_name = "auth/verify.html"
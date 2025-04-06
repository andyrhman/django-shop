import jwt, datetime
from decouple import config
from rest_framework import exceptions
from rest_framework.authentication import BaseAuthentication

from core.models import User

class JWTAuthentication(BaseAuthentication):
    def authenticate(self, request):
        token = request.COOKIES.get('user_session')
        if not token:
            return None

        try:
            payload = jwt.decode(token, config('JWT_SECRET'), algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            raise exceptions.AuthenticationFailed('Unauthenticated')

        path = request.path.lower()
        # 1) admin-only
        if path.startswith('/api/admin/'):
            if payload['scope'] != 'admin':
                raise exceptions.AuthenticationFailed('Invalid Scope!')
        # 2) user-only
        elif path.startswith('/api/user/'):
            if payload['scope'] != 'user':
                raise exceptions.AuthenticationFailed('Invalid Scope!')
        # 3) “generic” api: allow either
        elif path.startswith('/api/'):
            if payload['scope'] not in ('user', 'admin'):
                raise exceptions.AuthenticationFailed('Invalid Scope!')
        else:
            # not an API route we care about
            return None

        user = User.objects.get(id=payload['user_id'])
        return (user, None)
    
    @staticmethod
    def generate_jwt(id, scope):
        payload = {
            'user_id': str(id), 
            'scope': scope,
            'exp': datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=1),
            'iat': datetime.datetime.now(datetime.timezone.utc)
        }
        
        return jwt.encode(payload, config('JWT_SECRET'), algorithm='HS256')
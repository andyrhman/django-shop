import jwt, datetime
from decouple import config
from rest_framework import exceptions
from rest_framework.authentication import BaseAuthentication

from core.models import User

class JWTAuthentication(BaseAuthentication):
    def authenticate(self, request):
        is_user = 'api/user' in request.path 

        token = request.COOKIES.get('user_session')
        
        if not token:
            return None
        
        try:
            payload = jwt.decode(token, config('JWT_SECRET'), algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            raise exceptions.AuthenticationFailed('Unauthenticated')

        if (is_user and payload['scope'] != 'user') or (not is_user and payload['scope'] != 'admin'):
            raise exceptions.AuthenticationFailed('Invalid Scope!')

        user = User.objects.get(id=payload['user_id'])
        
        if user is None:
            raise exceptions.AuthenticationFailed('Unauthenticated')
         
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
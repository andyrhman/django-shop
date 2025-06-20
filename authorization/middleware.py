import logging
from django.utils.deprecation import MiddlewareMixin
from .services import UserService

logger = logging.getLogger(__name__)

def _detect_scope_from_path(path: str) -> str:
    return 'admin' if path.lower().startswith('/api/admin/') else 'user'

class UserMicroserviceAuthMiddleware(MiddlewareMixin):

    def process_request(self, request):
        request.user_ms = None

        scope = _detect_scope_from_path(request.path)

        token = request.COOKIES.get('user_session')
        if not token:
            return

        try:
            request.user_ms = UserService.get(
                scope,
                cookies={'user_session': token},
                timeout=5
            )
        except Exception as exc:
            logger.warning(
                "UserMicroserviceAuthMiddleware: failed to fetch user_ms for scope=%s token=%s: %s",
                scope, token, exc,
                exc_info=True,
            )
            request.user_ms = None

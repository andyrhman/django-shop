from django.apps import AppConfig


class AuthConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'authorization'

    def ready(self):
        # import your signal handlers
        import authorization.signals
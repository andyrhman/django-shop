import datetime
import json
import secrets
from django.conf import settings
from django.forms import model_to_dict
from django.utils import timezone
from django.template.loader import render_to_string
from django.core.mail import send_mail
from django.dispatch import Signal, receiver
from decouple import config
from app.producer import send_message
from core.models import Token

user_registered = Signal()

@receiver(user_registered)
def send_verification_email(sender, user, **kwargs):
    token_str = secrets.token_hex(16)
    expires_at = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(minutes=1)

    Token.objects.create(
        token=token_str,
        email=user.email,
        user=user,
        expiresAt=expires_at,
        used=False,
    )

    origin = config('ORIGIN')
    verify_url = f"{origin}/verify/{token_str}"

    payload = {
        "event": "user_registered",
        "user": model_to_dict(user),
        "verify_url": verify_url,
    }
    send_message.send(config('KAFKA_TOPIC', default='default'), payload)


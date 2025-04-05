import datetime
import secrets
from django.conf import settings
from django.utils import timezone
from django.template.loader import render_to_string
from django.core.mail import send_mail
from django.dispatch import Signal, receiver
from decouple import config
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

    origin = config('ORIGIN_2')
    verify_url = f"{origin}/verify/{token_str}"

    html_content = render_to_string(
        "email_template.html",
        {"name": user.fullName, "url": verify_url},
    )

    send_mail(
        subject="Verify your email",
        message="",
        from_email="service@mail.com",
        recipient_list=[user.email],
        html_message=html_content,
    )

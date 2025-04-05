import secrets
from datetime import timedelta

from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from django.template.loader import render_to_string
from django.core.mail import send_mail

from decouple import config
from core.models import User, Token  # adjust import path


@receiver(post_save, sender=User)
def send_verification_email(sender, instance, created, **kwargs):
    """
    After a new User is saved, generate a verification token
    and send the HTML email.
    """
    if not created:
        return  # only on new registrations

    # 1) Create the token
    token_str = secrets.token_hex(16)
    expires_at = timezone.now() + timedelta(minutes=1)

    Token.objects.create(
        token=token_str,
        email=instance.email,
        user=instance,
        expires_at=expires_at,
        used=False,
    )

    # 2) Build the verify URL
    origin = config('ORIGIN_2')
    verify_url = f"{origin}/verify/{token_str}"

    # 3) Render the HTML email template
    html_content = render_to_string(
        "auth_email_template.html",  # the inline‐style template you created
        {"name": instance.fullName, "url": verify_url},
    )

    # 4) Send the email
    send_mail(
        subject="Verify your email",
        message="",  # no plain‐text fallback
        from_email="service@mail.com",
        recipient_list=[instance.email],
        html_message=html_content,
        fail_silently=False,
    )

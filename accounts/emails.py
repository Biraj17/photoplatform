import logging

from django.conf import settings
from django.core.mail import send_mail

logger = logging.getLogger(__name__)


def send_signup_otp_email(email, full_name, code):
    """Send the signup verification code. Returns True when the email left
    the backend without raising, False otherwise so the caller can tell the
    user the address didn't work."""
    subject = "Your PhotoPlat verification code"
    body = (
        f"Hi {full_name},\n\n"
        f"Your PhotoPlat verification code is: {code}\n\n"
        "Enter this code on the verification page to finish creating your "
        "photographer account. The code expires in 10 minutes.\n\n"
        "If you didn't request this, you can safely ignore this email.\n\n"
        "— PhotoPlat"
    )
    try:
        send_mail(subject, body, settings.DEFAULT_FROM_EMAIL, [email], fail_silently=False)
        return True
    except Exception:
        logger.exception("Failed to send signup OTP email to %s", email)
        return False

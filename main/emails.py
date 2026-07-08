import logging

from django.conf import settings
from django.core.mail import send_mail

logger = logging.getLogger(__name__)


def send_booking_decision_email(booking, accepted):
    photographer = booking.photographer
    contact = photographer.contact_email or photographer.user.email

    if accepted:
        subject = f"Your booking request with {photographer.full_name} was accepted"
        body = (
            f"Hi {booking.client_name},\n\n"
            f"Good news — {photographer.full_name} has accepted your booking request "
            f"for {booking.shoot_date} ({booking.package}).\n\n"
            f"They'll be in touch directly to confirm the details. You can also reach "
            f"them at {contact}"
            + (f" or {photographer.phone}" if photographer.phone else "")
            + ".\n\n"
            "— PhotoPlat"
        )
    else:
        subject = f"Update on your booking request with {photographer.full_name}"
        body = (
            f"Hi {booking.client_name},\n\n"
            f"{photographer.full_name} isn't able to take your booking request for "
            f"{booking.shoot_date}. Feel free to browse other photographers on PhotoPlat "
            f"and send a new request.\n\n"
            "— PhotoPlat"
        )

    try:
        send_mail(
            subject,
            body,
            settings.DEFAULT_FROM_EMAIL,
            [booking.client_email],
            fail_silently=False,
        )
    except Exception:
        logger.exception(
            "Failed to send booking %s email to %s for booking id=%s",
            "acceptance" if accepted else "rejection",
            booking.client_email,
            booking.pk,
        )

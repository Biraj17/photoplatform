import logging

from django.conf import settings
from django.core.mail import send_mail

logger = logging.getLogger(__name__)


def send_new_booking_email(booking):
    """Notify the photographer that a new booking request just arrived."""
    photographer = booking.photographer
    to_email = photographer.contact_email or photographer.user.email

    subject = f"New booking request from {booking.client_name}"
    body = (
        f"Hi {photographer.full_name},\n\n"
        f"You have a new booking request on PhotoPlat:\n\n"
        f"  Client:  {booking.client_name}\n"
        f"  Email:   {booking.client_email}\n"
        f"  Phone:   {booking.client_phone}\n"
        f"  Date:    {booking.shoot_date}\n"
        f"  Package: {booking.package}\n\n"
        f"Message from the client:\n{booking.message}\n\n"
        "Log in to your PhotoPlat dashboard to accept or decline this request. "
        "The client will be notified by email as soon as you decide.\n\n"
        "— PhotoPlat"
    )

    try:
        send_mail(subject, body, settings.DEFAULT_FROM_EMAIL, [to_email], fail_silently=False)
    except Exception:
        logger.exception(
            "Failed to send new-booking email to %s for booking id=%s",
            to_email,
            booking.pk,
        )


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

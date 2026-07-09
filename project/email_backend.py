"""Email backend that delivers through Brevo's HTTPS API.

Render's free tier blocks outbound SMTP ports (25/465/587), so classic
SMTP delivery hangs and emails never leave the server. Brevo's REST API
runs over HTTPS port 443, which is never blocked. Activated by setting
the BREVO_API_KEY environment variable.
"""
import json
import logging
from email.utils import parseaddr
from urllib import error, request

from django.conf import settings
from django.core.mail.backends.base import BaseEmailBackend

logger = logging.getLogger(__name__)

BREVO_API_URL = "https://api.brevo.com/v3/smtp/email"


class BrevoEmailBackend(BaseEmailBackend):
    def send_messages(self, email_messages):
        sent = 0
        for message in email_messages:
            try:
                self._send(message)
                sent += 1
            except Exception:
                logger.exception("Brevo send failed for email to %s", message.to)
                if not self.fail_silently:
                    raise
        return sent

    def _send(self, message):
        from_name, from_email = parseaddr(message.from_email)
        sender = {"email": from_email}
        if from_name:
            sender["name"] = from_name

        payload = {
            "sender": sender,
            "to": [{"email": addr} for addr in message.to],
            "subject": message.subject,
            "textContent": message.body,
        }

        req = request.Request(
            BREVO_API_URL,
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "api-key": settings.BREVO_API_KEY,
                "content-type": "application/json",
                "accept": "application/json",
            },
            method="POST",
        )
        try:
            with request.urlopen(req, timeout=15) as response:
                response.read()
        except error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")[:500]
            logger.error("Brevo API rejected email to %s: HTTP %s — %s", message.to, exc.code, detail)
            raise

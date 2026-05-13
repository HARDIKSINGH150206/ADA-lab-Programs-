"""SMS helpers for OTP delivery."""
from __future__ import annotations

import logging

from app.config import settings

logger = logging.getLogger(__name__)


def _has_twilio_credentials() -> bool:
    return bool(
        settings.TWILIO_ACCOUNT_SID
        and settings.TWILIO_AUTH_TOKEN
        and settings.TWILIO_FROM_NUMBER
    )


def send_otp_sms(phone_number: str, otp: str) -> bool:
    """Send an OTP SMS when Twilio credentials are configured."""
    if not _has_twilio_credentials():
        logger.info("Twilio credentials missing; skipping SMS send for %s", phone_number)
        return False

    try:
        from twilio.rest import Client

        client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
        message = client.messages.create(
            body=f"Your Hear My Case OTP is {otp}. It expires in {settings.OTP_EXPIRY_MINUTES} minutes.",
            from_=settings.TWILIO_FROM_NUMBER,
            to=phone_number,
        )
        logger.info("OTP SMS sent for %s via Twilio message %s", phone_number, message.sid)
        return True
    except Exception as exc:
        logger.error("Failed to send OTP SMS to %s: %s", phone_number, exc)
        return False

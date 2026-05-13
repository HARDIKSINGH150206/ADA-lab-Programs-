"""Tests for SMS helper behavior."""
from app.services.sms import send_otp_sms


def test_send_otp_sms_returns_false_without_credentials(monkeypatch):
    monkeypatch.setattr("app.services.sms.settings.TWILIO_ACCOUNT_SID", "")
    monkeypatch.setattr("app.services.sms.settings.TWILIO_AUTH_TOKEN", "")
    monkeypatch.setattr("app.services.sms.settings.TWILIO_FROM_NUMBER", "")

    assert send_otp_sms("+919876543210", "123456") is False


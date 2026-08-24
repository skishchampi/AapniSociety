"""Development OTP issuance and verification.

No SMS gateway: in dev the code is logged and (when OTP_RETURN_CODE_IN_RESPONSE)
returned in the API response. Codes are stored only as salted hashes.
"""
import logging
import secrets
from datetime import timedelta

from django.conf import settings
from django.contrib.auth.hashers import check_password, make_password
from django.db import transaction
from django.utils import timezone

from .models import OTPChallenge

logger = logging.getLogger("apps.accounts.otp")

CODE_LENGTH = 6


class OTPError(Exception):
    pass


def generate_code() -> str:
    return f"{secrets.randbelow(10**CODE_LENGTH):0{CODE_LENGTH}d}"


def issue_otp(phone: str, purpose: str = OTPChallenge.Purpose.LOGIN) -> tuple[OTPChallenge, str]:
    """Create a fresh challenge for ``phone``, invalidating any prior open ones.

    Issuance is capped per phone per window so the per-challenge attempt cap cannot
    be reset at will by re-requesting (brute-force backstop, SRS §6.2).
    """
    window_start = timezone.now() - timedelta(seconds=settings.OTP_ISSUE_WINDOW_SECONDS)
    recent = OTPChallenge.objects.filter(phone=phone, created_at__gte=window_start).count()
    if recent >= settings.OTP_MAX_ISSUES_PER_WINDOW:
        raise OTPError("Too many code requests for this number. Try again later.")

    code = generate_code()
    with transaction.atomic():
        OTPChallenge.objects.filter(phone=phone, consumed_at__isnull=True).update(
            consumed_at=timezone.now()
        )
        challenge = OTPChallenge.objects.create(
            phone=phone,
            code_hash=make_password(code),
            purpose=purpose,
            expires_at=timezone.now() + timedelta(seconds=settings.OTP_TTL_SECONDS),
        )
    if settings.DEBUG:
        logger.info("OTP issued phone=%s purpose=%s code=%s (dev only)", phone, purpose, code)
    else:
        logger.info("OTP issued phone=%s purpose=%s", phone, purpose)
    return challenge, code


def verify_otp(phone: str, code: str) -> OTPChallenge:
    """Return the consumed challenge on success; raise OTPError otherwise."""
    challenge = (
        OTPChallenge.objects.filter(phone=phone, consumed_at__isnull=True)
        .order_by("-created_at")
        .first()
    )
    if challenge is None:
        raise OTPError("No active code. Request a new one.")
    if challenge.is_expired:
        raise OTPError("Code expired. Request a new one.")
    if challenge.attempts >= settings.OTP_MAX_ATTEMPTS:
        raise OTPError("Too many attempts. Request a new one.")

    challenge.attempts += 1
    if not check_password(code, challenge.code_hash):
        challenge.save(update_fields=["attempts"])
        raise OTPError("Incorrect code.")

    challenge.consumed_at = timezone.now()
    challenge.save(update_fields=["attempts", "consumed_at"])
    return challenge

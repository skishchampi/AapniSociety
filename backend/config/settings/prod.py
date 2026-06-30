"""Production settings. Placeholder hardened defaults — real SMS/secret wiring lands later."""
from django.core.exceptions import ImproperlyConfigured

from .base import *  # noqa: F403,F401
from .base import INSECURE_DEV_SECRET_KEY, SECRET_KEY, SIMPLE_JWT

DEBUG = False

# Tokens are forgeable if prod signs with the dev placeholder or a short key.
# Fail fast at boot rather than ship a guessable HS256 key (RFC 7518 §3.2).
if SECRET_KEY == INSECURE_DEV_SECRET_KEY or len(SECRET_KEY.encode()) < 32:
    raise ImproperlyConfigured(
        "SECRET_KEY must be set to a unique value of at least 32 bytes in production."
    )
SIMPLE_JWT = {**SIMPLE_JWT, "SIGNING_KEY": SECRET_KEY}

# OTP codes are never returned in API responses in production.
OTP_RETURN_CODE_IN_RESPONSE = False

SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

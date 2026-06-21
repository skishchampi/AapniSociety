"""Production settings. Placeholder hardened defaults — real SMS/secret wiring lands later."""
from .base import *  # noqa: F403,F401

DEBUG = False

# OTP codes are never returned in API responses in production.
OTP_RETURN_CODE_IN_RESPONSE = False

SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

"""Development settings."""
from .base import *  # noqa: F403,F401

DEBUG = True
ALLOWED_HOSTS = ["*"]

# In dev, the OTP code is returned in the API response and logged, so no SMS
# gateway is needed. NEVER enable this in production.
OTP_RETURN_CODE_IN_RESPONSE = True

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {"console": {"class": "logging.StreamHandler"}},
    "loggers": {
        "apps.accounts.otp": {"handlers": ["console"], "level": "INFO"},
    },
}

"""Test settings: dev behaviour, but no throttling (the suite issues many OTPs)."""
from .dev import *  # noqa: F403,F401
from .dev import REST_FRAMEWORK

REST_FRAMEWORK = {**REST_FRAMEWORK, "DEFAULT_THROTTLE_CLASSES": (), "DEFAULT_THROTTLE_RATES": {}}

PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]  # faster tests

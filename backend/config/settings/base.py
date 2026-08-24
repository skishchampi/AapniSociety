"""Base settings shared across environments.

Environment-driven via django-environ. Secrets never live in code; see .env.example.
"""
from datetime import timedelta
from pathlib import Path

import environ

# backend/config/settings/base.py -> backend/
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Dev default is >= 32 bytes so HS256 token signing never falls below the RFC 7518
# minimum. prod.py refuses to boot on this placeholder (see the guard there).
INSECURE_DEV_SECRET_KEY = "django-insecure-dev-only-key-change-me-in-prod"

env = environ.Env(
    DEBUG=(bool, False),
    SECRET_KEY=(str, INSECURE_DEV_SECRET_KEY),
    ALLOWED_HOSTS=(list, ["localhost", "127.0.0.1"]),
    CORS_ALLOWED_ORIGINS=(list, ["http://localhost:5173", "http://127.0.0.1:5173"]),
    DATABASE_URL=(str, f"sqlite:///{BASE_DIR / 'db.sqlite3'}"),
    OTP_TTL_SECONDS=(int, 300),
    OTP_MAX_ATTEMPTS=(int, 5),
    OTP_MAX_ISSUES_PER_WINDOW=(int, 5),
    OTP_ISSUE_WINDOW_SECONDS=(int, 3600),
)

# Load .env if present (local dev). In containers/CI, real env vars win.
environ.Env.read_env(BASE_DIR / ".env")

SECRET_KEY = env("SECRET_KEY")
DEBUG = env("DEBUG")
ALLOWED_HOSTS = env("ALLOWED_HOSTS")

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # third-party
    "rest_framework",
    "rest_framework_simplejwt.token_blacklist",
    "corsheaders",
    "drf_spectacular",
    # local
    "apps.accounts",
    "apps.geo",
    "apps.members",
]

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

DATABASES = {"default": env.db()}

AUTH_USER_MODEL = "accounts.User"

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
]

LANGUAGE_CODE = "en-in"
TIME_ZONE = "Asia/Kolkata"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# ── DRF ────────────────────────────────────────────────
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": ("rest_framework.permissions.IsAuthenticated",),
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "DEFAULT_THROTTLE_CLASSES": (
        "rest_framework.throttling.ScopedRateThrottle",
    ),
    "DEFAULT_THROTTLE_RATES": {
        # Issuing and verifying are throttled on separate IP buckets so verify
        # attempts cannot drain the issue budget (and vice versa). Per-phone
        # limits live in apps.accounts.otp, independent of these IP buckets.
        "otp": "10/hour",
        "otp_verify": "20/hour",
    },
}

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=15),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,
    "USER_ID_FIELD": "id",
    "USER_ID_CLAIM": "user_id",
    # HS256 over SECRET_KEY; prod.py guarantees that key is >= 32 bytes.
    "SIGNING_KEY": SECRET_KEY,
}

SPECTACULAR_SETTINGS = {
    "TITLE": "AapniSociety API",
    "DESCRIPTION": "Worker-led cooperative infrastructure — REST API",
    "VERSION": "0.1.0-alpha.1",
    "SERVE_INCLUDE_SCHEMA": False,
}

CORS_ALLOWED_ORIGINS = env("CORS_ALLOWED_ORIGINS")

# ── Auth / OTP (dev) ───────────────────────────────────
OTP_TTL_SECONDS = env("OTP_TTL_SECONDS")
OTP_MAX_ATTEMPTS = env("OTP_MAX_ATTEMPTS")
# Cap how often one phone can mint a fresh code, so the per-challenge attempt cap
# cannot be reset at will by re-requesting (brute-force backstop, SRS §6.2).
OTP_MAX_ISSUES_PER_WINDOW = env("OTP_MAX_ISSUES_PER_WINDOW")
OTP_ISSUE_WINDOW_SECONDS = env("OTP_ISSUE_WINDOW_SECONDS")

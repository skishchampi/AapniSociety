from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
from django.utils import timezone

from .managers import UserManager


class Role(models.TextChoices):
    WORKER = "worker", "Worker"
    HOUSEHOLD = "household", "Household"
    CONNECTOR = "connector", "Trusted connector"
    MODERATOR = "moderator", "Moderator"
    OPERATOR = "operator", "Cooperative operator"
    ADMIN = "admin", "System admin"


class User(AbstractBaseUser, PermissionsMixin):
    """Phone-first user. Phone is the login identity; email is optional/secondary.

    Hard privacy rule (SRS 6.1): no caste / religion / marital / relationship fields,
    ever — not here, not on any profile.
    """

    phone = models.CharField("phone (E.164)", max_length=20, unique=True)
    email = models.EmailField(unique=True, null=True, blank=True)
    full_name = models.CharField(max_length=150, blank=True)
    primary_role = models.CharField(
        max_length=20, choices=Role.choices, default=Role.HOUSEHOLD
    )

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)

    objects = UserManager()

    USERNAME_FIELD = "phone"
    REQUIRED_FIELDS = []  # phone + password prompted by createsuperuser automatically

    class Meta:
        ordering = ["-date_joined"]

    def __str__(self):
        return f"{self.full_name or self.phone} ({self.primary_role})"


class OTPChallenge(models.Model):
    """A short-lived one-time code tied to a phone number.

    The plaintext code is never stored — only a salted hash. In dev the code is
    surfaced in the response/log; in prod it would be delivered by SMS.
    """

    class Purpose(models.TextChoices):
        LOGIN = "login", "Login"
        SIGNUP = "signup", "Signup"

    phone = models.CharField(max_length=20, db_index=True)
    code_hash = models.CharField(max_length=128)
    purpose = models.CharField(
        max_length=10, choices=Purpose.choices, default=Purpose.LOGIN
    )
    attempts = models.PositiveSmallIntegerField(default=0)
    expires_at = models.DateTimeField()
    consumed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["phone", "consumed_at"])]

    @property
    def is_expired(self):
        return timezone.now() >= self.expires_at

    @property
    def is_consumed(self):
        return self.consumed_at is not None

    def __str__(self):
        return f"OTP({self.phone}, {self.purpose})"


class AuditEvent(models.Model):
    """Append-only record of sensitive actions (SRS 6.1/6.3).

    Scaffolded now; per-feature coverage is wired in later milestones. Sensitive
    payloads must be redacted before they reach `metadata`.
    """

    actor = models.ForeignKey(
        User, null=True, blank=True, on_delete=models.SET_NULL, related_name="audit_events"
    )
    action = models.CharField(max_length=100)
    target_type = models.CharField(max_length=100, blank=True)
    target_id = models.CharField(max_length=64, blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.action} by {self.actor_id or 'system'} @ {self.created_at:%Y-%m-%d %H:%M}"

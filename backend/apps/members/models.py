from django.conf import settings
from django.db import models
from django.db.models import Q

from apps.geo.models import Building, Locality, Unit


class ServiceCategory(models.Model):
    key = models.SlugField(unique=True)
    label = models.CharField(max_length=80)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name_plural = "service categories"
        ordering = ["label"]

    def __str__(self):
        return self.label


class ContactVisibility(models.TextChoices):
    PRIVATE = "private", "Private — reveal only on consent"
    COOP = "coop", "Cooperative moderators only"


class WorkerProfile(models.Model):
    """Worker-owned profile. References, rates, and safety notes are added in later
    milestones; alpha.1 holds only identity, categories, languages, and a rate floor."""

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="worker_profile"
    )
    display_name = models.CharField(max_length=120, blank=True)
    languages = models.JSONField(default=list, blank=True)
    service_categories = models.ManyToManyField(
        ServiceCategory, blank=True, related_name="workers"
    )
    localities_served = models.ManyToManyField(
        Locality, blank=True, related_name="workers"
    )
    availability = models.JSONField(default=dict, blank=True)
    default_rate_floor = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True
    )
    contact_visibility = models.CharField(
        max_length=10,
        choices=ContactVisibility.choices,
        default=ContactVisibility.PRIVATE,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"WorkerProfile<{self.display_name or self.user.phone}>"


class HouseholdProfile(models.Model):
    """Household / tenant profile. No public resident directory is ever derived from this."""

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="household_profile",
    )
    display_name = models.CharField(max_length=120, blank=True)
    building = models.ForeignKey(
        Building, null=True, blank=True, on_delete=models.SET_NULL, related_name="households"
    )
    unit = models.ForeignKey(
        Unit, null=True, blank=True, on_delete=models.SET_NULL, related_name="households"
    )
    discoverable_to_coop = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"HouseholdProfile<{self.display_name or self.user.phone}>"


class MembershipRequest(models.Model):
    """A signed-in user's ask to join the cooperative as worker or household.

    Approval flips `user.primary_role` to `role_sought`. One pending request
    per user, enforced at the database level.
    """

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        APPROVED = "approved", "Approved"
        REJECTED = "rejected", "Rejected"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="membership_requests"
    )
    role_sought = models.CharField(max_length=20)
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.PENDING)
    rejection_reason = models.TextField(blank=True)
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="membership_reviews",
    )
    reviewed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["user"],
                condition=Q(status="pending"),
                name="uniq_pending_membership_request",
            )
        ]

    def __str__(self):
        return f"MembershipRequest<{self.user.phone} → {self.role_sought} ({self.status})>"


class ServiceNeed(models.Model):
    """A household's request for a service. Never public; moderators and the
    owning household can read it. Matching and offers arrive in later gates."""

    class Status(models.TextChoices):
        OPEN = "open", "Open"
        MATCHED = "matched", "Matched"
        CLOSED = "closed", "Closed"

    household = models.ForeignKey(
        HouseholdProfile, on_delete=models.CASCADE, related_name="service_needs"
    )
    category = models.ForeignKey(
        ServiceCategory, on_delete=models.PROTECT, related_name="needs"
    )
    title = models.CharField(max_length=120)
    details = models.TextField(blank=True)
    locality = models.ForeignKey(
        Locality, null=True, blank=True, on_delete=models.SET_NULL, related_name="service_needs"
    )
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.OPEN)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"ServiceNeed<{self.title} ({self.status})>"

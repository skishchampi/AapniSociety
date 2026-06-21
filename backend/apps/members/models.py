from django.conf import settings
from django.db import models

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

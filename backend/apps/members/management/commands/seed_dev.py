"""Idempotent development seed: service categories, the Ahmedabad pilot locality,
a sample building, and one demo worker + one demo household user."""
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db import transaction

from apps.accounts.models import Role
from apps.geo.models import Building, City, Locality, Unit
from apps.members.models import HouseholdProfile, ServiceCategory, WorkerProfile

User = get_user_model()

CATEGORIES = [
    ("maid", "Maid"),
    ("cook", "Cook"),
    ("driver", "Driver"),
    ("plumber", "Plumber"),
    ("electrician", "Electrician"),
    ("caregiver", "Caregiver"),
]


class Command(BaseCommand):
    help = "Seed development data (idempotent)."

    @transaction.atomic
    def handle(self, *args, **options):
        for key, label in CATEGORIES:
            ServiceCategory.objects.get_or_create(key=key, defaults={"label": label})

        city, _ = City.objects.get_or_create(
            slug="ahmedabad", defaults={"name": "Ahmedabad", "state": "Gujarat"}
        )
        locality, _ = Locality.objects.get_or_create(
            city=city, slug="prahladnagar", defaults={"name": "Prahladnagar"}
        )
        building, _ = Building.objects.get_or_create(
            locality=locality,
            name="Pilot Apartments",
            defaults={"address": "Prahladnagar, Ahmedabad"},
        )
        unit, _ = Unit.objects.get_or_create(building=building, label="A-204")

        worker, created = User.objects.get_or_create(
            phone="+919900000001",
            defaults={"full_name": "Demo Worker", "primary_role": Role.WORKER},
        )
        wp, _ = WorkerProfile.objects.get_or_create(
            user=worker, defaults={"display_name": "Demo Worker"}
        )
        wp.service_categories.set(ServiceCategory.objects.filter(key__in=["maid", "cook"]))
        wp.localities_served.set([locality])

        household, _ = User.objects.get_or_create(
            phone="+919900000002",
            defaults={"full_name": "Demo Household", "primary_role": Role.HOUSEHOLD},
        )
        HouseholdProfile.objects.get_or_create(
            user=household,
            defaults={"display_name": "Demo Household", "building": building, "unit": unit},
        )

        if not User.objects.filter(is_superuser=True).exists():
            User.objects.create_superuser(phone="+919900000000", password="admin12345")
            self.stdout.write("Created superuser +919900000000 / admin12345 (dev only)")

        self.stdout.write(self.style.SUCCESS("Seed complete."))

from rest_framework import serializers

from .models import HouseholdProfile, ServiceCategory, WorkerProfile


class ServiceCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceCategory
        fields = ["id", "key", "label", "is_active"]


class WorkerProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkerProfile
        fields = [
            "id",
            "display_name",
            "languages",
            "service_categories",
            "localities_served",
            "availability",
            "default_rate_floor",
            "contact_visibility",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class HouseholdProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = HouseholdProfile
        fields = [
            "id",
            "display_name",
            "building",
            "unit",
            "discoverable_to_coop",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

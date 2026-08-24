from rest_framework import serializers

from .models import (
    HouseholdProfile,
    MembershipRequest,
    ServiceCategory,
    ServiceNeed,
    WorkerProfile,
)


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


class MembershipRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = MembershipRequest
        fields = ["id", "role_sought", "status", "rejection_reason", "created_at", "reviewed_at"]
        read_only_fields = ["id", "status", "rejection_reason", "created_at", "reviewed_at"]


class MembershipReviewSerializer(serializers.Serializer):
    action = serializers.ChoiceField(choices=["approve", "reject"])
    reason = serializers.CharField(required=False, allow_blank=True, default="")


class ServiceNeedSerializer(serializers.ModelSerializer):
    household = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = ServiceNeed
        fields = [
            "id",
            "household",
            "category",
            "title",
            "details",
            "locality",
            "status",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "household", "created_at", "updated_at"]

from rest_framework import serializers

from .models import (
    HouseholdProfile,
    IntroductionEvent,
    IntroductionRequest,
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


class IntroductionCreateSerializer(serializers.ModelSerializer):
    """Writable payload for filing an introduction. Never renders contacts."""

    class Meta:
        model = IntroductionRequest
        fields = ["id", "worker", "category", "note"]
        read_only_fields = ["id"]


ROUTED_PLUS = {
    IntroductionRequest.Status.ROUTED,
    IntroductionRequest.Status.ACCEPTED,
    IntroductionRequest.Status.DECLINED,
}


class IntroductionSerializer(serializers.ModelSerializer):
    """Read view for one introduction, gated by the viewer's role.

    The household sees the worker's name only after routing. The worker sees
    the household's name only after routing. No phone or email ever appears
    here; contact flows only through the reveal endpoint.
    """

    household_name = serializers.SerializerMethodField()
    worker_name = serializers.SerializerMethodField()
    note = serializers.SerializerMethodField()

    class Meta:
        model = IntroductionRequest
        fields = [
            "id",
            "status",
            "category",
            "worker",
            "household",
            "worker_name",
            "household_name",
            "note",
            "created_at",
        ]
        read_only_fields = fields

    def _viewer_role(self) -> str:
        return (self.context.get("viewer_role") or "").strip()

    def _is_moderator(self) -> bool:
        return self._viewer_role() in {"moderator", "operator", "admin"}

    def _is_household_viewer(self, obj: IntroductionRequest) -> bool:
        user = self.context.get("viewer_user")
        return bool(user and obj.household.user_id == getattr(user, "id", None))

    def _is_worker_viewer(self, obj: IntroductionRequest) -> bool:
        user = self.context.get("viewer_user")
        return bool(user and obj.worker.user_id == getattr(user, "id", None))

    def get_household_name(self, obj: IntroductionRequest) -> str:
        if not (self._is_moderator() or self._is_worker_viewer(obj)):
            return ""
        routed_plus = obj.status in ROUTED_PLUS
        if self._is_worker_viewer(obj) and not routed_plus and not self._is_moderator():
            return ""
        name = obj.household.display_name
        return name if name else "(household)"

    def get_worker_name(self, obj: IntroductionRequest) -> str:
        if not (self._is_moderator() or self._is_household_viewer(obj)):
            return ""
        routed_plus = obj.status in ROUTED_PLUS
        if self._is_household_viewer(obj) and not routed_plus and not self._is_moderator():
            return ""
        name = obj.worker.display_name
        return name if name else "(worker)"

    def get_note(self, obj: IntroductionRequest) -> str:
        # The note is the household's words to the worker; show it to the
        # worker, moderators, and the author. Strangers get nothing anyway.
        return obj.note


class IntroductionEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = IntroductionEvent
        fields = ["id", "what", "detail", "created_at"]
        read_only_fields = fields

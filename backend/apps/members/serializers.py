from rest_framework import serializers

from .models import (
    AbuseReport,
    AdminAuditLog,
    HouseholdProfile,
    IntroductionEvent,
    IntroductionRequest,
    MembershipRequest,
    ReferenceRequest,
    SafetyNote,
    ServiceCategory,
    ServiceNeed,
    WorkerBlock,
    WorkerProfile,
    WorkerReference,
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
    below_floor = serializers.SerializerMethodField()

    class Meta:
        model = ServiceNeed
        fields = [
            "id",
            "household",
            "category",
            "title",
            "details",
            "locality",
            "offered_rate",
            "matched_worker",
            "below_floor",
            "status",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "household", "below_floor", "created_at", "updated_at"]

    def _is_moderator(self) -> bool:
        role = (self.context.get("viewer_role") or "").strip()
        return role in {"moderator", "operator", "admin"}

    def get_below_floor(self, obj: ServiceNeed) -> bool | None:
        if not self._is_moderator():
            return None
        return obj.below_floor

    def to_representation(self, instance):
        data = super().to_representation(instance)
        if not self._is_moderator():
            data.pop("below_floor", None)
        return data


class IntroductionCreateSerializer(serializers.ModelSerializer):
    """Writable payload for filing an introduction. Never renders contacts."""

    class Meta:
        model = IntroductionRequest
        fields = ["id", "worker", "category", "offered_rate", "note"]
        read_only_fields = ["id"]


ROUTED_PLUS = {
    IntroductionRequest.Status.ROUTED,
    IntroductionRequest.Status.ACCEPTED,
    IntroductionRequest.Status.DECLINED,
}


class SharedReferenceSerializer(serializers.ModelSerializer):
    """Text-only reference payload shared inside routed introductions.

    Never carries star ratings, household contact details, or private notes.
    """

    class Meta:
        model = WorkerReference
        fields = ["id", "body", "created_at"]
        read_only_fields = fields


class IntroductionSerializer(serializers.ModelSerializer):
    """Read view for one introduction, gated by the viewer's role.

    The household sees the worker's name only after routing. The worker sees
    the household's name only after routing. Shared references appear only
    after routing. Below-floor flags go to the worker and moderators, never
    to the household. No phone or email ever appears here.
    """

    household_name = serializers.SerializerMethodField()
    worker_name = serializers.SerializerMethodField()
    note = serializers.SerializerMethodField()
    below_floor = serializers.SerializerMethodField()
    shared_references = serializers.SerializerMethodField()

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
            "offered_rate",
            "below_floor",
            "shared_references",
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

    def get_below_floor(self, obj: IntroductionRequest) -> bool | None:
        if not (self._is_moderator() or self._is_worker_viewer(obj)):
            return None
        return obj.below_floor

    def get_shared_references(self, obj: IntroductionRequest) -> list[dict]:
        if obj.status not in ROUTED_PLUS:
            return []
        refs = obj.worker.references.filter(visibility=WorkerReference.Visibility.SHARED)
        return SharedReferenceSerializer(refs, many=True).data

    def to_representation(self, instance):
        data = super().to_representation(instance)
        if not (self._is_moderator() or self._is_worker_viewer(instance)):
            data.pop("below_floor", None)
        return data


class IntroductionEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = IntroductionEvent
        fields = ["id", "what", "detail", "created_at"]
        read_only_fields = fields


class WorkerReferenceCreateSerializer(serializers.ModelSerializer):
    introduction = serializers.PrimaryKeyRelatedField(queryset=IntroductionRequest.objects.all())
    rating = serializers.IntegerField(required=False, allow_null=True, min_value=1, max_value=5)

    class Meta:
        model = WorkerReference
        fields = ["id", "introduction", "body", "rating"]
        read_only_fields = ["id"]


class WorkerReferenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkerReference
        fields = [
            "id",
            "introduction",
            "body",
            "rating",
            "visibility",
            "created_at",
            "updated_at",
        ]
        read_only_fields = fields


class ReferenceVisibilitySerializer(serializers.Serializer):
    visibility = serializers.ChoiceField(choices=WorkerReference.Visibility.choices)


class ReferenceRequestSerializer(serializers.ModelSerializer):
    worker = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = ReferenceRequest
        fields = [
            "id",
            "worker",
            "household",
            "introduction",
            "status",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "worker", "status", "created_at", "updated_at"]


class WorkerBlockSerializer(serializers.ModelSerializer):
    worker = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = WorkerBlock
        fields = ["id", "worker", "household", "reason", "created_at"]
        read_only_fields = ["id", "worker", "created_at"]


class AbuseReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = AbuseReport
        fields = [
            "id",
            "reported_household",
            "introduction",
            "category",
            "details",
            "status",
            "resolution_note",
            "reviewed_at",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "status",
            "resolution_note",
            "reviewed_at",
            "created_at",
            "updated_at",
        ]


class AbuseReportResolveSerializer(serializers.Serializer):
    status = serializers.ChoiceField(
        choices=[
            AbuseReport.Status.REVIEWING,
            AbuseReport.Status.RESOLVED,
            AbuseReport.Status.DISMISSED,
        ]
    )
    resolution_note = serializers.CharField(required=False, allow_blank=True, default="")


class SafetyNoteSerializer(serializers.ModelSerializer):
    """Worker-authored city safety note. Never emits author identity or contact."""

    class Meta:
        model = SafetyNote
        fields = [
            "id",
            "locality",
            "building",
            "note_type",
            "evidence_level",
            "body",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class AdminAuditLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = AdminAuditLog
        fields = ["id", "actor", "action", "target_type", "target_id", "detail", "created_at"]
        read_only_fields = fields

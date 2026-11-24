from django.db.models import Avg, Count, Max, Min, Q
from django.utils import timezone
from rest_framework import generics, status
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import AllowAny, BasePermission, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.geo.models import Locality

from .models import (
    AbuseReport,
    AdminAuditLog,
    HouseholdProfile,
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
from .notifications import notify_introduction_event
from .serializers import (
    AbuseReportResolveSerializer,
    AbuseReportSerializer,
    AdminAuditLogSerializer,
    HouseholdProfileSerializer,
    IntroductionCreateSerializer,
    IntroductionEventSerializer,
    IntroductionSerializer,
    MembershipRequestSerializer,
    MembershipReviewSerializer,
    ReferenceRequestSerializer,
    ReferenceVisibilitySerializer,
    SafetyNoteSerializer,
    ServiceCategorySerializer,
    ServiceNeedSerializer,
    WorkerBlockSerializer,
    WorkerProfileSerializer,
    WorkerReferenceCreateSerializer,
    WorkerReferenceSerializer,
)

MODERATOR_ROLES = {"moderator", "operator", "admin"}
HOUSEHOLD_ROLE = "household"
WORKER_ROLE = "worker"


class IsModerator(BasePermission):
    """Cooperative moderators, operators, and system admins only."""

    message = "Requires a cooperative moderator role."

    def has_permission(self, request, view):
        user = request.user
        return bool(user and user.is_authenticated and user.primary_role in MODERATOR_ROLES)


class IsHousehold(BasePermission):
    message = "Only household accounts can do this."

    def has_permission(self, request, view):
        user = request.user
        return bool(user and user.is_authenticated and user.primary_role == HOUSEHOLD_ROLE)


class IsWorker(BasePermission):
    message = "Only worker accounts can do this."

    def has_permission(self, request, view):
        user = request.user
        return bool(user and user.is_authenticated and user.primary_role == WORKER_ROLE)


class IsWorkerOrModerator(BasePermission):
    message = "Safety notes are restricted to workers and cooperative moderators."

    def has_permission(self, request, view):
        user = request.user
        return bool(
            user
            and user.is_authenticated
            and (user.primary_role == WORKER_ROLE or user.primary_role in MODERATOR_ROLES)
        )


def _log_admin_action(actor, action: str, target_type: str, target_id: int, detail: str = ""):
    AdminAuditLog.objects.create(
        actor=actor,
        action=action,
        target_type=target_type,
        target_id=target_id,
        detail=detail,
    )


class ServiceCategoryListView(generics.ListAPIView):
    queryset = ServiceCategory.objects.filter(is_active=True)
    serializer_class = ServiceCategorySerializer
    permission_classes = [AllowAny]
    pagination_class = None


class WorkerProfileMeView(generics.RetrieveUpdateAPIView):
    """GET/PUT the signed-in user's worker profile, creating it on first write."""

    serializer_class = WorkerProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        obj, _ = WorkerProfile.objects.get_or_create(user=self.request.user)
        return obj


class HouseholdProfileMeView(generics.RetrieveUpdateAPIView):
    serializer_class = HouseholdProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        obj, _ = HouseholdProfile.objects.get_or_create(user=self.request.user)
        return obj


class MembershipRequestCreateView(generics.CreateAPIView):
    """Ask to join the cooperative as worker or household.

    Refuses with 409 when a pending request already exists or when the caller
    already holds the sought role.
    """

    serializer_class = MembershipRequestSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        role_sought = request.data.get("role_sought")
        if role_sought not in {"worker", "household"}:
            raise ValidationError({"role_sought": "Must be 'worker' or 'household'."})
        pending = MembershipRequest.objects.filter(
            user=request.user, status=MembershipRequest.Status.PENDING
        ).exists()
        if pending:
            return Response(
                {"detail": "A pending membership request already exists."},
                status=status.HTTP_409_CONFLICT,
            )
        if request.user.primary_role == role_sought:
            return Response(
                {"detail": "You already hold this role."},
                status=status.HTTP_409_CONFLICT,
            )
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(user=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class MyMembershipRequestsView(generics.ListAPIView):
    serializer_class = MembershipRequestSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = None

    def get_queryset(self):
        return MembershipRequest.objects.filter(user=self.request.user)


class MembershipQueueView(generics.ListAPIView):
    """Pending requests for cooperative moderators."""

    serializer_class = MembershipRequestSerializer
    permission_classes = [IsAuthenticated, IsModerator]
    pagination_class = None

    def get_queryset(self):
        return MembershipRequest.objects.filter(status=MembershipRequest.Status.PENDING)


class MembershipReviewView(APIView):
    """Approve or reject one membership request. Moderators only.

    Approval flips the requester's `primary_role` to the sought role.
    """

    permission_classes = [IsAuthenticated, IsModerator]

    def post(self, request, pk):
        membership_request = get_object_or_404(MembershipRequest, pk=pk)
        if membership_request.status != MembershipRequest.Status.PENDING:
            return Response(
                {"detail": "This request was already reviewed."},
                status=status.HTTP_409_CONFLICT,
            )
        serializer = MembershipReviewSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        action = serializer.validated_data["action"]

        membership_request.reviewed_by = request.user
        membership_request.reviewed_at = timezone.now()
        if action == "approve":
            membership_request.status = MembershipRequest.Status.APPROVED
            membership_request.rejection_reason = ""
            requester = membership_request.user
            requester.primary_role = membership_request.role_sought
            requester.save(update_fields=["primary_role"])
        else:
            membership_request.status = MembershipRequest.Status.REJECTED
            membership_request.rejection_reason = serializer.validated_data["reason"]
        membership_request.save()
        _log_admin_action(
            request.user,
            f"membership_{membership_request.status}",
            "MembershipRequest",
            membership_request.id,
            detail=membership_request.rejection_reason,
        )

        return Response(MembershipRequestSerializer(membership_request).data)


class ServiceNeedListCreateView(generics.ListCreateAPIView):
    """Households file service needs. Moderators see all needs. No public access."""

    serializer_class = ServiceNeedSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = None

    def get_queryset(self):
        user = self.request.user
        qs = ServiceNeed.objects.select_related("matched_worker")
        if user.primary_role in MODERATOR_ROLES:
            return qs
        return qs.filter(household__user=user)

    def get_permissions(self):
        if self.request.method == "POST":
            return [IsAuthenticated(), IsHousehold()]
        return super().get_permissions()

    def get_serializer_context(self):
        return {**super().get_serializer_context(), **_viewer_context(self)}

    def perform_create(self, serializer):
        household, _ = HouseholdProfile.objects.get_or_create(user=self.request.user)
        serializer.save(household=household)


class ServiceNeedDetailView(generics.RetrieveUpdateAPIView):
    """One service need. Owners read and edit their own; moderators read all."""

    serializer_class = ServiceNeedSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        qs = ServiceNeed.objects.select_related("matched_worker")
        if user.primary_role in MODERATOR_ROLES:
            return qs
        return qs.filter(household__user=user)

    def get_serializer_context(self):
        return {**super().get_serializer_context(), **_viewer_context(self)}


def _viewer_context(view) -> dict:
    user = view.request.user
    return {"viewer_role": getattr(user, "primary_role", ""), "viewer_user": user}


class IntroductionCreateView(generics.CreateAPIView):
    """A household files an introduction request for one worker."""

    serializer_class = IntroductionCreateSerializer
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        return [IsAuthenticated(), IsHousehold()]

    def perform_create(self, serializer):
        household, _ = HouseholdProfile.objects.get_or_create(user=self.request.user)
        worker = serializer.validated_data["worker"]
        if WorkerBlock.objects.filter(worker=worker, household=household).exists():
            raise PermissionDenied("Introduction could not be created.")
        introduction = serializer.save(
            household=household, status=IntroductionRequest.Status.REQUESTED
        )
        introduction.record_event(self.request.user, IntroductionRequest.Status.REQUESTED)
        notify_introduction_event(introduction, "requested")


class MyIntroductionsView(generics.ListAPIView):
    """Role-scoped list: households see their own, workers theirs, mods all."""

    serializer_class = IntroductionSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = None

    def get_queryset(self):
        user = self.request.user
        qs = IntroductionRequest.objects.select_related(
            "household", "worker", "worker__user"
        )
        if user.primary_role in MODERATOR_ROLES:
            return qs
        if user.primary_role == WORKER_ROLE:
            return qs.filter(worker__user=user)
        return qs.filter(household__user=user)

    def get_serializer_context(self):
        return {**super().get_serializer_context(), **_viewer_context(self)}


def _get_introduction_for(view, pk: int) -> IntroductionRequest:
    """404 unless the caller is a participant or a moderator."""
    user = view.request.user
    qs = IntroductionRequest.objects.select_related("household", "worker")
    if user.primary_role not in MODERATOR_ROLES:
        qs = qs.filter(Q(household__user=user) | Q(worker__user=user))
    return get_object_or_404(qs, pk=pk)


class IntroductionRouteView(APIView):
    """Moderator moves a requested introduction to routed."""

    permission_classes = [IsAuthenticated, IsModerator]

    def post(self, request, pk):
        introduction = get_object_or_404(IntroductionRequest, pk=pk)
        if introduction.status != IntroductionRequest.Status.REQUESTED:
            return Response(
                {"detail": "Only requested introductions can be routed."},
                status=status.HTTP_409_CONFLICT,
            )
        if WorkerBlock.objects.filter(
            worker=introduction.worker, household=introduction.household
        ).exists():
            return Response(
                {"detail": "Worker has blocked this household."},
                status=status.HTTP_409_CONFLICT,
            )
        introduction.status = IntroductionRequest.Status.ROUTED
        introduction.routed_by = request.user
        introduction.routed_at = timezone.now()
        introduction.save(update_fields=["status", "routed_by", "routed_at", "updated_at"])
        introduction.record_event(request.user, IntroductionRequest.Status.ROUTED)
        _log_admin_action(
            request.user, "introduction_routed", "IntroductionRequest", introduction.id
        )
        notify_introduction_event(introduction, "routed")
        return Response({"id": introduction.id, "status": introduction.status})


class IntroductionDecideView(APIView):
    """The routed worker accepts or declines."""

    permission_classes = [IsAuthenticated]

    def post(self, request, pk, action: str):
        introduction = get_object_or_404(
            IntroductionRequest.objects.select_related("worker"), pk=pk
        )
        if introduction.worker.user_id != request.user.id:
            raise PermissionDenied("Only the addressed worker can decide.")
        if introduction.status != IntroductionRequest.Status.ROUTED:
            return Response(
                {"detail": "Only routed introductions can be decided."},
                status=status.HTTP_409_CONFLICT,
            )
        new_status = (
            IntroductionRequest.Status.ACCEPTED
            if action == "accept"
            else IntroductionRequest.Status.DECLINED
        )
        introduction.status = new_status
        introduction.decided_at = timezone.now()
        introduction.save(update_fields=["status", "decided_at", "updated_at"])
        introduction.record_event(request.user, new_status)
        notify_introduction_event(introduction, new_status)
        return Response({"id": introduction.id, "status": introduction.status})


class IntroductionWithdrawView(APIView):
    """The household pulls its request before the worker decides."""

    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        introduction = get_object_or_404(IntroductionRequest, pk=pk)
        if introduction.household.user_id != request.user.id:
            raise PermissionDenied("Only the requesting household can withdraw.")
        open_states = {
            IntroductionRequest.Status.REQUESTED,
            IntroductionRequest.Status.ROUTED,
        }
        if introduction.status not in open_states:
            return Response(
                {"detail": "This introduction is already decided."},
                status=status.HTTP_409_CONFLICT,
            )
        introduction.status = IntroductionRequest.Status.WITHDRAWN
        introduction.decided_at = timezone.now()
        introduction.save(update_fields=["status", "decided_at", "updated_at"])
        introduction.record_event(request.user, IntroductionRequest.Status.WITHDRAWN)
        notify_introduction_event(introduction, "withdrawn")
        return Response({"id": introduction.id, "status": introduction.status})


class RevealContactView(APIView):
    """Worker-only contact reveal, allowed once the intro is accepted.

    Writes the append-only contact_revealed event and returns the worker's
    contact fields in this one response. Nothing else ever carries them.
    """

    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        introduction = get_object_or_404(
            IntroductionRequest.objects.select_related("worker", "worker__user"), pk=pk
        )
        if introduction.worker.user_id != request.user.id:
            raise PermissionDenied("Only the addressed worker can reveal contact.")
        if introduction.status != IntroductionRequest.Status.ACCEPTED:
            return Response(
                {"detail": "Contact reveals only after acceptance."},
                status=status.HTTP_409_CONFLICT,
            )
        introduction.record_event(request.user, "contact_revealed")
        notify_introduction_event(introduction, "contact_revealed")
        worker_user = introduction.worker.user
        return Response(
            {
                "revealed": True,
                "phone": worker_user.phone,
                "email": worker_user.email,
            }
        )


class IntroductionEventsView(generics.ListAPIView):
    """Append-only audit trail. Participants and moderators only."""

    serializer_class = IntroductionEventSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = None

    def get_queryset(self):
        introduction = _get_introduction_for(self, int(self.kwargs["pk"]))
        return introduction.events.all()


class ReferenceRequestListCreateView(generics.ListCreateAPIView):
    """Workers invite households to write references. Lists are role-scoped."""

    serializer_class = ReferenceRequestSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = None

    def get_queryset(self):
        user = self.request.user
        if user.primary_role in MODERATOR_ROLES:
            return ReferenceRequest.objects.all()
        if user.primary_role == WORKER_ROLE:
            return ReferenceRequest.objects.filter(worker__user=user)
        return ReferenceRequest.objects.filter(household__user=user)

    def get_permissions(self):
        if self.request.method == "POST":
            return [IsAuthenticated(), IsWorker()]
        return super().get_permissions()

    def perform_create(self, serializer):
        worker, _ = WorkerProfile.objects.get_or_create(user=self.request.user)
        introduction = serializer.validated_data.get("introduction")
        household = serializer.validated_data["household"]
        if introduction is not None:
            if introduction.worker_id != worker.id:
                raise PermissionDenied("You can only link your own introduction.")
            if introduction.household_id != household.id:
                raise ValidationError({"introduction": "Introduction does not match household."})
        serializer.save(worker=worker)


class WorkerReferenceCreateView(APIView):
    """Household writes a reference for an accepted introduction.

    Refuses with 403 if the caller is not the introduction's household, and
    with 409 if the introduction is not accepted or already has a reference.
    """

    permission_classes = [IsAuthenticated, IsHousehold]

    def post(self, request):
        serializer = WorkerReferenceCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        introduction = serializer.validated_data["introduction"]
        if introduction.household.user_id != request.user.id:
            raise PermissionDenied(
                "Only the household from this introduction can write a reference."
            )
        if introduction.status != IntroductionRequest.Status.ACCEPTED:
            return Response(
                {"detail": "A reference requires an accepted introduction."},
                status=status.HTTP_409_CONFLICT,
            )
        if WorkerReference.objects.filter(introduction=introduction).exists():
            return Response(
                {"detail": "A reference already exists for this introduction."},
                status=status.HTTP_409_CONFLICT,
            )
        reference = serializer.save(
            written_by=request.user,
            worker=introduction.worker,
            visibility=WorkerReference.Visibility.PRIVATE,
        )
        ReferenceRequest.objects.filter(
            worker=introduction.worker,
            household=introduction.household,
            status=ReferenceRequest.Status.PENDING,
        ).filter(Q(introduction=introduction) | Q(introduction__isnull=True)).update(
            status=ReferenceRequest.Status.WRITTEN
        )
        return Response(WorkerReferenceSerializer(reference).data, status=status.HTTP_201_CREATED)


class MyReferencesView(generics.ListAPIView):
    """The signed-in worker's own references with their visibility state."""

    serializer_class = WorkerReferenceSerializer
    permission_classes = [IsAuthenticated, IsWorker]
    pagination_class = None

    def get_queryset(self):
        return WorkerReference.objects.filter(worker__user=self.request.user)


class ReferenceVisibilityView(APIView):
    """Worker-only visibility control: private, coop, or shared."""

    permission_classes = [IsAuthenticated]

    def patch(self, request, pk):
        reference = get_object_or_404(
            WorkerReference.objects.select_related("worker"), pk=pk
        )
        if reference.worker.user_id != request.user.id:
            raise PermissionDenied("Only the worker can change reference visibility.")
        serializer = ReferenceVisibilitySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        reference.visibility = serializer.validated_data["visibility"]
        reference.save(update_fields=["visibility", "updated_at"])
        return Response(WorkerReferenceSerializer(reference).data)


def _fmt_rate(val) -> str | None:
    if val is None:
        return None
    return f"{val:.2f}"


class BargainingSummaryView(APIView):
    """Cooperative-side aggregate rates and demand counts per category and locality.

    Never exposed to households. Carries no individual worker identifiers or
    star ratings.
    """

    permission_classes = [IsAuthenticated, IsModerator]

    def get(self, request):
        by_category = []
        for cat in ServiceCategory.objects.filter(is_active=True):
            worker_stats = WorkerProfile.objects.filter(service_categories=cat).aggregate(
                worker_count=Count("id", distinct=True),
                avg_rate_floor=Avg("default_rate_floor"),
                min_rate_floor=Min("default_rate_floor"),
                max_rate_floor=Max("default_rate_floor"),
            )
            needs_qs = ServiceNeed.objects.filter(category=cat).select_related("matched_worker")
            need_stats = needs_qs.aggregate(
                need_count=Count("id"),
                avg_offered_rate=Avg("offered_rate"),
            )
            below_needs = sum(1 for n in needs_qs if n.below_floor is True)
            intros_qs = IntroductionRequest.objects.filter(category=cat).select_related("worker")
            below_intros = sum(1 for i in intros_qs if i.below_floor is True)
            by_category.append(
                {
                    "category_id": cat.id,
                    "category_label": cat.label,
                    "worker_count": worker_stats["worker_count"] or 0,
                    "avg_rate_floor": _fmt_rate(worker_stats["avg_rate_floor"]),
                    "min_rate_floor": _fmt_rate(worker_stats["min_rate_floor"]),
                    "max_rate_floor": _fmt_rate(worker_stats["max_rate_floor"]),
                    "need_count": need_stats["need_count"] or 0,
                    "avg_offered_rate": _fmt_rate(need_stats["avg_offered_rate"]),
                    "below_floor_count": below_needs + below_intros,
                }
            )

        by_locality = []
        for loc in Locality.objects.all():
            worker_count = WorkerProfile.objects.filter(localities_served=loc).count()
            need_stats = ServiceNeed.objects.filter(locality=loc).aggregate(
                need_count=Count("id"),
                avg_offered_rate=Avg("offered_rate"),
            )
            by_locality.append(
                {
                    "locality_id": loc.id,
                    "locality_name": loc.name,
                    "worker_count": worker_count,
                    "need_count": need_stats["need_count"] or 0,
                    "avg_offered_rate": _fmt_rate(need_stats["avg_offered_rate"]),
                }
            )

        return Response({"by_category": by_category, "by_locality": by_locality})


class WorkerBlockListCreateView(generics.ListCreateAPIView):
    """Worker blocks a household or lists their own active blocks."""

    serializer_class = WorkerBlockSerializer
    permission_classes = [IsAuthenticated, IsWorker]
    pagination_class = None

    def get_queryset(self):
        return WorkerBlock.objects.filter(worker__user=self.request.user)

    def create(self, request, *args, **kwargs):
        worker, _ = WorkerProfile.objects.get_or_create(user=request.user)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        household = serializer.validated_data["household"]
        if WorkerBlock.objects.filter(worker=worker, household=household).exists():
            return Response(
                {"detail": "This household is already blocked."},
                status=status.HTTP_409_CONFLICT,
            )
        block = serializer.save(worker=worker)
        return Response(WorkerBlockSerializer(block).data, status=status.HTTP_201_CREATED)


class WorkerBlockDeleteView(generics.DestroyAPIView):
    """Worker removes one of their own household blocks."""

    permission_classes = [IsAuthenticated, IsWorker]

    def get_queryset(self):
        return WorkerBlock.objects.filter(worker__user=self.request.user)


class AbuseReportListCreateView(generics.ListCreateAPIView):
    """File or view confidential abuse reports.

    Reporters see only their own reports. Moderators see all reports.
    Reported households never see reports filed against them.
    """

    serializer_class = AbuseReportSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = None

    def get_queryset(self):
        user = self.request.user
        if user.primary_role in MODERATOR_ROLES:
            return AbuseReport.objects.all()
        return AbuseReport.objects.filter(reporter=user)

    def perform_create(self, serializer):
        serializer.save(reporter=self.request.user)


class AbuseReportResolveView(APIView):
    """Moderator reviews, resolves, or dismisses an abuse report."""

    permission_classes = [IsAuthenticated, IsModerator]

    def post(self, request, pk):
        report = get_object_or_404(AbuseReport, pk=pk)
        serializer = AbuseReportResolveSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        report.status = serializer.validated_data["status"]
        report.resolution_note = serializer.validated_data["resolution_note"]
        report.reviewed_by = request.user
        report.reviewed_at = timezone.now()
        report.save(
            update_fields=["status", "resolution_note", "reviewed_by", "reviewed_at", "updated_at"]
        )
        _log_admin_action(
            request.user,
            f"report_{report.status}",
            "AbuseReport",
            report.id,
            detail=report.resolution_note,
        )
        return Response(AbuseReportSerializer(report).data)


class SafetyNoteListCreateView(generics.ListCreateAPIView):
    """Worker-authored city safety notes. Never exposed to households or public."""

    serializer_class = SafetyNoteSerializer
    permission_classes = [IsAuthenticated, IsWorkerOrModerator]
    pagination_class = None

    def get_queryset(self):
        return SafetyNote.objects.all()

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class AdminAuditLogListView(generics.ListAPIView):
    """Append-only log of moderator and admin actions. Moderators only."""

    serializer_class = AdminAuditLogSerializer
    permission_classes = [IsAuthenticated, IsModerator]
    pagination_class = None

    def get_queryset(self):
        return AdminAuditLog.objects.all()

from django.db.models import Q
from django.utils import timezone
from rest_framework import generics, status
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import AllowAny, BasePermission, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import (
    HouseholdProfile,
    IntroductionRequest,
    MembershipRequest,
    ServiceCategory,
    ServiceNeed,
    WorkerProfile,
)
from .notifications import notify_introduction_event
from .serializers import (
    HouseholdProfileSerializer,
    IntroductionCreateSerializer,
    IntroductionEventSerializer,
    IntroductionSerializer,
    MembershipRequestSerializer,
    MembershipReviewSerializer,
    ServiceCategorySerializer,
    ServiceNeedSerializer,
    WorkerProfileSerializer,
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

        return Response(MembershipRequestSerializer(membership_request).data)


class ServiceNeedListCreateView(generics.ListCreateAPIView):
    """Households file service needs. Moderators see all needs. No public access."""

    serializer_class = ServiceNeedSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = None

    def get_queryset(self):
        user = self.request.user
        if user.primary_role in MODERATOR_ROLES:
            return ServiceNeed.objects.all()
        return ServiceNeed.objects.filter(household__user=user)

    def get_permissions(self):
        if self.request.method == "POST":
            return [IsAuthenticated(), IsHousehold()]
        return super().get_permissions()

    def perform_create(self, serializer):
        household, _ = HouseholdProfile.objects.get_or_create(user=self.request.user)
        serializer.save(household=household)


class ServiceNeedDetailView(generics.RetrieveUpdateAPIView):
    """One service need. Owners read and edit their own; moderators read all."""

    serializer_class = ServiceNeedSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.primary_role in MODERATOR_ROLES:
            return ServiceNeed.objects.all()
        return ServiceNeed.objects.filter(household__user=user)


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
        introduction.status = IntroductionRequest.Status.ROUTED
        introduction.routed_by = request.user
        introduction.routed_at = timezone.now()
        introduction.save(update_fields=["status", "routed_by", "routed_at", "updated_at"])
        introduction.record_event(request.user, IntroductionRequest.Status.ROUTED)
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

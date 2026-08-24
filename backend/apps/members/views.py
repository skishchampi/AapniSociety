from django.utils import timezone
from rest_framework import generics, status
from rest_framework.exceptions import ValidationError
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import AllowAny, BasePermission, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import (
    HouseholdProfile,
    MembershipRequest,
    ServiceCategory,
    ServiceNeed,
    WorkerProfile,
)
from .serializers import (
    HouseholdProfileSerializer,
    MembershipRequestSerializer,
    MembershipReviewSerializer,
    ServiceCategorySerializer,
    ServiceNeedSerializer,
    WorkerProfileSerializer,
)

MODERATOR_ROLES = {"moderator", "operator", "admin"}
HOUSEHOLD_ROLE = "household"


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

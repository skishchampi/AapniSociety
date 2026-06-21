from rest_framework import generics
from rest_framework.permissions import AllowAny, IsAuthenticated

from .models import HouseholdProfile, ServiceCategory, WorkerProfile
from .serializers import (
    HouseholdProfileSerializer,
    ServiceCategorySerializer,
    WorkerProfileSerializer,
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

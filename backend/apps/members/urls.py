from django.urls import path

from .views import (
    HouseholdProfileMeView,
    MembershipQueueView,
    MembershipRequestCreateView,
    MembershipReviewView,
    MyMembershipRequestsView,
    ServiceCategoryListView,
    ServiceNeedDetailView,
    ServiceNeedListCreateView,
    WorkerProfileMeView,
)

urlpatterns = [
    path("me/worker-profile/", WorkerProfileMeView.as_view(), name="me-worker-profile"),
    path(
        "me/household-profile/",
        HouseholdProfileMeView.as_view(),
        name="me-household-profile",
    ),
    path("service-categories/", ServiceCategoryListView.as_view(), name="service-categories"),
    path("membership/request/", MembershipRequestCreateView.as_view(), name="membership-request"),
    path(
        "membership/requests/mine/",
        MyMembershipRequestsView.as_view(),
        name="membership-requests-mine",
    ),
    path("membership/queue/", MembershipQueueView.as_view(), name="membership-queue"),
    path(
        "membership/requests/<int:pk>/review/",
        MembershipReviewView.as_view(),
        name="membership-review",
    ),
    path("needs/", ServiceNeedListCreateView.as_view(), name="service-needs"),
    path("needs/<int:pk>/", ServiceNeedDetailView.as_view(), name="service-need-detail"),
]

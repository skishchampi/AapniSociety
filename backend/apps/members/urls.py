from django.urls import path

from .views import (
    HouseholdProfileMeView,
    IntroductionCreateView,
    IntroductionDecideView,
    IntroductionEventsView,
    IntroductionRouteView,
    IntroductionWithdrawView,
    MembershipQueueView,
    MembershipRequestCreateView,
    MembershipReviewView,
    MyIntroductionsView,
    MyMembershipRequestsView,
    RevealContactView,
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
    path(
        "introductions/",
        IntroductionCreateView.as_view(),
        name="introduction-create",
    ),
    path(
        "introductions/mine/",
        MyIntroductionsView.as_view(),
        name="introductions-mine",
    ),
    path(
        "introductions/<int:pk>/withdraw/",
        IntroductionWithdrawView.as_view(),
        name="introduction-withdraw",
    ),
    path(
        "introductions/<int:pk>/accept/",
        IntroductionDecideView.as_view(),
        {"action": "accept"},
        name="introduction-accept",
    ),
    path(
        "introductions/<int:pk>/decline/",
        IntroductionDecideView.as_view(),
        {"action": "decline"},
        name="introduction-decline",
    ),
    path(
        "introductions/<int:pk>/reveal-contact/",
        RevealContactView.as_view(),
        name="introduction-reveal",
    ),
    path(
        "introductions/<int:pk>/events/",
        IntroductionEventsView.as_view(),
        name="introduction-events",
    ),
    path(
        "moderation/introductions/<int:pk>/route/",
        IntroductionRouteView.as_view(),
        name="introduction-route",
    ),
]

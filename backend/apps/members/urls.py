from django.urls import path

from .views import HouseholdProfileMeView, ServiceCategoryListView, WorkerProfileMeView

urlpatterns = [
    path("me/worker-profile/", WorkerProfileMeView.as_view(), name="me-worker-profile"),
    path(
        "me/household-profile/",
        HouseholdProfileMeView.as_view(),
        name="me-household-profile",
    ),
    path("service-categories/", ServiceCategoryListView.as_view(), name="service-categories"),
]

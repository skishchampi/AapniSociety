from django.contrib import admin

from .models import (
    HouseholdProfile,
    MembershipRequest,
    ServiceCategory,
    ServiceNeed,
    WorkerProfile,
)


@admin.register(ServiceCategory)
class ServiceCategoryAdmin(admin.ModelAdmin):
    list_display = ["label", "key", "is_active"]
    prepopulated_fields = {"key": ("label",)}


@admin.register(WorkerProfile)
class WorkerProfileAdmin(admin.ModelAdmin):
    list_display = ["display_name", "user", "contact_visibility", "default_rate_floor"]
    search_fields = ["display_name", "user__phone"]
    filter_horizontal = ["service_categories", "localities_served"]


@admin.register(HouseholdProfile)
class HouseholdProfileAdmin(admin.ModelAdmin):
    list_display = ["display_name", "user", "building", "unit"]
    search_fields = ["display_name", "user__phone"]


@admin.register(MembershipRequest)
class MembershipRequestAdmin(admin.ModelAdmin):
    list_display = ["user", "role_sought", "status", "reviewed_by", "reviewed_at"]
    list_filter = ["status", "role_sought"]
    search_fields = ["user__phone"]


@admin.register(ServiceNeed)
class ServiceNeedAdmin(admin.ModelAdmin):
    list_display = ["title", "household", "category", "locality", "status"]
    list_filter = ["status"]
    search_fields = ["title", "household__display_name"]

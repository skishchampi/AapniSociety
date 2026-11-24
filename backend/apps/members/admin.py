from django.contrib import admin

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
    list_display = ["title", "household", "category", "locality", "offered_rate", "status"]
    list_filter = ["status"]
    search_fields = ["title", "household__display_name"]


@admin.register(WorkerReference)
class WorkerReferenceAdmin(admin.ModelAdmin):
    list_display = ["id", "worker", "introduction", "visibility", "created_at"]
    list_filter = ["visibility"]
    readonly_fields = [
        "introduction",
        "written_by",
        "worker",
        "body",
        "rating",
        "visibility",
        "created_at",
        "updated_at",
    ]

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(ReferenceRequest)
class ReferenceRequestAdmin(admin.ModelAdmin):
    list_display = ["id", "worker", "household", "introduction", "status", "created_at"]
    list_filter = ["status"]


@admin.register(WorkerBlock)
class WorkerBlockAdmin(admin.ModelAdmin):
    list_display = ["id", "worker", "household", "created_at"]


@admin.register(AbuseReport)
class AbuseReportAdmin(admin.ModelAdmin):
    list_display = ["id", "category", "reported_household", "status", "reviewed_by", "created_at"]
    list_filter = ["status", "category"]


@admin.register(SafetyNote)
class SafetyNoteAdmin(admin.ModelAdmin):
    list_display = ["id", "note_type", "evidence_level", "locality", "building", "created_at"]
    list_filter = ["note_type", "evidence_level"]


@admin.register(AdminAuditLog)
class AdminAuditLogAdmin(admin.ModelAdmin):
    list_display = ["id", "actor", "action", "target_type", "target_id", "created_at"]
    list_filter = ["action", "target_type"]
    readonly_fields = ["actor", "action", "target_type", "target_id", "detail", "created_at"]

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(IntroductionRequest)
class IntroductionRequestAdmin(admin.ModelAdmin):
    list_display = ["id", "household", "worker", "category", "status", "routed_by"]
    list_filter = ["status"]
    search_fields = ["household__display_name", "worker__display_name"]

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(IntroductionEvent)
class IntroductionEventAdmin(admin.ModelAdmin):
    list_display = ["introduction", "what", "actor", "created_at"]
    list_filter = ["what"]
    readonly_fields = ["introduction", "actor", "what", "detail", "created_at"]

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

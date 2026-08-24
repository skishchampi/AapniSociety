from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import AuditEvent, OTPChallenge, User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    ordering = ["-date_joined"]
    list_display = ["phone", "full_name", "primary_role", "is_staff", "date_joined"]
    list_filter = ["primary_role", "is_staff", "is_active"]
    search_fields = ["phone", "full_name", "email"]
    fieldsets = (
        (None, {"fields": ("phone", "password")}),
        ("Profile", {"fields": ("full_name", "email", "primary_role")}),
        (
            "Permissions",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),
        ("Dates", {"fields": ("last_login", "date_joined")}),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("phone", "password1", "password2", "primary_role"),
            },
        ),
    )


@admin.register(OTPChallenge)
class OTPChallengeAdmin(admin.ModelAdmin):
    list_display = ["phone", "purpose", "attempts", "expires_at", "consumed_at", "created_at"]
    list_filter = ["purpose"]
    search_fields = ["phone"]
    readonly_fields = ["code_hash", "created_at"]


@admin.register(AuditEvent)
class AuditEventAdmin(admin.ModelAdmin):
    list_display = ["action", "actor", "target_type", "target_id", "created_at"]
    list_filter = ["action"]
    search_fields = ["action", "target_id"]
    readonly_fields = ["actor", "action", "target_type", "target_id", "metadata", "created_at"]

from django.contrib import admin

from .models import HouseholdProfile, ServiceCategory, WorkerProfile


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

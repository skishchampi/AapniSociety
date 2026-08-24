from django.contrib import admin

from .models import Building, City, Locality, Unit


@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    list_display = ["name", "state", "slug"]
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Locality)
class LocalityAdmin(admin.ModelAdmin):
    list_display = ["name", "city", "slug"]
    list_filter = ["city"]


@admin.register(Building)
class BuildingAdmin(admin.ModelAdmin):
    list_display = ["name", "locality"]
    list_filter = ["locality"]
    search_fields = ["name", "address"]


@admin.register(Unit)
class UnitAdmin(admin.ModelAdmin):
    list_display = ["label", "building"]
    list_filter = ["building"]

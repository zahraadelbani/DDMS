"""Admin for shared models."""

from django.contrib import admin

from .models import Organization, Unit


@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = ("name", "org_type", "is_active")
    list_filter = ("org_type", "is_active")
    search_fields = ("name",)


@admin.register(Unit)
class UnitAdmin(admin.ModelAdmin):
    list_display = ("name", "unit_type", "is_active")
    list_filter = ("unit_type", "is_active")
    search_fields = ("name",)
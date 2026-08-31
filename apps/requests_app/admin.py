"""Admin for activity requests."""

from django.contrib import admin

from .models import ActivityRequest


@admin.register(ActivityRequest)
class ActivityRequestAdmin(admin.ModelAdmin):
    list_display = ("title", "start_date", "end_date", "status", "created_by")
    list_filter = ("status",)
    search_fields = ("title", "description")
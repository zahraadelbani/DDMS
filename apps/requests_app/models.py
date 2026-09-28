"""Activity request model."""

from django.conf import settings
from django.db import models


class ActivityRequest(models.Model):
    class Status(models.TextChoices):
        DRAFT = "DRAFT", "Draft"
        PENDING = "PENDING", "Pending"
        APPROVED = "APPROVED", "Approved"
        REJECTED = "REJECTED", "Rejected"

    title = models.CharField(max_length=255)
    description = models.TextField()
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    expected_participants = models.PositiveIntegerField()
    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.DRAFT
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="activity_requests",
    )
    organization = models.ForeignKey(
        "core.Organization",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="activity_requests",
    )
    unit = models.ForeignKey(
        "core.Unit",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="activity_requests",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def can_be_seen_by(self, user):
        """Every role is written here on purpose, so a new role does not
        get access by accident."""
        from apps.accounts.models import User

        if user.role == User.Roles.REPRESENTATIVE:
            return self.created_by_id == user.id
        if user.role == User.Roles.UNIT_STAFF:
            return self.unit_id is not None and self.unit_id == user.unit_id
        if user.role in (
            User.Roles.DIRECTORATE_STAFF,
            User.Roles.COORDINATOR,
            User.Roles.DIRECTOR,
        ):
            return True
        return False

    def can_be_edited_by(self, user):
        """Only the creator can edit and only while it is still a draft."""
        return self.created_by_id == user.id and self.status == self.Status.DRAFT

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.title
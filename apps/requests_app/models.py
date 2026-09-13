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
        """Representatives only see their own requests. Staff, coordinator
        and director can see all of them."""
        if user.role == "REPRESENTATIVE":
            return self.created_by_id == user.id
        return True

    def can_be_edited_by(self, user):
        """Only the creator can edit and only while it is still a draft."""
        return self.created_by_id == user.id and self.status == self.Status.DRAFT

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.title
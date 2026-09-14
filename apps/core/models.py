"""Shared models for DDMS."""

from django.db import models


class Organization(models.Model):
    """Clubs and societies. They both work the same way so i kept them
    in one table with a type field."""

    class OrgType(models.TextChoices):
        CLUB = "CLUB", "Club"
        SOCIETY = "SOCIETY", "Society"

    name = models.CharField(max_length=255, unique=True)
    org_type = models.CharField(max_length=20, choices=OrgType.choices)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Unit(models.Model):
    """Alumni, Sports and Career units."""

    class UnitType(models.TextChoices):
        ALUMNI = "ALUMNI", "Alumni"
        SPORTS = "SPORTS", "Sports"
        CAREER = "CAREER", "Career"

    name = models.CharField(max_length=255, unique=True)
    unit_type = models.CharField(max_length=20, choices=UnitType.choices)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name
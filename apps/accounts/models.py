"""User model for DDMS."""

from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.core.exceptions import ValidationError
from django.db import models


class UserManager(BaseUserManager):
    """We login with email, so the default manager that wants a
    username does not work for us."""

    use_in_migrations = True

    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Users must have an email address")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):
    class Roles(models.TextChoices):
        REPRESENTATIVE = "REPRESENTATIVE", "Representative"
        DIRECTORATE_STAFF = "DIRECTORATE_STAFF", "Directorate Staff"
        UNIT_STAFF = "UNIT_STAFF", "Unit Staff"
        COORDINATOR = "COORDINATOR", "Coordinator"
        DIRECTOR = "DIRECTOR", "Director"

    username = None
    email = models.EmailField("email address", unique=True)
    role = models.CharField(
        max_length=25, choices=Roles.choices, blank=True
    )

    organization = models.ForeignKey(
        "core.Organization",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="representatives",
    )
    unit = models.ForeignKey(
        "core.Unit",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="staff_members",
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = UserManager()

    def clean(self):
        """A representative needs an organization and no unit, a unit staff
        needs a unit and no organization, the other roles need neither."""
        super().clean()
        errors = {}

        if self.role == self.Roles.REPRESENTATIVE:
            if self.organization is None:
                errors["organization"] = "A representative needs an organization."
            if self.unit is not None:
                errors["unit"] = "A representative cannot have a unit."

        elif self.role == self.Roles.UNIT_STAFF:
            if self.unit is None:
                errors["unit"] = "A unit staff needs a unit."
            if self.organization is not None:
                errors["organization"] = "A unit staff cannot have an organization."

        elif self.role in (
            self.Roles.DIRECTORATE_STAFF,
            self.Roles.COORDINATOR,
            self.Roles.DIRECTOR,
        ):
            if self.organization is not None:
                errors["organization"] = "This role cannot have an organization."
            if self.unit is not None:
                errors["unit"] = "This role cannot have a unit."

        elif self.role == "" and not self.is_superuser:
            errors["role"] = "Please choose a role."

        if errors:
            raise ValidationError(errors)

    def __str__(self):
        return self.email
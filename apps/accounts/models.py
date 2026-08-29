"""User model for DDMS."""

from django.contrib.auth.models import AbstractUser, BaseUserManager
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
        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):
    class Roles(models.TextChoices):
        REPRESENTATIVE = "REPRESENTATIVE", "Club / Society Representative"
        COORDINATOR = "COORDINATOR", "Sports Affairs"
        DIRECTOR = "DIRECTOR", "Activity Directorate"
        STAFF = "STAFF", "Rectorate / Staff"

    username = None
    email = models.EmailField("email address", unique=True)
    role = models.CharField(max_length=25, choices=Roles.choices)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = UserManager()

    def __str__(self):
        return self.email
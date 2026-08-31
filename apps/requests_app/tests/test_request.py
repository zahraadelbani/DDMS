"""Tests for login, activity requests and validation."""

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from apps.requests_app.models import ActivityRequest

User = get_user_model()


class LoginTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="rep@emu.edu.tr", password="testpass123", role=User.Roles.REPRESENTATIVE
        )

    def test_login_with_correct_password(self):
        response = self.client.post(
            reverse("accounts:login"),
            {"username": "rep@emu.edu.tr", "password": "testpass123"},
        )
        self.assertEqual(response.status_code, 302)

    def test_login_with_wrong_password(self):
        response = self.client.post(
            reverse("accounts:login"),
            {"username": "rep@emu.edu.tr", "password": "wrongpass"},
        )
        self.assertEqual(response.status_code, 200)

    def test_request_list_needs_login(self):
        response = self.client.get(reverse("core:representative_view_requests"))
        self.assertEqual(response.status_code, 302)


class ActivityRequestTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="rep@emu.edu.tr", password="testpass123", role=User.Roles.REPRESENTATIVE
        )
        self.client.login(username="rep@emu.edu.tr", password="testpass123")
        self.start = timezone.now() + timezone.timedelta(days=7)
        self.end = self.start + timezone.timedelta(hours=3)

    def form_data(self, **overrides):
        data = {
            "title": "Robotics Workshop",
            "description": "A short workshop for club members.",
            "start_date": self.start.strftime("%Y-%m-%dT%H:%M"),
            "end_date": self.end.strftime("%Y-%m-%dT%H:%M"),
            "expected_participants": 40,
        }
        data.update(overrides)
        return data

    def test_create_request(self):
        self.client.post(reverse("requests_app:create_request"), self.form_data())
        self.assertEqual(ActivityRequest.objects.count(), 1)
        created = ActivityRequest.objects.first()
        self.assertEqual(created.title, "Robotics Workshop")
        self.assertEqual(created.created_by, self.user)

    def test_end_date_must_be_after_start_date(self):
        data = self.form_data(
            end_date=(self.start - timezone.timedelta(hours=1)).strftime("%Y-%m-%dT%H:%M")
        )
        self.client.post(reverse("requests_app:create_request"), data)
        self.assertEqual(ActivityRequest.objects.count(), 0)

    def test_participants_must_be_greater_than_zero(self):
        self.client.post(
            reverse("requests_app:create_request"), self.form_data(expected_participants=0)
        )
        self.assertEqual(ActivityRequest.objects.count(), 0)

    def test_list_shows_own_requests(self):
        ActivityRequest.objects.create(
            title="Robotics Workshop",
            description="A short workshop.",
            start_date=self.start,
            end_date=self.end,
            expected_participants=40,
            created_by=self.user,
        )
        response = self.client.get(reverse("core:representative_view_requests"))
        self.assertContains(response, "Robotics Workshop")
"""Tests for roles, organizations, ownership and editing."""

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from apps.core.models import Organization, Unit
from apps.requests_app.models import ActivityRequest

User = get_user_model()


class BaseSetUp(TestCase):
    def setUp(self):
        self.club = Organization.objects.create(
            name="Robotics Club", org_type=Organization.OrgType.CLUB
        )
        self.other_club = Organization.objects.create(
            name="Debate Club", org_type=Organization.OrgType.CLUB
        )
        self.sports_unit = Unit.objects.create(
            name="Sports Unit", unit_type=Unit.UnitType.SPORTS
        )

        self.rep = User.objects.create_user(
            email="rep@emu.edu.tr",
            password="testpass123",
            role=User.Roles.REPRESENTATIVE,
            organization=self.club,
        )
        self.other_rep = User.objects.create_user(
            email="rep2@emu.edu.tr",
            password="testpass123",
            role=User.Roles.REPRESENTATIVE,
            organization=self.other_club,
        )
        self.unit_staff = User.objects.create_user(
            email="unitstaff@emu.edu.tr",
            password="testpass123",
            role=User.Roles.UNIT_STAFF,
            unit=self.sports_unit,
        )
        self.director = User.objects.create_user(
            email="director@emu.edu.tr",
            password="testpass123",
            role=User.Roles.DIRECTOR,
        )

        self.start = timezone.now() + timezone.timedelta(days=7)
        self.end = self.start + timezone.timedelta(hours=3)

    def make_request(self, user, status=ActivityRequest.Status.DRAFT):
        return ActivityRequest.objects.create(
            title="Test Activity",
            description="A test activity.",
            start_date=self.start,
            end_date=self.end,
            expected_participants=30,
            status=status,
            created_by=user,
            organization=user.organization,
            unit=user.unit,
        )


class RoleBasedAccessTests(BaseSetUp):
    def test_representative_cannot_open_director_dashboard(self):
        self.client.login(username="rep@emu.edu.tr", password="testpass123")
        response = self.client.get(reverse("core:director_dashboard"))
        self.assertEqual(response.status_code, 403)

    def test_representative_cannot_open_staff_dashboard(self):
        self.client.login(username="rep@emu.edu.tr", password="testpass123")
        response = self.client.get(reverse("core:staff_dashboard"))
        self.assertEqual(response.status_code, 403)

    def test_staff_cannot_open_coordinator_dashboard(self):
        self.client.login(username="unitstaff@emu.edu.tr", password="testpass123")
        response = self.client.get(reverse("core:coordinator_dashboard"))
        self.assertEqual(response.status_code, 403)

    def test_representative_can_open_own_dashboard(self):
        self.client.login(username="rep@emu.edu.tr", password="testpass123")
        response = self.client.get(reverse("core:representative_dashboard"))
        self.assertEqual(response.status_code, 200)


class OrganizationUnitTests(BaseSetUp):
    def test_representative_belongs_to_organization(self):
        self.assertEqual(self.rep.organization, self.club)
        self.assertIsNone(self.rep.unit)

    def test_unit_staff_belongs_to_unit(self):
        self.assertEqual(self.unit_staff.unit, self.sports_unit)
        self.assertIsNone(self.unit_staff.organization)

    def test_request_gets_the_organization_of_the_creator(self):
        self.client.login(username="rep@emu.edu.tr", password="testpass123")
        self.client.post(
            reverse("requests_app:create_request"),
            {
                "title": "Workshop",
                "description": "A workshop.",
                "start_date": self.start.strftime("%Y-%m-%dT%H:%M"),
                "end_date": self.end.strftime("%Y-%m-%dT%H:%M"),
                "expected_participants": 20,
            },
        )
        created = ActivityRequest.objects.get(title="Workshop")
        self.assertEqual(created.organization, self.club)
        self.assertIsNone(created.unit)


class OwnershipTests(BaseSetUp):
    def test_representative_only_sees_own_requests(self):
        self.make_request(self.rep)
        other = self.make_request(self.other_rep)
        self.client.login(username="rep@emu.edu.tr", password="testpass123")
        response = self.client.get(reverse("requests_app:request_list"))
        self.assertNotContains(response, f"REQ-{other.pk}")

    def test_director_sees_all_requests(self):
        self.make_request(self.rep)
        self.make_request(self.other_rep)
        self.client.login(username="director@emu.edu.tr", password="testpass123")
        response = self.client.get(reverse("requests_app:request_list"))
        self.assertEqual(len(response.context["requests"]), 2)

    def test_cannot_open_another_users_request(self):
        other = self.make_request(self.other_rep)
        self.client.login(username="rep@emu.edu.tr", password="testpass123")
        response = self.client.get(
            reverse("requests_app:request_detail", args=[other.pk])
        )
        self.assertEqual(response.status_code, 403)

    def test_can_open_own_request(self):
        own = self.make_request(self.rep)
        self.client.login(username="rep@emu.edu.tr", password="testpass123")
        response = self.client.get(
            reverse("requests_app:request_detail", args=[own.pk])
        )
        self.assertEqual(response.status_code, 200)


class EditingTests(BaseSetUp):
    def test_creator_can_edit_a_draft(self):
        own = self.make_request(self.rep)
        self.client.login(username="rep@emu.edu.tr", password="testpass123")
        response = self.client.get(
            reverse("requests_app:edit_request", args=[own.pk])
        )
        self.assertEqual(response.status_code, 200)

    def test_cannot_edit_a_pending_request(self):
        own = self.make_request(self.rep, status=ActivityRequest.Status.PENDING)
        self.client.login(username="rep@emu.edu.tr", password="testpass123")
        response = self.client.get(
            reverse("requests_app:edit_request", args=[own.pk])
        )
        self.assertEqual(response.status_code, 403)

    def test_cannot_edit_another_users_request(self):
        other = self.make_request(self.other_rep)
        self.client.login(username="rep@emu.edu.tr", password="testpass123")
        response = self.client.get(
            reverse("requests_app:edit_request", args=[other.pk])
        )
        self.assertEqual(response.status_code, 403)


class SuperuserTests(TestCase):
    def test_superuser_is_created_with_the_right_flags(self):
        admin = User.objects.create_superuser(
            email="admin@emu.edu.tr", password="testpass123"
        )
        self.assertTrue(admin.is_staff)
        self.assertTrue(admin.is_superuser)
        self.assertEqual(admin.role, User.Roles.DIRECTOR)

    def test_superuser_cannot_be_created_with_is_staff_false(self):
        with self.assertRaises(ValueError):
            User.objects.create_superuser(
                email="admin2@emu.edu.tr", password="testpass123", is_staff=False
            )

    def test_superuser_cannot_be_created_with_is_superuser_false(self):
        with self.assertRaises(ValueError):
            User.objects.create_superuser(
                email="admin3@emu.edu.tr",
                password="testpass123",
                is_superuser=False,
            )
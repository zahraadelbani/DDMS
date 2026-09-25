"""Tests for roles, organizations, ownership, editing and validation."""

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
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
        self.career_unit = Unit.objects.create(
            name="Career Unit", unit_type=Unit.UnitType.CAREER
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
        self.other_unit_staff = User.objects.create_user(
            email="unitstaff2@emu.edu.tr",
            password="testpass123",
            role=User.Roles.UNIT_STAFF,
            unit=self.career_unit,
        )
        self.dir_staff = User.objects.create_user(
            email="staff@emu.edu.tr",
            password="testpass123",
            role=User.Roles.DIRECTORATE_STAFF,
        )
        self.coordinator = User.objects.create_user(
            email="coordinator@emu.edu.tr",
            password="testpass123",
            role=User.Roles.COORDINATOR,
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
        
    def test_unit_staff_cannot_open_manage_users(self):
        self.client.login(username="unitstaff@emu.edu.tr", password="testpass123")
        response = self.client.get(reverse("core:manage_users"))
        self.assertEqual(response.status_code, 403)

    def test_directorate_staff_can_open_manage_users(self):
        self.client.login(username="staff@emu.edu.tr", password="testpass123")
        response = self.client.get(reverse("core:manage_users"))
        self.assertEqual(response.status_code, 200)


class RequestViewAccessTests(BaseSetUp):
    def test_director_cannot_open_the_create_page(self):
        self.client.login(username="director@emu.edu.tr", password="testpass123")
        response = self.client.get(reverse("requests_app:create_request"))
        self.assertEqual(response.status_code, 403)

    def test_coordinator_cannot_open_the_create_page(self):
        self.client.login(
            username="coordinator@emu.edu.tr", password="testpass123"
        )
        response = self.client.get(reverse("requests_app:create_request"))
        self.assertEqual(response.status_code, 403)

    def test_representative_can_open_the_create_page(self):
        self.client.login(username="rep@emu.edu.tr", password="testpass123")
        response = self.client.get(reverse("requests_app:create_request"))
        self.assertEqual(response.status_code, 200)

    def test_director_cannot_open_the_edit_page(self):
        own = self.make_request(self.rep)
        self.client.login(username="director@emu.edu.tr", password="testpass123")
        response = self.client.get(
            reverse("requests_app:edit_request", args=[own.pk])
        )
        self.assertEqual(response.status_code, 403)


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

    def test_directorate_staff_sees_all_requests(self):
        self.make_request(self.rep)
        self.make_request(self.unit_staff)
        self.client.login(username="staff@emu.edu.tr", password="testpass123")
        response = self.client.get(reverse("requests_app:request_list"))
        self.assertEqual(len(response.context["requests"]), 2)

    def test_unit_staff_only_sees_requests_of_its_own_unit(self):
        self.make_request(self.unit_staff)
        self.make_request(self.other_unit_staff)
        self.client.login(
            username="unitstaff@emu.edu.tr", password="testpass123"
        )
        response = self.client.get(reverse("requests_app:request_list"))
        self.assertEqual(len(response.context["requests"]), 1)

    def test_unit_staff_cannot_open_a_request_of_another_unit(self):
        other = self.make_request(self.other_unit_staff)
        self.client.login(
            username="unitstaff@emu.edu.tr", password="testpass123"
        )
        response = self.client.get(
            reverse("requests_app:request_detail", args=[other.pk])
        )
        self.assertEqual(response.status_code, 403)

    def test_unit_staff_cannot_open_a_club_request(self):
        club_request = self.make_request(self.rep)
        self.client.login(
            username="unitstaff@emu.edu.tr", password="testpass123"
        )
        response = self.client.get(
            reverse("requests_app:request_detail", args=[club_request.pk])
        )
        self.assertEqual(response.status_code, 403)

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


class UserValidationTests(BaseSetUp):
    def make_user(self, **fields):
        user = User(**fields)
        user.set_password("testpass123")
        return user

    def assert_invalid(self, user, field):
        with self.assertRaises(ValidationError) as error:
            user.full_clean()
        self.assertIn(field, error.exception.message_dict)

    def test_representative_without_an_organization_is_not_valid(self):
        user = self.make_user(
            email="bad1@emu.edu.tr", role=User.Roles.REPRESENTATIVE
        )
        self.assert_invalid(user, "organization")

    def test_representative_with_a_unit_is_not_valid(self):
        user = self.make_user(
            email="bad2@emu.edu.tr",
            role=User.Roles.REPRESENTATIVE,
            organization=self.club,
            unit=self.sports_unit,
        )
        self.assert_invalid(user, "unit")

    def test_unit_staff_without_a_unit_is_not_valid(self):
        user = self.make_user(
            email="bad3@emu.edu.tr", role=User.Roles.UNIT_STAFF
        )
        self.assert_invalid(user, "unit")

    def test_unit_staff_with_an_organization_is_not_valid(self):
        user = self.make_user(
            email="bad4@emu.edu.tr",
            role=User.Roles.UNIT_STAFF,
            unit=self.sports_unit,
            organization=self.club,
        )
        self.assert_invalid(user, "organization")

    def test_coordinator_with_an_organization_is_not_valid(self):
        user = self.make_user(
            email="bad5@emu.edu.tr",
            role=User.Roles.COORDINATOR,
            organization=self.club,
        )
        self.assert_invalid(user, "organization")

    def test_a_correct_representative_is_valid(self):
        user = self.make_user(
            email="good1@emu.edu.tr",
            role=User.Roles.REPRESENTATIVE,
            organization=self.club,
        )
        user.full_clean()

    def test_a_correct_unit_staff_is_valid(self):
        user = self.make_user(
            email="good2@emu.edu.tr",
            role=User.Roles.UNIT_STAFF,
            unit=self.sports_unit,
        )
        user.full_clean()


class SuperuserTests(TestCase):
    def test_superuser_is_created_with_the_right_flags(self):
        admin = User.objects.create_superuser(
            email="admin@emu.edu.tr", password="testpass123"
        )
        self.assertTrue(admin.is_staff)
        self.assertTrue(admin.is_superuser)

    def test_superuser_does_not_get_a_role(self):
        admin = User.objects.create_superuser(
            email="admin4@emu.edu.tr", password="testpass123"
        )
        self.assertEqual(admin.role, "")

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
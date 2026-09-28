"""Tests for cross role access, unauthorized URLs, the sidebar and login redirects."""

from django.test import TestCase
from django.urls import reverse

from apps.accounts.models import User
from apps.requests_app.models import ActivityRequest

from .test_week3 import BaseSetUp

PASSWORD = "testpass123"

# which roles are allowed to open each page, everybody else should get 403
PAGE_ACCESS = {
    "core:representative_dashboard": [User.Roles.REPRESENTATIVE],
    "core:representative_submit_request": [User.Roles.REPRESENTATIVE],
    "core:representative_view_requests": [User.Roles.REPRESENTATIVE],
    "core:staff_dashboard": [User.Roles.DIRECTORATE_STAFF, User.Roles.UNIT_STAFF],
    "core:staff_view_requests": [User.Roles.DIRECTORATE_STAFF, User.Roles.UNIT_STAFF],
    "core:manage_users": [User.Roles.DIRECTORATE_STAFF],
    "core:coordinator_dashboard": [User.Roles.COORDINATOR],
    "core:coordinator_view_requests": [User.Roles.COORDINATOR],
    "core:coordinator_manage_users": [User.Roles.COORDINATOR],
    "core:director_dashboard": [User.Roles.DIRECTOR],
    "core:director_view_requests": [User.Roles.DIRECTOR],
}


class CrossRoleAccessTests(BaseSetUp):
    def users_by_role(self):
        return {
            User.Roles.REPRESENTATIVE: self.rep,
            User.Roles.DIRECTORATE_STAFF: self.dir_staff,
            User.Roles.UNIT_STAFF: self.unit_staff,
            User.Roles.COORDINATOR: self.coordinator,
            User.Roles.DIRECTOR: self.director,
        }

    def test_every_role_on_every_dashboard_page(self):
        for role, user in self.users_by_role().items():
            self.client.force_login(user)
            for url_name, allowed_roles in PAGE_ACCESS.items():
                with self.subTest(role=role, page=url_name):
                    response = self.client.get(reverse(url_name))
                    expected = 200 if role in allowed_roles else 403
                    self.assertEqual(response.status_code, expected)

    def test_every_role_can_open_profile(self):
        for role, user in self.users_by_role().items():
            self.client.force_login(user)
            with self.subTest(role=role):
                response = self.client.get(reverse("core:profile"))
                self.assertEqual(response.status_code, 200)

    def test_unit_staff_cannot_edit_a_request_of_another_unit(self):
        other = self.make_request(self.other_unit_staff)
        self.client.force_login(self.unit_staff)
        response = self.client.get(
            reverse("requests_app:edit_request", args=[other.pk])
        )
        self.assertEqual(response.status_code, 403)

    def test_unit_staff_can_edit_its_own_draft(self):
        own = self.make_request(self.unit_staff)
        self.client.force_login(self.unit_staff)
        response = self.client.get(
            reverse("requests_app:edit_request", args=[own.pk])
        )
        self.assertEqual(response.status_code, 200)

    def test_coordinator_and_director_can_open_any_request(self):
        club_request = self.make_request(self.rep)
        for user in (self.coordinator, self.director, self.dir_staff):
            self.client.force_login(user)
            with self.subTest(user=user.email):
                response = self.client.get(
                    reverse("requests_app:request_detail", args=[club_request.pk])
                )
                self.assertEqual(response.status_code, 200)


class UnauthorizedUrlTests(BaseSetUp):
    def test_logged_out_user_is_sent_to_login_from_every_page(self):
        own = self.make_request(self.rep)
        url_names = list(PAGE_ACCESS) + ["core:profile"]
        urls = [reverse(name) for name in url_names] + [
            reverse("requests_app:request_list"),
            reverse("requests_app:create_request"),
            reverse("requests_app:request_detail", args=[own.pk]),
            reverse("requests_app:edit_request", args=[own.pk]),
        ]
        for url in urls:
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertEqual(response.status_code, 302)
                self.assertTrue(response.url.startswith(reverse("accounts:login")))

    def test_request_that_does_not_exist_gives_404(self):
        self.client.force_login(self.director)
        response = self.client.get(
            reverse("requests_app:request_detail", args=[99999])
        )
        self.assertEqual(response.status_code, 404)

    def test_posting_to_another_users_edit_page_does_not_change_it(self):
        other = self.make_request(self.other_rep)
        self.client.force_login(self.rep)
        self.client.post(
            reverse("requests_app:edit_request", args=[other.pk]),
            {
                "title": "Changed",
                "description": "Changed.",
                "start_date": self.start.strftime("%Y-%m-%dT%H:%M"),
                "end_date": self.end.strftime("%Y-%m-%dT%H:%M"),
                "expected_participants": 5,
            },
        )
        other.refresh_from_db()
        self.assertEqual(other.title, "Test Activity")


class SidebarTests(BaseSetUp):
    def label(self, name):
        return f'<p class="sidebar-nav-label">{name}</p>'

    def sidebar(self, response):
        # only the left menu, not the page content under it
        html = response.content.decode()
        start = html.index('<nav class="sidebar-nav"')
        end = html.index("</nav>", start)
        return html[start:end]

    def test_representative_only_sees_its_own_section(self):
        self.client.force_login(self.rep)
        menu = self.sidebar(self.client.get(reverse("core:representative_dashboard")))
        self.assertIn(self.label("Representative"), menu)
        for other in ("Staff", "Coordinator", "Director"):
            self.assertNotIn(self.label(other), menu)

    def test_director_only_sees_its_own_section(self):
        self.client.force_login(self.director)
        menu = self.sidebar(self.client.get(reverse("core:director_dashboard")))
        self.assertIn(self.label("Director"), menu)
        for other in ("Representative", "Staff", "Coordinator"):
            self.assertNotIn(self.label(other), menu)

    def test_unit_staff_does_not_see_manage_users(self):
        self.client.force_login(self.unit_staff)
        menu = self.sidebar(self.client.get(reverse("core:staff_dashboard")))
        self.assertIn(self.label("Staff"), menu)
        self.assertNotIn(reverse("core:manage_users"), menu)

    def test_directorate_staff_sees_manage_users(self):
        self.client.force_login(self.dir_staff)
        menu = self.sidebar(self.client.get(reverse("core:staff_dashboard")))
        self.assertIn(reverse("core:manage_users"), menu)
        
class LoginRedirectTests(BaseSetUp):
    def login(self, email, next_url=None):
        url = reverse("accounts:login")
        data = {"username": email, "password": PASSWORD}
        if next_url:
            data["next"] = next_url
        return self.client.post(url, data)

    def test_each_role_goes_to_its_own_dashboard(self):
        expected = {
            "rep@emu.edu.tr": "core:representative_dashboard",
            "staff@emu.edu.tr": "core:staff_dashboard",
            "unitstaff@emu.edu.tr": "core:staff_dashboard",
            "coordinator@emu.edu.tr": "core:coordinator_dashboard",
            "director@emu.edu.tr": "core:director_dashboard",
        }
        for email, url_name in expected.items():
            with self.subTest(email=email):
                self.client.logout()
                response = self.login(email)
                self.assertRedirects(
                    response, reverse(url_name), fetch_redirect_response=False
                )

    def test_next_still_wins_over_the_dashboard(self):
        target = reverse("requests_app:request_list")
        response = self.login("rep@emu.edu.tr", next_url=target)
        self.assertRedirects(response, target, fetch_redirect_response=False)

    def test_superuser_without_a_role_goes_to_admin(self):
        User.objects.create_superuser(email="admin@emu.edu.tr", password=PASSWORD)
        response = self.login("admin@emu.edu.tr")
        self.assertRedirects(
            response, reverse("admin:index"), fetch_redirect_response=False
        )
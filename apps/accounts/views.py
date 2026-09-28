"""Login and logout views."""

from django.contrib.auth.views import LoginView, LogoutView
from django.urls import reverse

from .models import User

DASHBOARD_BY_ROLE = {
    User.Roles.REPRESENTATIVE: "core:representative_dashboard",
    User.Roles.DIRECTORATE_STAFF: "core:staff_dashboard",
    User.Roles.UNIT_STAFF: "core:staff_dashboard",
    User.Roles.COORDINATOR: "core:coordinator_dashboard",
    User.Roles.DIRECTOR: "core:director_dashboard",
}


class DDMSLoginView(LoginView):
    template_name = "accounts/login.html"

    def get_success_url(self):
        # if the user was trying to open a page before login, send them back there
        next_url = self.get_redirect_url()
        if next_url:
            return next_url

        user = self.request.user
        if user.role in DASHBOARD_BY_ROLE:
            return reverse(DASHBOARD_BY_ROLE[user.role])
        if user.is_superuser:
            return reverse("admin:index")
        return reverse("core:profile")


class DDMSLogoutView(LogoutView):
    pass
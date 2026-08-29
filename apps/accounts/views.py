"""Login and logout views."""

from django.contrib.auth.views import LoginView, LogoutView


class DDMSLoginView(LoginView):
    template_name = "accounts/login.html"
    redirect_authenticated_user = True


class DDMSLogoutView(LogoutView):
    pass
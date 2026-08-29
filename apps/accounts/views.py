"""Login and logout views."""

from django.contrib.auth.views import LoginView, LogoutView


class DDMSLoginView(LoginView):
    template_name = "accounts/login.html"
    


class DDMSLogoutView(LogoutView):
    pass
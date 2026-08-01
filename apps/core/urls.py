from django.urls import path
from django.views.generic import TemplateView
from .views import (
    submit_request,
    view_requests,
    manage_users,
    staff_view_requests,
    coordinator_view_requests,
    representative_dashboard,
    staff_dashboard,
    coordinator_dashboard,
    coordinator_manage_users,
    director_dashboard,
    director_view_requests,
    profile,
)


app_name = "core"
urlpatterns = [
    path("representative/dashboard/", representative_dashboard, name="representative_dashboard"),
    path("representative/submit_request/", submit_request, name="representative_submit_request"),
    path("representative/view_requests/", view_requests, name="representative_view_requests"),
    path("staff/dashboard/", staff_dashboard, name="staff_dashboard"),
    path("staff/view_requests/", staff_view_requests, name="staff_view_requests"),
    path("staff/manage_users/", manage_users, name="manage_users"),
    path("coordinator/dashboard/", coordinator_dashboard, name="coordinator_dashboard"),
    path("coordinator/view_requests/", coordinator_view_requests, name="coordinator_view_requests"),
    path("coordinator/manage_users/", coordinator_manage_users, name="coordinator_manage_users"),
    path("director/dashboard/", director_dashboard, name="director_dashboard"),
    path("director/view_requests/", director_view_requests, name="director_view_requests"),
    path("profile/", profile, name="profile"),
    path("", TemplateView.as_view(template_name="accounts/login.html"), name="login"),
]

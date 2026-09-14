from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from apps.accounts.models import User
from apps.requests_app.models import ActivityRequest

from .decorators import role_required

STAFF_ROLES = (User.Roles.DIRECTORATE_STAFF, User.Roles.UNIT_STAFF)


@login_required
@role_required(User.Roles.REPRESENTATIVE)
def submit_request(request):
    return render(request, "representative/submit_request.html")


@login_required
@role_required(User.Roles.REPRESENTATIVE)
def view_requests(request):
    activity_requests = ActivityRequest.objects.filter(created_by=request.user)
    status = request.GET.get("status")
    if status:
        activity_requests = activity_requests.filter(status=status.upper())
    return render(
        request,
        "representative/view_requests.html",
        {
            "activity_requests": activity_requests,
            "active_filter": status or "all",
        },
    )


@login_required
@role_required(*STAFF_ROLES)
def manage_users(request):
    return render(request, "staff/manage_users.html")


@login_required
@role_required(*STAFF_ROLES)
def staff_view_requests(request):
    return render(request, "staff/view_requests.html")


@login_required
@role_required(User.Roles.COORDINATOR)
def coordinator_view_requests(request):
    return render(request, "coordinator/view_requests.html")


@login_required
@role_required(User.Roles.REPRESENTATIVE)
def representative_dashboard(request):
    return render(request, "representative/dashboard.html")


@login_required
@role_required(*STAFF_ROLES)
def staff_dashboard(request):
    return render(request, "staff/dashboard.html")


@login_required
@role_required(User.Roles.COORDINATOR)
def coordinator_dashboard(request):
    return render(request, "coordinator/dashboard.html")


@login_required
@role_required(User.Roles.COORDINATOR)
def coordinator_manage_users(request):
    return render(request, "coordinator/manage_users.html")


@login_required
@role_required(User.Roles.DIRECTOR)
def director_dashboard(request):
    return render(request, "director/dashboard.html")


@login_required
@role_required(User.Roles.DIRECTOR)
def director_view_requests(request):
    return render(request, "director/view_requests.html")


@login_required
def profile(request):
    return render(request, "profile.html")
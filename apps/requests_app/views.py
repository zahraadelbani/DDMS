"""Views for activity requests."""

from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, redirect, render

from apps.accounts.models import User
from apps.core.decorators import role_required

from .forms import ActivityRequestForm
from .models import ActivityRequest


@login_required
@role_required(User.Roles.REPRESENTATIVE, User.Roles.UNIT_STAFF)
def create_request(request):
    if request.method == "POST":
        form = ActivityRequestForm(request.POST)
        if form.is_valid():
            activity_request = form.save(commit=False)
            activity_request.created_by = request.user
            activity_request.organization = request.user.organization
            activity_request.unit = request.user.unit
            activity_request.save()
            return redirect("requests_app:request_list")
    else:
        form = ActivityRequestForm()
    return render(request, "requests_app/create_request.html", {"form": form})


@login_required
def request_list(request):
    requests = ActivityRequest.objects.select_related(
        "created_by", "organization", "unit"
    )
    if request.user.role == User.Roles.REPRESENTATIVE:
        requests = requests.filter(created_by=request.user)
    elif request.user.role == User.Roles.UNIT_STAFF:
        requests = requests.filter(unit=request.user.unit)
    elif request.user.role not in (
        User.Roles.DIRECTORATE_STAFF,
        User.Roles.COORDINATOR,
        User.Roles.DIRECTOR,
    ):
        requests = requests.none()
    return render(
        request, "requests_app/request_list.html", {"requests": requests}
    )


@login_required
def request_detail(request, pk):
    activity_request = get_object_or_404(
        ActivityRequest.objects.select_related(
            "created_by", "organization", "unit"
        ),
        pk=pk,
    )
    if not activity_request.can_be_seen_by(request.user):
        raise PermissionDenied
    return render(
        request,
        "requests_app/request_detail.html",
        {
            "activity_request": activity_request,
            "can_edit": activity_request.can_be_edited_by(request.user),
        },
    )


@login_required
@role_required(User.Roles.REPRESENTATIVE, User.Roles.UNIT_STAFF)
def edit_request(request, pk):
    activity_request = get_object_or_404(ActivityRequest, pk=pk)
    if not activity_request.can_be_edited_by(request.user):
        raise PermissionDenied
    if request.method == "POST":
        form = ActivityRequestForm(request.POST, instance=activity_request)
        if form.is_valid():
            form.save()
            return redirect("requests_app:request_detail", pk=activity_request.pk)
    else:
        form = ActivityRequestForm(instance=activity_request)
    return render(
        request,
        "requests_app/edit_request.html",
        {"form": form, "activity_request": activity_request},
    )
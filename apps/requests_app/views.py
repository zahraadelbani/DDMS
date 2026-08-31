"""Views for activity requests."""

from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from .forms import ActivityRequestForm
from .models import ActivityRequest


@login_required
def create_request(request):
    if request.method == "POST":
        form = ActivityRequestForm(request.POST)
        if form.is_valid():
            activity_request = form.save(commit=False)
            activity_request.created_by = request.user
            activity_request.save()
            return redirect("requests_app:request_list")
    else:
        form = ActivityRequestForm()
    return render(request, "requests_app/create_request.html", {"form": form})


@login_required
def request_list(request):
    requests = ActivityRequest.objects.select_related("created_by")
    return render(
        request, "requests_app/request_list.html", {"requests": requests}
    )
from django.shortcuts import render


def submit_request(request):
    return render(request, "representative/submit_request.html")


def view_requests(request):
    return render(request, "representative/view_requests.html")


def manage_users(request):
    return render(request, "staff/manage_users.html")


def staff_view_requests(request):
    return render(request, "staff/view_requests.html")


def coordinator_view_requests(request):
    return render(request, "coordinator/view_requests.html")


def representative_dashboard(request):
    return render(request, "representative/dashboard.html")


def staff_dashboard(request):
    return render(request, "staff/dashboard.html")


def coordinator_dashboard(request):
    return render(request, "coordinator/dashboard.html")


def coordinator_manage_users(request):
    return render(request, "coordinator/manage_users.html")


def director_dashboard(request):
    return render(request, "director/dashboard.html")


def director_view_requests(request):
    return render(request, "director/view_requests.html")


def profile(request):
    return render(request, "profile.html")

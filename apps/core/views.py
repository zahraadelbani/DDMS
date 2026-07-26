from django.shortcuts import render


def home(request):
    """Render the project verification page."""
    return render(request, "home.html")

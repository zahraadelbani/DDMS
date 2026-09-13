from django.urls import path

from .views import create_request, request_detail, request_list

app_name = "requests_app"

urlpatterns = [
    path("requests/new/", create_request, name="create_request"),
    path("requests/<int:pk>/", request_detail, name="request_detail"),
    path("requests/", request_list, name="request_list"),
]
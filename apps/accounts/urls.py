from django.urls import path

from .views import DDMSLoginView, DDMSLogoutView

app_name = "accounts"

urlpatterns = [
    path("", DDMSLoginView.as_view(), name="login"),
    path("logout/", DDMSLogoutView.as_view(), name="logout"),
]
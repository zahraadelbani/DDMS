"""Forms for activity requests."""

from django import forms

from .models import ActivityRequest


class ActivityRequestForm(forms.ModelForm):
    class Meta:
        model = ActivityRequest
        fields = [
            "title",
            "description",
            "start_date",
            "end_date",
            "expected_participants",
        ]
        widgets = {
            "start_date": forms.DateTimeInput(
                attrs={"type": "datetime-local"}, format="%Y-%m-%dT%H:%M"
            ),
            "end_date": forms.DateTimeInput(
                attrs={"type": "datetime-local"}, format="%Y-%m-%dT%H:%M"
            ),
            "description": forms.Textarea(attrs={"rows": 4}),
        }
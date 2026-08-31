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

    def clean_expected_participants(self):
        participants = self.cleaned_data["expected_participants"]
        if participants < 1:
            raise forms.ValidationError(
                "Expected participants must be greater than 0."
            )
        return participants

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get("start_date")
        end_date = cleaned_data.get("end_date")
        if start_date and end_date and end_date <= start_date:
            raise forms.ValidationError(
                "End date must be after the start date."
            )
        return cleaned_data
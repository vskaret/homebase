from django import forms
from .models import Task


class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = [
            "name",
            "notes",
            "season",
            "month",
            "day",
        ]
        widgets = {
            "name": forms.TextInput(
                attrs={
                    "class": "uk-input",
                    "placeholder": "Hva skal gjøres?",
                    "autofocus": "autofocus",
                }
            ),
            "notes": forms.Textarea(
                attrs={
                    "class": "uk-textarea",
                    "rows": 3,
                    "placeholder": "Eventuelle detaljer/notater",
                }
            ),
            "season": forms.Select(
                attrs={
                    "class": "uk-select",
                }
            ),
            "month": forms.NumberInput(
                attrs={
                    "class": "uk-input",
                    "min": 1,
                    "max": 12,
                    "placeholder": "1-12",
                }
            ),
            "day": forms.NumberInput(
                attrs={
                    "class": "uk-input",
                    "min": 1,
                    "max": 31,
                    "placeholder": "1-31",
                }
            ),
        }

    def clean(self):
        cleaned = super().clean()
        # Let the model handle the heavy validation
        task = Task(**{k: cleaned.get(k) for k in ["name", "notes", "season", "month", "day"]})
        try:
            task.clean()
        except Exception as e:  # Convert model ValidationError into form error
            self.add_error(None, e)
        return cleaned

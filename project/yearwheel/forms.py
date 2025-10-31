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
        base_input = "block w-full rounded border border-gray-300 bg-white px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
        widgets = {
            "name": forms.TextInput(
                attrs={
                    "class": base_input,
                    "placeholder": "Hva skal gjøres?",
                    "autofocus": "autofocus",
                }
            ),
            "notes": forms.Textarea(
                attrs={
                    "class": base_input,
                    "rows": 3,
                    "placeholder": "Eventuelle detaljer/notater",
                }
            ),
            "season": forms.Select(
                attrs={
                    "class": base_input,
                }
            ),
            "month": forms.NumberInput(
                attrs={
                    "class": base_input,
                    "min": 1,
                    "max": 12,
                    "placeholder": "1-12",
                }
            ),
            "day": forms.NumberInput(
                attrs={
                    "class": base_input,
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

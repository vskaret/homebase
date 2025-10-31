from django import forms
from .models import Task


class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = [
            "name",
            "notes",
            "month",
            "day",
            "weekday",
            "week_rank",
            "recurrence",
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
            "weekday": forms.Select(
                choices=[
                    ("", "— Velg —"),
                    (0, "Mandag"),
                    (1, "Tirsdag"),
                    (2, "Onsdag"),
                    (3, "Torsdag"),
                    (4, "Fredag"),
                    (5, "Lørdag"),
                    (6, "Søndag"),
                ],
                attrs={"class": base_input},
            ),
            "week_rank": forms.Select(
                choices=[("", "— Velg —")] + list(Task.WeekRank.choices),
                attrs={"class": base_input},
            ),
            "recurrence": forms.Select(
                choices=Task.Recurrence.choices,
                attrs={"class": base_input},
            ),
        }

    # Rely on ModelForm's built-in model validation to avoid duplicate errors

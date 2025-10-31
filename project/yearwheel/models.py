from django.db import models
from django.core.exceptions import ValidationError


class Task(models.Model):
    class Season(models.TextChoices):
        SPRING = "spring", "Vår"
        SUMMER = "summer", "Sommer"
        AUTUMN = "autumn", "Høst"
        WINTER = "winter", "Vinter"

    name = models.CharField(max_length=200)
    notes = models.TextField(blank=True)

    # Exact date within a year (optional)
    month = models.PositiveSmallIntegerField(null=True, blank=True)
    day = models.PositiveSmallIntegerField(null=True, blank=True)

    # Broad seasonal timing (optional)
    season = models.CharField(
        max_length=10, choices=Season.choices, blank=True, default=""
    )

    # Soft delete flags
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["season", "month", "day", "name"]

    def __str__(self) -> str:  # pragma: no cover - trivial
        when = self.human_when()
        return f"{self.name} ({when})" if when else self.name

    def clean(self):
        # At least one of (season) or (month & day) must be provided
        if not self.season and not (self.month and self.day):
            raise ValidationError(
                "Provide either a season or a specific month and day for the task."
            )

        # If only one of month/day is provided, it's invalid
        if (self.month and not self.day) or (self.day and not self.month):
            raise ValidationError("Both month and day must be provided for a date.")

        # Validate ranges
        if self.month and (self.month < 1 or self.month > 12):
            raise ValidationError("Month must be between 1 and 12.")
        if self.day and (self.day < 1 or self.day > 31):
            raise ValidationError("Day must be between 1 and 31.")

        # If exact date exists and no explicit season, derive season
        if self.month and self.day and not self.season:
            self.season = self.derive_season(self.month)

    @staticmethod
    def derive_season(month: int) -> str:
        # Northern hemisphere seasons by meteorological convention
        if month in (3, 4, 5):
            return Task.Season.SPRING
        if month in (6, 7, 8):
            return Task.Season.SUMMER
        if month in (9, 10, 11):
            return Task.Season.AUTUMN
        return Task.Season.WINTER

    def human_when(self) -> str:
        # Friendly representation of timing
        if self.month and self.day:
            return f"{self.day:02d}.{self.month:02d} ({self.get_season_display()})"
        if self.season:
            return self.get_season_display()
        return ""


class TaskDone(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name="done_marks")
    year = models.PositiveIntegerField()
    completed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=("task", "year"), name="unique_task_year_done"),
        ]

    def __str__(self) -> str:  # pragma: no cover - trivial
        return f"{self.task.name} done in {self.year}"
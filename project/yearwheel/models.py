from django.db import models
from django.core.exceptions import ValidationError
import calendar


class Task(models.Model):
    class Season(models.TextChoices):
        SPRING = "spring", "Vår"
        SUMMER = "summer", "Sommer"
        AUTUMN = "autumn", "Høst"
        WINTER = "winter", "Vinter"

    class WeekRank(models.TextChoices):
        FIRST = "1", "Første"
        SECOND = "2", "Andre"
        THIRD = "3", "Tredje"
        FOURTH = "4", "Fjerde"
        LAST = "last", "Siste"

    class Recurrence(models.TextChoices):
        YEARLY = "yearly", "Årlig"
        SEMIANNUAL = "semiannual", "Halvårlig"
        QUARTERLY = "quarterly", "Kvartalsvis"
        MONTHLY = "monthly", "Månedlig"

    name = models.CharField(max_length=200)
    notes = models.TextField(blank=True)

    # Date-based schedule (optional)
    month = models.PositiveSmallIntegerField(null=True, blank=True)
    day = models.PositiveSmallIntegerField(null=True, blank=True)

    # Ordinal weekday-in-month schedule (optional)
    weekday = models.PositiveSmallIntegerField(null=True, blank=True, help_text="0=Mon, 6=Sun")
    week_rank = models.CharField(max_length=5, choices=WeekRank.choices, blank=True, default="")

    # Recurrence across the year (for month-based schedules)
    recurrence = models.CharField(max_length=12, choices=Recurrence.choices, default=Recurrence.YEARLY)

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

    # ---- Helpers for schedule kinds ----
    def uses_exact_date(self) -> bool:
        return bool(self.day) and (
            self.month is not None or self.recurrence in {self.Recurrence.MONTHLY, self.Recurrence.QUARTERLY, self.Recurrence.SEMIANNUAL}
        )

    def uses_weekday_rule(self) -> bool:
        return (
            self.weekday is not None
            and bool(self.week_rank)
            and (self.month is not None or self.recurrence in {self.Recurrence.MONTHLY, self.Recurrence.QUARTERLY, self.Recurrence.SEMIANNUAL})
        )

    def clean(self):
        # At least one of season, exact date, or weekday rule
        if not (self.season or (self.day and (self.month or self.recurrence)) or (self.weekday is not None and self.week_rank and (self.month or self.recurrence))):
            raise ValidationError(
                "Provide either a season, a specific date (day [+ month]), or an ordinal weekday-in-month."
            )

        # Disallow mixing both schedule types simultaneously
        if (self.day and (self.weekday is not None or self.week_rank)):
            raise ValidationError("Choose either exact date or weekday-in-month, not both.")

        # Ranges
        if self.month is not None and (self.month < 1 or self.month > 12):
            raise ValidationError("Month must be between 1 and 12.")
        if self.day is not None and (self.day < 1 or self.day > 31):
            raise ValidationError("Day must be between 1 and 31.")
        if self.weekday is not None and (self.weekday < 0 or self.weekday > 6):
            raise ValidationError("Weekday must be between 0 (Mon) and 6 (Sun).")

        # For yearly recurrence, month is required for month-based schedules
        if self.recurrence == self.Recurrence.YEARLY and (self.day or self.weekday is not None or self.week_rank):
            if not self.month:
                raise ValidationError("A month is required for yearly schedules.")

        # For quarterly recurrence, an anchor month is required (1..12)
        if self.recurrence == self.Recurrence.QUARTERLY:
            if not self.month:
                raise ValidationError("An anchor month is required for quarterly schedules.")
        # For semiannual recurrence, an anchor month is required (1..12)
        if self.recurrence == self.Recurrence.SEMIANNUAL:
            if not self.month:
                raise ValidationError("An anchor month is required for semiannual schedules.")

        # Derive season from month when a month is specified
        if self.month and not self.season:
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
        if self.day:
            if self.recurrence == self.Recurrence.MONTHLY:
                return f"Dag {self.day} hver måned"
            if self.recurrence == self.Recurrence.SEMIANNUAL and self.month:
                return f"Dag {self.day} i måned {self.month} og {((self.month + 5 - 1) % 12) + 1} (halvårlig)"
            if self.recurrence == self.Recurrence.QUARTERLY and self.month:
                return f"Dag {self.day} i {self.month}. måned hvert kvartal"
            if self.month:
                return f"{self.day:02d}.{self.month:02d} ({self.get_season_display()})"
        if self.weekday is not None and self.week_rank:
            weekday_names = ["Mandag", "Tirsdag", "Onsdag", "Torsdag", "Fredag", "Lørdag", "Søndag"]
            rank_labels = {"1": "Første", "2": "Andre", "3": "Tredje", "4": "Fjerde", "last": "Siste"}
            if self.recurrence == self.Recurrence.MONTHLY:
                return f"{rank_labels[self.week_rank]} {weekday_names[self.weekday]} hver måned"
            if self.recurrence == self.Recurrence.SEMIANNUAL and self.month:
                return f"{rank_labels[self.week_rank]} {weekday_names[self.weekday]} i måned {self.month} og {((self.month + 5 - 1) % 12) + 1} (halvårlig)"
            if self.recurrence == self.Recurrence.QUARTERLY and self.month:
                return f"{rank_labels[self.week_rank]} {weekday_names[self.weekday]} i måned {self.month} hvert kvartal"
            if self.month:
                return f"{rank_labels[self.week_rank]} {weekday_names[self.weekday]} i {calendar.month_name[self.month]}"
        if self.season:
            return self.get_season_display()
        return ""

    def _quarter_months(self) -> set[int]:
        if not self.month:
            return set()
        base = self.month
        return {((base - 1 + offset) % 12) + 1 for offset in (0, 3, 6, 9)}

    def _semiannual_months(self) -> set[int]:
        if not self.month:
            return set()
        base = self.month
        return {base, ((base - 1 + 6) % 12) + 1}

    def occurs_in_month(self, year: int, month: int) -> bool:
        if self.recurrence == self.Recurrence.MONTHLY:
            return True
        if self.recurrence == self.Recurrence.QUARTERLY:
            return month in self._quarter_months()
        if self.recurrence == self.Recurrence.SEMIANNUAL:
            return month in self._semiannual_months()
        # yearly
        return self.month == month

    def occurrence_day_in(self, year: int, month: int) -> int | None:
        """
        Returns the day-of-month (1..31) when this task occurs for the given year+month,
        or None if it does not occur in that month. Works for both schedule types.
        """
        if not self.occurs_in_month(year, month):
            return None
        if self.day:
            # Exact day, but if month has fewer days (e.g., 30 vs 31), skip occurrence
            _, last_day = calendar.monthrange(year, month)
            return self.day if self.day <= last_day else None
        if self.weekday is not None and self.week_rank:
            cal = calendar.Calendar(firstweekday=0)
            days = [d for d, wd in cal.itermonthdays2(year, month) if d != 0 and wd == self.weekday]
            if not days:
                return None
            if self.week_rank == Task.WeekRank.LAST:
                return days[-1]
            idx = int(self.week_rank) - 1
            return days[idx] if idx < len(days) else None
        return None


class TaskDone(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name="done_marks")
    year = models.PositiveIntegerField()
    # Per-month completion for recurring schedules
    month = models.PositiveSmallIntegerField(null=True, blank=True)
    completed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=("task", "year", "month"), name="unique_task_year_month_done"),
        ]

    def __str__(self) -> str:  # pragma: no cover - trivial
        return f"{self.task.name} done in {self.year}-{self.month or 0}"
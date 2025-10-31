from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpRequest, HttpResponse, HttpResponseNotAllowed
from django.utils import timezone
import calendar
from .models import Task, TaskDone
from .forms import TaskForm


# Create your views here.
def index(request: HttpRequest) -> HttpResponse:
    # Build calendar for selected month (defaults to current) with tasks per day
    today = timezone.localdate()

    # Read query params year/month; fallback to today
    try:
        year = int(request.GET.get("year") or today.year)
    except (TypeError, ValueError):
        year = today.year
    try:
        month = int(request.GET.get("month") or today.month)
    except (TypeError, ValueError):
        month = today.month
    if not 1 <= month <= 12:
        month = today.month

    cal = calendar.Calendar(firstweekday=0)  # Monday first
    raw_weeks = cal.monthdayscalendar(year, month)  # list of weeks, 0 = out-of-month

    # Fetch tasks for this month that have a specific day
    month_tasks = (
        Task.objects.filter(month=month, day__isnull=False)
        .order_by("day", "name")
    )

    # Load completion state for the selected year
    done_ids = set(
        TaskDone.objects.filter(year=year, task__in=month_tasks).values_list("task_id", flat=True)
    )

    tasks_by_day = {}
    for t in month_tasks:
        # transient attribute for template
        t.is_done = t.id in done_ids
        tasks_by_day.setdefault(t.day, []).append(t)

    # Enrich weeks with tasks per day for easy templating
    weeks = [
        [
            {"day": d, "tasks": (tasks_by_day.get(d, []) if d else [])}
            for d in week
        ]
        for week in raw_weeks
    ]

    # Compute previous and next month/year pairs
    if month == 1:
        prev_year, prev_month = year - 1, 12
    else:
        prev_year, prev_month = year, month - 1
    if month == 12:
        next_year, next_month = year + 1, 1
    else:
        next_year, next_month = year, month + 1

    month_label = timezone.datetime(year, month, 1).strftime("%B")
    weekday_labels = [calendar.day_abbr[(calendar.MONDAY + i) % 7] for i in range(7)]

    context = {
        "today": today,
        "year": year,
        "month": month,
        "month_label": month_label,
        "weeks": weeks,
        "weekday_labels": weekday_labels,
        "prev_year": prev_year,
        "prev_month": prev_month,
        "next_year": next_year,
        "next_month": next_month,
    }
    return render(request, "index.html", context)


def month_list(request: HttpRequest) -> HttpResponse:
    # Determine selected month from query parameter, default to current local month
    try:
        selected_month = int(request.GET.get("month") or 0)
    except ValueError:
        selected_month = 0
    if not 1 <= selected_month <= 12:
        selected_month = timezone.localdate().month

    tasks = Task.objects.filter(month=selected_month).order_by("day", "name")

    # Build month choices 1..12
    month_choices = [
        (i, timezone.datetime(2000, i, 1).strftime("%B")) for i in range(1, 13)
    ]
    month_label = timezone.datetime(2000, selected_month, 1).strftime("%B")

    context = {
        "selected_month": selected_month,
        "tasks": tasks,
        "month_choices": month_choices,
        "month_label": month_label,
    }
    return render(request, "month_list.html", context)


def season_list(request: HttpRequest, season: str) -> HttpResponse:
    # Validate the season key against choices
    season_keys = {choice[0] for choice in Task.Season.choices}
    if season not in season_keys:
        from django.http import HttpResponseNotFound
        return HttpResponseNotFound("Season not found")

    tasks = Task.objects.filter(season=season).order_by("month", "day", "name")
    context = {
        "season": season,
        "season_label": dict(Task.Season.choices)[season],
        "tasks": tasks,
    }
    return render(request, "season_list.html", context)


def task_create(request: HttpRequest) -> HttpResponse:
    if request.method == "POST":
        form = TaskForm(request.POST)
        if form.is_valid():
            task = form.save(commit=False)
            # Ensure model validation runs (ModelForm usually calls full_clean on save, but we enforce)
            task.full_clean()
            task.save()
            return redirect("season", season=task.season or Task.derive_season(task.month))
    else:
        form = TaskForm()

    return render(request, "task_form.html", {"form": form})


def task_toggle_done(request: HttpRequest, task_id: int) -> HttpResponse:
    if request.method != "POST":
        return HttpResponseNotAllowed(["POST"])
    task = get_object_or_404(Task, id=task_id)
    try:
        year = int(request.POST.get("year") or timezone.localdate().year)
    except (TypeError, ValueError):
        year = timezone.localdate().year

    mark, created = TaskDone.objects.get_or_create(task=task, year=year)
    if not created:
        # already exists -> uncheck by deleting
        mark.delete()
        is_done = False
    else:
        is_done = True

    # attach transient flag for rendering
    task.is_done = is_done
    return render(request, "partials/task_checkbox.html", {"task": task, "year": year})

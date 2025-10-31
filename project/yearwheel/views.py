from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpRequest, HttpResponse, HttpResponseNotAllowed
from django.utils import timezone
from django.db.models import Q
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

    # Fetch candidate tasks (not deleted); we will resolve occurrence per month
    candidates = Task.objects.filter(is_deleted=False)

    # Load completion state for the selected year+month
    done_ids = set(
        TaskDone.objects.filter(year=year, month=month, task__in=candidates).values_list("task_id", flat=True)
    )

    tasks_by_day = {}
    for t in candidates:
        day = t.occurrence_day_in(year, month)
        if not day:
            continue
        # transient attribute for template
        t.is_done = t.id in done_ids
        tasks_by_day.setdefault(day, []).append(t)

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

    year = timezone.localdate().year
    candidates = Task.objects.filter(is_deleted=False)
    items = []
    for t in candidates:
        day = t.occurrence_day_in(year, selected_month)
        if day:
            t._occurrence_day = day
            items.append(t)
    tasks = sorted(items, key=lambda t: (t._occurrence_day, t.name.lower()))

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

    tasks = Task.objects.filter(season=season, is_deleted=False).order_by("month", "day", "name")
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
            task = form.save()
            # Redirect back to appropriate listing.
            if task.month:
                return redirect(f"/tasks/?month={task.month}")
            # For monthly/quarterly/semiannual tasks without a fixed month, go to current month
            if getattr(task, "recurrence", None) in {Task.Recurrence.MONTHLY, Task.Recurrence.QUARTERLY, Task.Recurrence.SEMIANNUAL}:
                return redirect(f"/tasks/?month={timezone.localdate().month}")
            if task.season:
                return redirect("season", season=task.season)
            return redirect("index")
    else:
        form = TaskForm()

    return render(request, "task_form.html", {"form": form, "cancel_url": "/"})


def task_edit(request: HttpRequest, pk: int) -> HttpResponse:
    task = get_object_or_404(Task, pk=pk, is_deleted=False)
    if request.method == "POST":
        form = TaskForm(request.POST, instance=task)
        if form.is_valid():
            task = form.save()
            # Prefer redirect to selected month list
            if task.month:
                return redirect(f"/tasks/?month={task.month}")
            if getattr(task, "recurrence", None) in {Task.Recurrence.MONTHLY, Task.Recurrence.QUARTERLY, Task.Recurrence.SEMIANNUAL}:
                return redirect(f"/tasks/?month={timezone.localdate().month}")
            if task.season:
                return redirect("season", season=task.season)
            return redirect("index")
    else:
        form = TaskForm(instance=task)
    cancel_url = f"/tasks/?month={task.month}" if task.month else "/"
    return render(request, "task_form.html", {"form": form, "cancel_url": cancel_url})


def task_delete(request: HttpRequest, pk: int) -> HttpResponse:
    if request.method != "POST":
        return HttpResponseNotAllowed(["POST"])
    task = get_object_or_404(Task, pk=pk, is_deleted=False)
    # read month from form payload to preserve filter
    try:
        selected_month = int(request.POST.get("month") or 0)
    except (TypeError, ValueError):
        selected_month = task.month or 0
    task.is_deleted = True
    task.deleted_at = timezone.now()
    task.save(update_fields=["is_deleted", "deleted_at", "updated_at"])
    if selected_month:
        return redirect(f"/tasks/?month={selected_month}")
    # fallback to season list or home
    if task.season:
        return redirect("season", season=task.season)
    return redirect("index")


def task_toggle_done(request: HttpRequest, task_id: int) -> HttpResponse:
    if request.method != "POST":
        return HttpResponseNotAllowed(["POST"])
    task = get_object_or_404(Task, id=task_id)
    try:
        year = int(request.POST.get("year") or timezone.localdate().year)
    except (TypeError, ValueError):
        year = timezone.localdate().year
    try:
        month = int(request.POST.get("month") or timezone.localdate().month)
    except (TypeError, ValueError):
        month = timezone.localdate().month

    mark, created = TaskDone.objects.get_or_create(task=task, year=year, month=month)
    if not created:
        # already exists -> uncheck by deleting
        mark.delete()
        is_done = False
    else:
        is_done = True

    # attach transient flag for rendering
    task.is_done = is_done
    return render(request, "partials/task_checkbox.html", {"task": task, "year": year, "month": month})

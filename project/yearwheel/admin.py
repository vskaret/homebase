from django.contrib import admin
from .models import Task, TaskDone

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ("name", "recurrence", "month", "day", "week_rank", "weekday", "updated_at")
    list_filter = ("recurrence", "month", "week_rank", "weekday")
    search_fields = ("name", "notes")

@admin.register(TaskDone)
class TaskDoneAdmin(admin.ModelAdmin):
    list_display = ("task", "year", "month", "completed_at")
    list_filter = ("year", "month")
    search_fields = ("task__name",)

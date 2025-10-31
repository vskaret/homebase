from django.contrib import admin
from .models import Task, TaskDone

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ("name", "season", "month", "day", "updated_at")
    list_filter = ("season",)
    search_fields = ("name", "notes")

@admin.register(TaskDone)
class TaskDoneAdmin(admin.ModelAdmin):
    list_display = ("task", "year", "completed_at")
    list_filter = ("year",)
    search_fields = ("task__name",)

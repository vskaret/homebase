from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("yearwheel", "0003_task_soft_delete"),
    ]

    operations = [
        # Task new fields
        migrations.AddField(
            model_name="task",
            name="weekday",
            field=models.PositiveSmallIntegerField(null=True, blank=True, help_text="0=Mon, 6=Sun"),
        ),
        migrations.AddField(
            model_name="task",
            name="week_rank",
            field=models.CharField(max_length=5, choices=[("1", "Første"), ("2", "Andre"), ("3", "Tredje"), ("4", "Fjerde"), ("last", "Siste")], blank=True, default=""),
        ),
        migrations.AddField(
            model_name="task",
            name="recurrence",
            field=models.CharField(max_length=12, choices=[("yearly", "Årlig"), ("quarterly", "Kvartalsvis"), ("monthly", "Månedlig")], default="yearly"),
        ),
        # TaskDone month field
        migrations.AddField(
            model_name="taskdone",
            name="month",
            field=models.PositiveSmallIntegerField(null=True, blank=True),
        ),
        # Replace the old unique constraint (task, year) with (task, year, month)
        migrations.RemoveConstraint(
            model_name="taskdone",
            name="unique_task_year_done",
        ),
        migrations.AddConstraint(
            model_name="taskdone",
            constraint=models.UniqueConstraint(fields=("task", "year", "month"), name="unique_task_year_month_done"),
        ),
    ]

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("yearwheel", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="TaskDone",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("year", models.PositiveIntegerField()),
                ("completed_at", models.DateTimeField(auto_now_add=True)),
                ("task", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="done_marks", to="yearwheel.task")),
            ],
            options={
                "constraints": [
                    models.UniqueConstraint(fields=("task", "year"), name="unique_task_year_done"),
                ],
            },
        ),
    ]

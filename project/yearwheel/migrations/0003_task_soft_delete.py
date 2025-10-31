from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("yearwheel", "0002_taskdone"),
    ]

    operations = [
        migrations.AddField(
            model_name="task",
            name="is_deleted",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="task",
            name="deleted_at",
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]

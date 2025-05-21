# Tento soubor je zkrácenou verzí původní migrace 0004_alter_service_session_type_alter_session_duration_and_more.py
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("viewer", "0003_add_google_calendar_event_id"),
    ]

    operations = [
        migrations.AlterField(
            model_name="service",
            name="session_type",
            field=models.CharField(
                choices=[("online", "Online"), ("personal", "Personal")],
                default="online",
                max_length=20,
            ),
        ),
        migrations.AlterField(
            model_name="session",
            name="duration",
            field=models.PositiveIntegerField(default=60),
        ),
        migrations.AlterField(
            model_name="session",
            name="type",
            field=models.CharField(
                choices=[("online", "Online"), ("personal", "Personal")],
                default="online",
                max_length=20,
            ),
        ),
    ]

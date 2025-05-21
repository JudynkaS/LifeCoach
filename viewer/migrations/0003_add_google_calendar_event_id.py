from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("viewer", "0002_add_default_session_type"),
    ]

    operations = [
        migrations.AddField(
            model_name="session",
            name="google_calendar_event_id",
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]

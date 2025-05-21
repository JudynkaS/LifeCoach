from django.db import migrations


def create_default_session_type(apps, schema_editor):
    SessionType = apps.get_model("viewer", "SessionType")
    if not SessionType.objects.filter(id=1).exists():
        SessionType.objects.create(
            id=1,
            name="Online Session",
            description="Online coaching session via video call",
        )


def remove_default_session_type(apps, schema_editor):
    SessionType = apps.get_model("viewer", "SessionType")
    SessionType.objects.filter(id=1).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("viewer", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(create_default_session_type, remove_default_session_type),
    ]

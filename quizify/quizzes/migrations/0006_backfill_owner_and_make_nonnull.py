from django.conf import settings
from django.db import migrations, models


def _backfill_owner(apps, schema_editor):
    Quiz = apps.get_model("quizzes", "Quiz")
    # Resolve app label and model name from AUTH_USER_MODEL (like 'quizify_auth.User')
    app_label, model_name = settings.AUTH_USER_MODEL.split(".")
    User = apps.get_model(app_label, model_name)

    # Pick a sensible default: the first user by id
    default_user = User.objects.order_by("id").first()
    if default_user is None:
        # Create a minimal admin user for migration purposes
        default_user = User.objects.create(
            email="migration-admin@example.com",
            username="migration_admin",
            is_staff=True,
            is_superuser=True,
            is_active=True,
        )

    Quiz.objects.filter(owner__isnull=True).update(owner=default_user)


class Migration(migrations.Migration):

    dependencies = [
        ("quizzes", "0005_add_owner_nullable"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.RunPython(_backfill_owner, migrations.RunPython.noop),
        migrations.AlterField(
            model_name="quiz",
            name="owner",
            field=models.ForeignKey(
                to=settings.AUTH_USER_MODEL,
                related_name="quizzes",
                null=False,
                on_delete=models.CASCADE,
            ),
        ),
    ]

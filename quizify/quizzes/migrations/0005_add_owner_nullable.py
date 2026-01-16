from django.conf import settings
from django.db import migrations, models


def _add_owner_column_if_missing(apps, schema_editor):
    # This project uses SQLite in dev. If the column already exists (e.g. created
    # manually or by a failed/partial migration), avoid failing with
    # "duplicate column name: owner_id".
    if schema_editor.connection.vendor != "sqlite":
        return

    with schema_editor.connection.cursor() as cursor:
        cursor.execute('PRAGMA table_info("quizzes_quiz");')
        cols = [row[1] for row in cursor.fetchall()]
        if "owner_id" in cols:
            return

        # Add a nullable integer column. We deliberately keep this simple; the
        # next migration backfills values and then makes it non-nullable.
        cursor.execute('ALTER TABLE "quizzes_quiz" ADD COLUMN "owner_id" integer NULL;')


class Migration(migrations.Migration):

    dependencies = [
        ("quizzes", "0004_fix_user_fk_table"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=[
                migrations.RunPython(_add_owner_column_if_missing, migrations.RunPython.noop),
            ],
            state_operations=[
                migrations.AddField(
                    model_name="quiz",
                    name="owner",
                    field=models.ForeignKey(
                        to=settings.AUTH_USER_MODEL,
                        related_name="quizzes",
                        null=True,
                        on_delete=models.CASCADE,
                    ),
                ),
            ],
        ),
    ]

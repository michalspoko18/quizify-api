from django.db import migrations


def _sqlite_fix_user_fk(apps, schema_editor):
    """Fix invalid FK in SQLite that references non-existent auth_user table.

    Earlier migrations created quizzes_userquizresult.user_id as FK to auth_user,
    but this project uses a custom user model stored in quizify_auth_user.
    SQLite can't ALTER foreign keys, so we rebuild the table.
    """

    if schema_editor.connection.vendor != "sqlite":
        return

    with schema_editor.connection.cursor() as cursor:
        cursor.execute("PRAGMA foreign_key_list(quizzes_userquizresult);")
        fks = cursor.fetchall()
        # fk rows: (id, seq, table, from, to, on_update, on_delete, match)
        references_auth_user = any(row[2] == "auth_user" for row in fks)
        if not references_auth_user:
            return

        cursor.execute("PRAGMA foreign_keys=OFF;")

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS "quizzes_userquizresult__new" (
              "id" integer NOT NULL PRIMARY KEY AUTOINCREMENT,
              "percentage" integer unsigned NOT NULL CHECK ("percentage" >= 0),
              "correct_answers" integer unsigned NOT NULL CHECK ("correct_answers" >= 0),
              "total_questions" integer unsigned NOT NULL CHECK ("total_questions" >= 0),
              "passed" bool NOT NULL,
              "created_at" datetime NOT NULL,
              "quiz_id" bigint NOT NULL REFERENCES "quizzes_quiz" ("id") DEFERRABLE INITIALLY DEFERRED,
              "user_id" integer NULL REFERENCES "quizify_auth_user" ("id") DEFERRABLE INITIALLY DEFERRED,
              "external_user_id" varchar(255) NULL
            );
            """
        )

        cursor.execute(
            """
            INSERT INTO "quizzes_userquizresult__new" (
              "id", "percentage", "correct_answers", "total_questions", "passed", "created_at",
              "quiz_id", "user_id", "external_user_id"
            )
            SELECT
              "id", "percentage", "correct_answers", "total_questions", "passed", "created_at",
              "quiz_id", "user_id", "external_user_id"
            FROM "quizzes_userquizresult";
            """
        )

        cursor.execute('DROP TABLE "quizzes_userquizresult";')
        cursor.execute('ALTER TABLE "quizzes_userquizresult__new" RENAME TO "quizzes_userquizresult";')

        # Recreate indexes (names copied from previous schema)
        cursor.execute(
            'CREATE UNIQUE INDEX IF NOT EXISTS "quizzes_userquizresult_user_id_quiz_id_created_at_671aa2ce_uniq" '
            'ON "quizzes_userquizresult" ("user_id", "quiz_id", "created_at");'
        )
        cursor.execute(
            'CREATE INDEX IF NOT EXISTS "quizzes_userquizresult_quiz_id_4bd0bcfe" '
            'ON "quizzes_userquizresult" ("quiz_id");'
        )
        cursor.execute(
            'CREATE INDEX IF NOT EXISTS "quizzes_userquizresult_user_id_70e3c1f3" '
            'ON "quizzes_userquizresult" ("user_id");'
        )

        cursor.execute("PRAGMA foreign_keys=ON;")


class Migration(migrations.Migration):

    dependencies = [
        ("quizzes", "0003_add_external_user_id"),
    ]

    operations = [
        migrations.RunPython(_sqlite_fix_user_fk, migrations.RunPython.noop),
    ]

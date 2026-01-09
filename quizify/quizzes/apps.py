from django.apps import AppConfig


class QuizzesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'quizzes'

    def ready(self):
        # Import signals to attach post_migrate handler
        from . import signals  # noqa: F401

from django.db.models.signals import post_migrate
from django.dispatch import receiver
from django.contrib.auth import get_user_model


@receiver(post_migrate)
def seed_default_users(sender, **kwargs):
    # Seed only after our app migrations
    if sender.label != 'quizify_auth':
        return

    User = get_user_model()

    # Demo local user
    if not User.objects.filter(email__iexact='demo@quizify.local').exists():
        User.objects.create_user(
            email='demo@quizify.local',
            password='demo1234',
            username='DemoUser',
            auth_provider='local',
        )

    # Demo google-linked user (no password)
    if not User.objects.filter(
        email__iexact='googleuser@quizify.local'
    ).exists():
        user = User.objects.create_user(
            email='googleuser@quizify.local',
            password=None,
            username='GoogleUser',
            auth_provider='google',
        )
        user.google_id = 'demo-google-sub'
        user.save(update_fields=['google_id'])

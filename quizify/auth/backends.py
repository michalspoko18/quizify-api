from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model


class EmailBackend(ModelBackend):
    def authenticate(
        self, request, username=None, email=None, password=None, **kwargs
    ):
        User = get_user_model()
        try:
            lookup_email = email or username
            if not lookup_email or not password:
                return None
            user = User.objects.get(email__iexact=lookup_email)
        except User.DoesNotExist:
            return None

        if user.check_password(password):
            return user
        return None

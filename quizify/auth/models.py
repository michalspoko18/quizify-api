from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser,
    PermissionsMixin,
    BaseUserManager,
)
from django.utils import timezone


class UserManager(BaseUserManager):
    def create_user(
        self,
        email,
        password=None,
        username=None,
        auth_provider="local",
        google_id=None,
        **extra_fields,
    ):
        if not email:
            raise ValueError("Users must have an email address")

        email = self.normalize_email(email)

        if not username:
            username = email.split("@")[0]

        user = self.model(
            email=email,
            username=username,
            auth_provider=auth_provider,
            google_id=google_id,
            **extra_fields,
        )

        if auth_provider == "local":
            user.set_password(password)
        else:
            user.set_unusable_password()

        user.save(using=self._db)
        return user

    def create_superuser(
        self,
        email,
        password=None,
        username=None,
        **extra_fields,
    ):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(
            email=email,
            password=password,
            username=username or "admin",
            auth_provider="local",
            **extra_fields,
        )


class User(AbstractBaseUser, PermissionsMixin):
    class AuthProvider(models.TextChoices):
        LOCAL = "local", "Local"
        GOOGLE = "google", "Google"

    email = models.EmailField(unique=True)
    username = models.CharField(max_length=50, unique=True)
    google_id = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        unique=True,
    )
    auth_provider = models.CharField(
        max_length=20,
        choices=AuthProvider.choices,
        default=AuthProvider.LOCAL,
    )

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    date_joined = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    def __str__(self):
        return f"{self.username} <{self.email}>"

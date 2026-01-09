from rest_framework import serializers
from .models import User


class UserSerializer(serializers.ModelSerializer):
    nick = serializers.CharField(source="username")

    class Meta:
        model = User
        fields = (
            "id",
            "email",
            "nick",
            "auth_provider",
            "google_id",
            "is_active",
            "is_staff",
            "date_joined",
            "updated_at",
        )
        read_only_fields = (
            "is_active",
            "is_staff",
            "date_joined",
            "updated_at",
        )

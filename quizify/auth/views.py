from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from django.contrib.auth import authenticate
from django.contrib.auth import logout as django_logout
from django.contrib.auth import get_user_model
from django.conf import settings
from rest_framework_simplejwt.tokens import RefreshToken
from google.oauth2 import id_token as google_id_token
from google.auth.transport import requests as google_requests
from .serializers import UserSerializer
from django.db import IntegrityError


def _unique_username(base: str) -> str:
    User = get_user_model()
    candidate = base
    suffix = 1
    while User.objects.filter(username=candidate).exists():
        candidate = f"{base}-{suffix}"
        suffix += 1
    return candidate


def _token_response(user):
    refresh = RefreshToken.for_user(user)
    return {
        "user": UserSerializer(user).data,
        "accessToken": str(refresh.access_token),
        "refreshToken": str(refresh),
    }


class AuthenticateUser(APIView):
    permission_classes = [permissions.AllowAny]
    authentication_classes = []

    def post(self, request):
        email = request.data.get("email")
        password = request.data.get("password")

        user = authenticate(request, email=email, password=password)
        if user is None:
            return Response(
                {"detail": "Invalid credentials"},
                status=status.HTTP_401_UNAUTHORIZED,
            )
        if not user.is_active:
            return Response(
                {"detail": "User inactive"},
                status=status.HTTP_403_FORBIDDEN,
            )

        return Response(_token_response(user), status=status.HTTP_200_OK)


class MeView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        return Response(
            UserSerializer(request.user).data,
            status=status.HTTP_200_OK,
        )


class RegisterView(APIView):
    permission_classes = [permissions.AllowAny]
    authentication_classes = []

    def post(self, request):
        email = request.data.get("email")
        password = request.data.get("password")
        username = request.data.get("nick")

        if not email or not password:
            return Response(
                {"message": "Email and password are required."},
                status=status.HTTP_422_UNPROCESSABLE_ENTITY,
            )

        User = get_user_model()
        # Uniqueness checks
        if User.objects.filter(email__iexact=email).exists():
            return Response(
                {"message": "Email jest już zajęty."},
                status=status.HTTP_409_CONFLICT,
            )
        if (
            username
            and User.objects.filter(username__iexact=username).exists()
        ):
            return Response(
                {"message": "Nick jest już zajęty."},
                status=status.HTTP_409_CONFLICT,
            )

        try:
            user = User.objects.create_user(
                email=email,
                password=password,
                username=username or _unique_username(email.split("@")[0]),
                auth_provider="local",
            )
        except IntegrityError:
            return Response(
                {"message": "Email lub nick jest już zajęty."},
                status=status.HTTP_409_CONFLICT,
            )

        return Response(
            _token_response(user),
            status=status.HTTP_201_CREATED,
        )


class LogoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        django_logout(request)
        return Response({"message": "Logged out"}, status=status.HTTP_200_OK)


class ProfileView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        return Response(UserSerializer(request.user).data)

    def put(self, request):
        user = request.user
        # Map 'nick' to internal 'username' for updates
        data = dict(request.data)
        if "nick" in data and "username" not in data:
            data["username"] = data["nick"]
        serializer = UserSerializer(user, data=data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(
            {"errors": serializer.errors},
            status=status.HTTP_422_UNPROCESSABLE_ENTITY,
        )


class RefreshTokenView(APIView):
    permission_classes = [permissions.AllowAny]
    authentication_classes = []

    def post(self, request):
        refresh_token = (
            request.data.get("refreshToken")
            or request.data.get("refresh")
            or request.COOKIES.get("quizapp_refresh")
        )
        if not refresh_token:
            return Response(
                {"detail": "Refresh token required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            refresh = RefreshToken(refresh_token)
        except Exception:
            return Response(
                {"detail": "Invalid refresh token"},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        data = {
            "accessToken": str(refresh.access_token),
            "refreshToken": str(refresh),
        }
        return Response(data, status=status.HTTP_200_OK)


class GoogleLoginView(APIView):
    permission_classes = [permissions.AllowAny]
    authentication_classes = []

    def post(self, request):
        credential = (
            request.data.get("credential")
            or request.data.get("idToken")
            or request.data.get("id_token")
        )
        nick = request.data.get("nick")

        if not credential:
            return Response(
                {"message": "Missing Google ID token."},
                status=status.HTTP_422_UNPROCESSABLE_ENTITY,
            )

        if not settings.GOOGLE_CLIENT_ID:
            return Response(
                {"message": "Google client id not configured."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        try:
            idinfo = google_id_token.verify_oauth2_token(
                credential,
                google_requests.Request(),
                settings.GOOGLE_CLIENT_ID,
            )
        except Exception:
            return Response(
                {"message": "Invalid Google ID token."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        sub = idinfo.get("sub")
        email = idinfo.get("email")
        name = idinfo.get("name")
        picture = idinfo.get("picture")

        if not sub or not email:
            return Response(
                {"message": "Google token missing sub or email."},
                status=status.HTTP_422_UNPROCESSABLE_ENTITY,
            )

        User = get_user_model()
        # If a local account exists with same email, attach google_id
        try:
            user = User.objects.get(email__iexact=email)
            if not user.google_id:
                user.google_id = sub
                user.auth_provider = "google"
                user.save(
                    update_fields=["google_id", "auth_provider", "updated_at"]
                )
        except User.DoesNotExist:
            # Ensure nick (username) uniqueness or generate one
            desired = (nick or email.split("@")[0])
            unique_username = _unique_username(desired)
            # Create new google user
            try:
                user = User.objects.create_user(
                    email=email,
                    password=None,
                    username=unique_username,
                    auth_provider="google",
                    google_id=sub,
                )
            except IntegrityError:
                return Response(
                    {"message": "Nie udało się utworzyć użytkownika Google."},
                    status=status.HTTP_409_CONFLICT,
                )

        # If user existed without google_id, try to attach
        # If user existed and we just attached Google, proceed

        data = _token_response(user)
        data.update({
            "name": name,
            "picture": picture,
        })
        return Response(data, status=status.HTTP_200_OK)

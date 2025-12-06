from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from django.contrib.auth import authenticate, login
from django.contrib.auth import logout as django_logout
from django.contrib.auth import get_user_model
from .serializers import UserSerializer


class AuthenticateUser(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        email = request.data.get("email")
        password = request.data.get("password")

        user = authenticate(request, email=email, password=password)
        if user is None:
            return Response(
                {"detail": "Invalid credentials"},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        login(request, user)
        data = UserSerializer(user).data
        # Frontend expects a token; return a placeholder when using sessions
        data.update({"token": "session"})
        return Response(data, status=status.HTTP_200_OK)


class MeView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        return Response(
            UserSerializer(request.user).data,
            status=status.HTTP_200_OK,
        )


class RegisterView(APIView):
    permission_classes = [permissions.AllowAny]

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
        try:
            user = User.objects.create_user(
                email=email,
                password=password,
                username=username,
                auth_provider="local",
            )
        except Exception as e:
            return Response(
                {"message": str(e) or "Registration failed."},
                status=status.HTTP_409_CONFLICT,
            )

        return Response(
            UserSerializer(user).data,
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
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        # Session-based: nothing to refresh, but OK for frontend
        return Response({"token": "session"}, status=status.HTTP_200_OK)

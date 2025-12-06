from django.urls import path
from auth import views

app_name = 'auth'

urlpatterns = [
    path("login", views.AuthenticateUser.as_view(), name="login"),
    path("register", views.RegisterView.as_view(), name="register"),
    path("logout", views.LogoutView.as_view(), name="logout"),
    path("profile", views.ProfileView.as_view(), name="profile"),
    path("refresh", views.RefreshTokenView.as_view(), name="refresh"),
    path("me", views.MeView.as_view(), name="me"),
]

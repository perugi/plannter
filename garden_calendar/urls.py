from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("password_change", views.password_change, name="password_change"),
    path("planner", views.planner, name="planner"),
    path("settings", views.settings, name="settings"),
]

from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("password_change", views.password_change, name="password_change"),
    path("planner", views.planner, name="planner"),
    path("settings", views.user_settings, name="settings"),
    path("weekly", views.weekly, name="weekly"),
    path("toggle_plant", views.toggle_plant, name="toggle_plant"),
    path("edit_activity", views.edit_activity, name="edit_activity"),
]

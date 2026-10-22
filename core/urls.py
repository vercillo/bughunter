
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import path

from bugs import views


urlpatterns = [
    path("admin/", admin.site.urls),

    path("", views.landing, name="landing"),

    path("dashboard/", views.bug_list, name="bug_list"),
    path("assigned-to-me/", views.assigned_to_me, name="assigned_to_me"),

    path("bugs/new/", views.bug_create, name="bug_create"),
    path("bugs/<int:bug_id>/detail/", views.bug_detail, name="bug_detail"),
    path("bugs/<int:bug_id>/edit/", views.bug_edit, name="bug_edit"),
    path("bugs/<int:bug_id>/assign/", views.assign_bug, name="assign_bug"),
    path("bugs/<int:bug_id>/delete/", views.bug_delete, name="bug_delete"),

    path("tech-staff/add/", views.add_tech_staff, name="add_tech_staff"),

    path("register/", views.register, name="register"),

    path(
        "login/",
        auth_views.LoginView.as_view(
            template_name="bugs/login.html",
            next_page="bug_list",
        ),
        name="login",
    ),

    path(
        "logout/",
        auth_views.LogoutView.as_view(next_page="landing"),
        name="logout",
    ),
]

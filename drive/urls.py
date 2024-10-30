from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("register", views.register_view, name="register"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("upload", views.upload, name="upload"),
    path("download/<int:id>", views.download, name="download"),
    path("shared", views.shared, name="shared"),
    path("shared-with-me", views.shared_with_me, name="shared_with_me"),
    path("file/shared-with/<int:id>", views.shared_with, name="shared_with"),
    path("file/<int:id>", views.file, name="file"),
    path("permissions/<int:id>", views.manage_access, name="manage_access"),
    path("ping", views.ping, name="ping"),
    path("manage", views.manage_account, name="manage_account"),
    path("delete-account", views.delete_account, name="delete_account"),
]

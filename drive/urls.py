from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("register", views.register_view, name="register"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("upload", views.upload, name="upload"),
    path("download/<int:id>", views.download, name="download"),
    path("notifications", views.notifications, name="notifications"),
]

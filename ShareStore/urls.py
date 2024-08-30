"""
URL configuration for ShareStore project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf.urls import handler403, handler404
from django.shortcuts import render


def custom_403_view(request, exception):
    return render(request, "drive/403.html", status=403)


def custom_404_view(request, exception):
    return render(request, "drive/404.html", status=404)


handler403 = custom_403_view
handler404 = custom_404_view

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("drive.urls")),
]

from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth import authenticate, login, logout
from django.urls import reverse
from django.db import IntegrityError
from .models import File, User


# Create your views here.
def index(request):
    return render(request, "drive/index.html")


def login_view(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]

        if not len(username) or not len(password):
            return render(
                request,
                "drive/login.html",
                {
                    "message": "Username and password are required!",
                    "username": username,
                },
            )
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(
                request, "drive/login.html", {"message": "Invalid Credentials!"}
            )

    return render(request, "drive/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register_view(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        password = request.POST["password"]
        confirmation = request.POST["confirmation"]

        if (
            not len(username)
            or not len(email)
            or not len(password)
            or not len(confirmation)
        ):
            return render(
                request,
                "drive/register.html",
                {
                    "message": "All fields are required!",
                    "username": username,
                    "email": email,
                },
            )
        if password != confirmation:
            return render(
                request,
                "drive/register.html",
                {
                    "message": "Passwords must match!",
                    "username": username,
                    "email": email,
                },
            )

        try:
            user = User.objects.create_user(
                username=username, email=email, password=password
            )
            user.save()
        except IntegrityError:
            return render(
                request, "drive/register.html", {"message": "Username already taken!"}
            )
        else:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
    return render(request, "drive/register.html")


def upload(request):
    if request.method == "POST" and request.FILES:
        for i in request.FILES.getlist("files"):
            print(dir(i))
            print(i.content_type)
            print(i.name)
            print(i.size)
    return HttpResponseRedirect(reverse("index"))

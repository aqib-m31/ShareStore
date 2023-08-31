from django.shortcuts import render
from django.http import (
    HttpResponse,
    HttpResponseRedirect,
    StreamingHttpResponse,
)
from django.contrib.auth import authenticate, login, logout
from django.urls import reverse
from django.db import IntegrityError
from .models import File, User, Notification, Share
from .utils import handle_uploaded_file, file_iterator


# Create your views here.
def index(request):
    if request.user.is_authenticated:
        return render(
            request,
            "drive/index.html",
            {"files": File.objects.filter(user=request.user)},
        )
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
                request,
                "drive/login.html",
                {"message": "Invalid Credentials!", "username": username},
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
        for file in request.FILES.getlist("files"):
            if file_path := handle_uploaded_file(file, request.user.id):
                try:
                    f = File(
                        user=request.user,
                        name=file.name,
                        size=file.size,
                        type=file.content_type,
                        path=file_path,
                        access_permissions="Private",
                    )
                    f.save()
                except IntegrityError:
                    return render(
                        request,
                        "drive/upload.html",
                        {"error": "Couldn't save the file info! Try again!"},
                    )
                else:
                    return HttpResponseRedirect(reverse("index"))
            else:
                return render(
                    request,
                    "drive/upload.html",
                    {"error": "An error occurred! Try again!"},
                )

    return render(request, "drive/upload.html")


def download(request, id):
    if not request.user.is_authenticated:
        return render(request, "drive/403.html", status=403)
    try:
        file = File.objects.get(pk=id)
    except File.DoesNotExist:
        return render(request, "drive/404.html", status=40)

    if file.user == request.user:
        try:
            response = StreamingHttpResponse(
                file_iterator(file.path), content_type=file.type
            )
            response["Content-Disposition"] = f'attachment; filename="{file.name}"'
            return response
        except Exception:
            print("Error, Couldn't open file!")
    else:
        return render(request, "drive/403.html", status=403)
    return HttpResponseRedirect(reverse("index"))


def notifications(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse("login"))
    print(Notification.objects.filter(receiver=request.user))
    return render(
        request,
        "drive/notifications.html",
        {"notifications": Notification.objects.filter(receiver=request.user)},
    )

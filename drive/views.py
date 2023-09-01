import json
from django.shortcuts import render
from django.http import (
    HttpResponse,
    HttpResponseRedirect,
    StreamingHttpResponse,
    JsonResponse,
)
from django.contrib.auth import authenticate, login, logout
from django.urls import reverse
from django.db import IntegrityError
from .models import File, User, Share
from .utils import handle_uploaded_file, file_iterator, delete_file


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
        return render(request, "drive/404.html", status=404)

    if (
        file.user == request.user
        or file.access_permissions == "Everyone"
        or (
            file.access_permissions == "Restricted"
            and Share.objects.filter(receiver=request.user)
        )
    ):
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


def shared_with_me(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse("login"))

    return render(
        request,
        "drive/shared_with_me.html",
        {"shared_files": Share.objects.filter(receiver=request.user)},
    )


def shared(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse("login"))

    return render(
        request,
        "drive/shared.html",
        {"shared_files": File.objects.filter(sharing_status=True, user=request.user)},
    )


def file(request, id):
    if request.method == "DELETE":
        if file := File.objects.filter(pk=id).first():
            if file.user == request.user:
                if delete_file(file.path):
                    file.delete()
                    return HttpResponseRedirect(reverse("index"))
                else:
                    return JsonResponse({"error": "Server Error"}, status=500)
            return JsonResponse({"error": "FORBIDDEN"}, status=403)
        return JsonResponse({"error": "Not Found"}, status=404)

    if not request.user.is_authenticated:
        return render(request, "drive/403.html", status=403)
    try:
        file = File.objects.get(pk=id)
    except File.DoesNotExist:
        return render(request, "drive/404.html", status=404)

    if request.user != file.user:
        return render(request, "drive/403.html", status=403)

    if shared := Share.objects.filter(file=file).first():
        shared = shared.receiver.all()
    return render(request, "drive/file.html", {"file": file})


def shared_with(request, id):
    if not request.user.is_authenticated:
        return JsonResponse({"error": "FORBIDDEN"}, status=403)
    try:
        file = File.objects.get(pk=id)
    except File.DoesNotExist:
        return JsonResponse({"error": "NOT FOUND"}, status=404)

    if request.user != file.user:
        return JsonResponse({"error": "FORBIDDEN"}, status=403)

    usernames = []
    if shared := Share.objects.filter(file=file).first():
        shared = shared.receiver.all()
        for user in shared:
            usernames.append(user.username)

    return JsonResponse({"usernames": usernames}, status=200)


def manage_access(request, id):
    if request.method in ["PUT", "DELETE", "POST"]:
        body = json.loads(request.body)

        if not request.user.is_authenticated:
            return JsonResponse({"error": "Forbidden"}, status=403)

        try:
            file = File.objects.get(pk=id)
        except File.DoesNotExist:
            return JsonResponse({"error": "NOT FOUND"}, status=404)

        if file.user != request.user:
            return JsonResponse({"error": "Forbidden"}, status=403)

    if request.method == "PUT":
        permission = body.get("permission")
        permissions = ["Private", "Restricted", "Everyone"]

        if permission is None or body.get("permission") not in permissions:
            return JsonResponse({"error": "Value Error"}, status=400)
        if permission == "Private":
            message = "Not Shared"
            file.sharing_status = False
            Share.objects.filter(file=file).delete()
            file.access_permissions = permission
            file.save()
            return JsonResponse({"message": message}, status=200)

        elif permission == "Restricted":
            if username := body.get("username"):
                if username == request.user.username:
                    return JsonResponse({"error": "It's your own file."}, status=400)
                else:
                    try:
                        receiver = User.objects.get(username=username)
                    except User.DoesNotExist:
                        return JsonResponse(
                            {"error": "Username not found!"}, status=404
                        )
                    else:
                        try:
                            share = Share.objects.get(file=file)
                        except Share.DoesNotExist:
                            try:
                                share = Share(file=file, sender=request.user)
                                share.save()
                                share.receiver.add(receiver)
                            except Exception:
                                return JsonResponse(
                                    {"error": "Server ERROR"}, status=500
                                )
                        else:
                            print(share.receiver.all())
                            if receiver in share.receiver.all():
                                return JsonResponse(
                                    {"error": "Already Shared!"}, status=200
                                )
                            share.receiver.add(receiver)
            message = permission
            file.sharing_status = True
            file.access_permissions = permission
            file.save()
            return JsonResponse({"message": message}, status=200)

        elif permission == "Everyone":
            message = permission
            file.sharing_status = True
            file.access_permissions = permission
            file.save()
            return JsonResponse({"message": message}, status=200)

        return JsonResponse({"error": "Server ERROR"}, status=500)

    elif request.method == "DELETE":
        username = body.get("username")
        if user := User.objects.filter(username=username).first():
            if receivers := Share.objects.filter(file=file).first().receiver.all():
                if user in receivers:
                    Share.objects.get(file=file).receiver.remove(user)
                    return JsonResponse(
                        {"message": f"Access Permissions for {username} removed!"},
                        status=200,
                    )
        return JsonResponse(
            {"error": "Oops! Make sure you're providing valid input!"}, status=404
        )

    return JsonResponse({"error": "POST method required"}, status=400)

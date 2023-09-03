from datetime import datetime
from time import time
import json

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import (
    HttpResponseRedirect,
    StreamingHttpResponse,
    JsonResponse,
)
from django.shortcuts import render
from django.urls import reverse

from .models import File, User, Share
from .utils import file_iterator
from .firebase import bucket


def index(request):
    """
    Render the index page.

    Display files associated with the authenticated user, if logged in.
    Otherwise, show index page with login button.
    """
    if request.user.is_authenticated:
        user_files = File.objects.filter(user=request.user)
        return render(
            request,
            "drive/index.html",
            {"files": user_files},
        )
    return render(request, "drive/index.html")


def login_view(request):
    """
    Handle user login.

    If the request method is POST, attempt to authenticate the user using the provided
    username and password. If successful, log the user in and redirect to the index page.
    If authentication fails, display an error message on the login page.

    If the request method is not POST, render the login page.
    """
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]

        # Check if username and password are provided
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
    """
    Handle user logout.

    Log the user out and redirect to the index page.
    """
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register_view(request):
    """
    Handle user registration.

    If the request method is POST, it attempts to register a new user with the provided
    username, email, and password. Validates that all required fields are provided,
    passwords match, and checks for duplicate usernames. If successful, the user is
    logged in and redirected to the index page.
    """
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


@login_required(login_url="/login")
def upload(request):
    """
    Handles file uploads from the user.
    This view processes file uploads from the user, storing them in Firebase Storage
    and recording their metadata in the database.
    """
    if request.method == "POST" and request.FILES:
        for file in request.FILES.getlist("files"):
            try:
                # Create a unique file name based on user ID and timestamp
                file_name = f"{request.user.id}_{datetime.now().strftime('%Y%m%d%H%M%S')}_{file.name}"

                # Upload the file to Firebase Storage
                file_path = f"user_uploads/user_{request.user.id}/{file_name}"
                blob = bucket.blob(file_path)
                blob.upload_from_file(file)
            except Exception as e:
                return render(
                    request,
                    "drive/upload.html",
                    {"error": f"Couldn't upload the file! Please try again. {e}"},
                )
            else:
                try:
                    # Save file metadata to the database
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
                    # If file info couldn't be saved, delete the uploaded file
                    blob.delete()
                    return render(
                        request,
                        "drive/upload.html",
                        {"error": "Couldn't save file info! Please try again."},
                    )
                else:
                    return HttpResponseRedirect(reverse("index"))

    return render(request, "drive/upload.html")


@login_required(login_url="/login")
def download(request, id):
    """
    Handles file downloads for authorized users.

    This view allows authorized users to download files stored in Firebase Storage.
    It generates a signed URL for the file, allowing temporary access, and streams
    the file content to the user for download.
    """
    try:
        # Attempt to retrieve the file from the database
        file = File.objects.get(pk=id)
    except File.DoesNotExist:
        # Return a 404 error page if the file does not exist
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
            # Create a reference to the file in Firebase Storage
            blob = bucket.blob(file.path)

            # Check if the file exists in Firebase Storage
            if not blob.exists():
                return render(request, "drive/404.html")

            # Generate a signed URL with a 24-hour expiration
            expiration = int(time() + 86400)
            signed_url = blob.generate_signed_url(expiration=expiration)

            # Stream the file content as a response with appropriate headers
            response = StreamingHttpResponse(
                file_iterator(signed_url), content_type="application/octet-stream"
            )
            response["Content-Disposition"] = f'attachment; filename="{file.name}"'
            return response
        except Exception as e:
            print(f"Error, Couldn't open file! {e}")
    else:
        # Return a 403 error page for unauthorized access
        return render(request, "drive/403.html", status=403)

    return HttpResponseRedirect(reverse("index"))


@login_required(login_url="/login")
def shared_with_me(request):
    """
    Displays files shared with the current user.

    This view displays files that have been shared with the currently authenticated user.
    It retrieves shared files from the database and renders them in the 'shared_with_me.html'
    template for the user to view.
    """
    return render(
        request,
        "drive/shared_with_me.html",
        {"shared_files": Share.objects.filter(receiver=request.user)},
    )


@login_required(login_url="/login")
def shared(request):
    """
    Displays files shared by the current user.

    This view displays files that the currently authenticated user has shared with others.
    It retrieves shared files from the database and renders them in the 'shared.html' template
    for the user to view.
    """
    return render(
        request,
        "drive/shared.html",
        {"shared_files": File.objects.filter(sharing_status=True, user=request.user)},
    )


@login_required(login_url="/login")
def file(request, id):
    """
    Display information about a specific file.

    This view provides information about a specific file, including its details and sharing status.
    If the authenticated user has the necessary permissions, they can delete the file.
    """
    if request.method == "DELETE":
        if file := File.objects.filter(pk=id).first():
            if file.user != request.user:
                return JsonResponse({"error": "FORBIDDEN"}, status=403)
            try:
                file_path = file.path
                blob = bucket.blob(file_path)
                if not blob.exists():
                    return JsonResponse({"error": "Not Found"}, status=404)
                blob.delete()
                file.delete()
            except Exception as e:
                print(f"Error {e}")
                return JsonResponse({"error": "Server Error"}, status=500)
            else:
                return HttpResponseRedirect(reverse("index"))

        return JsonResponse({"error": "Not Found"}, status=404)

    try:
        file = File.objects.get(pk=id)
    except File.DoesNotExist:
        return render(request, "drive/404.html", status=404)

    if request.user != file.user:
        return render(request, "drive/403.html", status=403)

    return render(request, "drive/file.html", {"file": file})


def shared_with(request, id):
    """
    Retrieve a list of users with whom the file is shared.

    This view returns a JSON response containing the usernames of users with whom a specific file is shared.
    The authenticated user must have the necessary permissions to access this information.
    """
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
    """
    Manage access permissions for a file.

    This view allows users to manage access permissions for a specific file.
    Users can modify permissions, share the file with others, or remove access for specific users.
    """
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

                try:
                    receiver = User.objects.get(username=username)
                except User.DoesNotExist:
                    return JsonResponse({"error": "Username not found!"}, status=404)

                try:
                    share = Share.objects.get(file=file)
                except Share.DoesNotExist:
                    try:
                        share = Share(file=file, sender=request.user)
                        share.save()
                        share.receiver.add(receiver)
                    except Exception:
                        return JsonResponse({"error": "Server ERROR"}, status=500)
                else:
                    if receiver in share.receiver.all():
                        return JsonResponse({"error": "Already Shared!"}, status=200)
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
            if user in Share.objects.filter(file=file).first().receiver.all():
                # if user in receivers - Remove user!
                Share.objects.get(file=file).receiver.remove(user)
                return JsonResponse(
                    {"message": f"Access Permissions for {username} removed!"},
                    status=200,
                )
        return JsonResponse(
            {"error": "Oops! Make sure you're providing valid input!"}, status=404
        )

    return JsonResponse({"error": "POST method required"}, status=400)

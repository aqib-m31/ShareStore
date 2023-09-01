from django.db import models
from django.contrib.auth.models import AbstractUser


# Create your models here.
class User(AbstractUser):
    pass


class File(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="files")
    name = models.CharField(max_length=255)
    size = models.BigIntegerField()
    type = models.CharField(max_length=50)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    path = models.CharField(max_length=255)
    access_permissions = models.CharField(max_length=20)
    sharing_status = models.BooleanField(default=False)

    @property
    def formatted_size(self):
        size = self.size / 1024
        suffixes = ["KB", "MB", "GB"]

        for suffix in suffixes:
            if size < 1024:
                break
            size /= 1024

        return f"{size:.2f}{suffix}"

    def __str__(self) -> str:
        return f"{self.name} uploaded by {self.user.username} at {self.uploaded_at}"


class Share(models.Model):
    file = models.ForeignKey(File, on_delete=models.CASCADE, related_name="shared")
    sender = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="shared_files"
    )
    receiver = models.ManyToManyField(User, related_name="shared_with")

    def __str__(self) -> str:
        return f"{self.sender.username} shared {self.file.name}"

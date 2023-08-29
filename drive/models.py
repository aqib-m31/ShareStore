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
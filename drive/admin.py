from django.contrib import admin
from .models import User, File

# Register your models here.
admin.site.register(User)
admin.site.register(File)
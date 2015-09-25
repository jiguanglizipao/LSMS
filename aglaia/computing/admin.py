from django.contrib import admin
from django.contrib.auth.models import Permission
from .models import Computing, Package
# Register your models here.

admin.site.register(Package)
admin.site.register(Computing)

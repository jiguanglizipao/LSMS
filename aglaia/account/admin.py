from django.contrib import admin
from django.contrib.auth.models import Permission
from .models import Account, Department
# Register your models here.

admin.site.register(Permission)
admin.site.register(Department)
admin.site.register(Account)

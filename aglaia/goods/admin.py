from django.contrib import admin
from django.contrib.auth.models import Permission
from .models import GType, Goods, Single, Borrow
# Register your models here.

admin.site.register(Single)
admin.site.register(Borrow)
admin.site.register(Goods)
admin.site.register(GType)

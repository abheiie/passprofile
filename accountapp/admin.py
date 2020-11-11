from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, UserType, UserGroup

admin.site.register(User, UserAdmin)
admin.site.register(UserType)
admin.site.register(UserGroup)


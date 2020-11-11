from django.db import models
from django.contrib.auth.models import AbstractUser

class UserType(models.Model):
    name = models.CharField(max_length=100, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class User(AbstractUser):
    user_type = models.ForeignKey(UserType, on_delete=models.CASCADE)
    raw_password = models.CharField(max_length=30, null=True, blank=True)


class UserGroup(models.Model):
    name = models.CharField(max_length=300, null=True, blank=False)
    user = models.ManyToManyField(User, blank=True)
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_groups", blank=True,null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

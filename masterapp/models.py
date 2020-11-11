from django.db import models
from accountapp.models import User, UserGroup

# Create your models here.
class Credential(models.Model):
    product = models.CharField(max_length=300, null=True, blank=False)
    username = models.CharField(max_length=100, null=True, blank=False)
    password = models.CharField(max_length=100, null=True,blank=False)
    user = models.ManyToManyField(User, blank=True)
    user_group = models.ManyToManyField(UserGroup, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

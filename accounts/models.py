from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager


# class CustomUserManager(BaseUserManager):
#     pass

class User(AbstractUser):
    pass

    # objects = CustomUserManager()
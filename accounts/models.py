from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager,Group

from general.models import BaseModel
from datetime import datetime, timedelta
from .functions import get_auto_id




# class CustomUserManager(BaseUserManager):
#     pass

USER_ROLE_CHOICES = [
        ('super_admin', 'Super Admin'),
        ('student', 'Student'),
    ]

class User(AbstractUser):
    # Additional fields
    dob = models.DateField(null=True, blank=True)
    phone = models.CharField(max_length=15, unique=True, null=True, blank=True)
    profile_image = models.ImageField(upload_to='profile_images/', null=True, blank=True)
    is_verified=models.BooleanField(default=False)
    user_role = models.CharField(max_length=20, choices=USER_ROLE_CHOICES, default='student')
    encrypted_password=models.CharField(null=True,blank=True)

    def __str__(self):
        return self.username
  

class SocialMediaLink(BaseModel):
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='social_links')
    link = models.URLField(max_length=255)
    name = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.user}'s {self.name} link"
    
    def save(self, *args, **kwargs):
        if self._state.adding:
                auto_id = get_auto_id(SocialMediaLink)
                self.auto_id = auto_id

        super(SocialMediaLink, self).save(*args, **kwargs)
    
    class Meta:
        db_table = "accounts_SocialMediaLink"
        verbose_name = "SocialMediaLink"
        verbose_name_plural = "SocialMediaLink"
        ordering = ("date_added",)

class OTP(BaseModel):
    phone = models.CharField(max_length=15, blank=True, null=True)
    otp = models.CharField(max_length=6, blank=True, null=True)  
    is_verified = models.BooleanField(default=False)
    attempt = models.PositiveBigIntegerField(default=0)  
    expiration_time = models.DateTimeField(null=True, blank=True)  
    def is_expired(self):
        return self.expiration_time < datetime.now().astimezone() 
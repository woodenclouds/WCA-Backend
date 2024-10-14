from rest_framework import serializers

from django.db.models import Sum, Count
from django.db.models import Avg

from accounts.models import *
from general.encryptions import encrypt,decrypt

from datetime import datetime
from . functions import *


class UserSignUpSerializer(serializers.Serializer):
    first_name = serializers.CharField(max_length=100)
    last_name = serializers.CharField(max_length=100)
    email = serializers.EmailField(max_length=255)
    phone = serializers.CharField(max_length=15)
    dob = serializers.DateField()
    
    def validate_phone(self, value):
        if User.objects.filter(phone=value).exists():
            raise serializers.ValidationError("Phone number already exists.")
        return value
    
    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email already exists.")
        return value
    
    def create(self, validated_data):
        user = User.objects.create_user(
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            email=validated_data['email'],
            phone=validated_data['phone'],
            dob=validated_data['dob'],
            username=validated_data['email'],  # Assuming username is based on email
            password= generate_random_password()
        )
        return user
    
class SignupVerifyOtpSerializer(serializers.Serializer):
    otp = serializers.CharField(min_length=4, max_length=4)
    phone = serializers.CharField()


class SocialMediaLinksViewSerializer(serializers.ModelSerializer):
    class Meta:
        model=SocialMediaLink
        fields=['id','link','name']

class UserProfileViewSerializer(serializers.ModelSerializer):
    social_media_links=SocialMediaLinksViewSerializer(many=True,read_only=True,source='social_links')
    class Meta:
        model=User
        fields=['email','profile_image','first_name','last_name','dob','phone','social_media_links']

class SocialMediaLinkSerializer(serializers.Serializer):
    name=serializers.CharField()
    link=serializers.URLField()

class UserEditProfileSerializer(serializers.Serializer):
    first_name=serializers.CharField(required=False)
    last_name=serializers.CharField(required=False)
    email=serializers.CharField(required=False)
    dob=serializers.DateField(required=False)
    phone=serializers.CharField(required=False)
    profile_image=serializers.ImageField(required=False)
    social_media_links=SocialMediaLinkSerializer(many=True,required=False)
    
    def validate_email(self,value):
        user_id=self.context['user_id']
        if User.objects.filter(email=value).exclude(id=user_id).exists():
            raise serializers.ValidationError("Email Already Exists")
        return value
    def validate_phone(self,value):
        user_id=self.context['user_id']
        if User.objects.filter(phone=value).exclude(id=user_id).exists():
            raise serializers.ValidationError("Phone Number Already Exists")
        return value
    def update(self,instance,validated_data):
        instance.first_name=validated_data.get('first_name',instance.first_name)
        instance.last_name=validated_data.get('last_name',instance.last_name)
        instance.email=validated_data.get('email',instance.email)
        instance.dob=validated_data.get('dob',instance.dob)
        instance.phone=validated_data.get('phone',instance.phone)
        profile_image=validated_data.get('profile_image',None)
        if profile_image:
            instance.profile_image=profile_image

        instance.save()

        social_media_links=validated_data.get('social_media_links',[])
        for link_data in social_media_links:
            name=link_data.get('name')
            link=link_data.get('link')
            if name and link:
                # Check if social media link exists for the user
                social_link, created = SocialMediaLink.objects.update_or_create(
                    user=instance,
                    name=name,
                    defaults={'link': link}
                )
        return instance
            
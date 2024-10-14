from rest_framework import serializers

from django.db.models import Sum, Count
from django.db.models import Avg

from accounts.models import *
from general.encryptions import encrypt,decrypt

from datetime import datetime
from . functions import *
from activities.models import *


# class UserSignUpSerializer(serializers.Serializer):
#     first_name = serializers.CharField(max_length=100)
#     last_name = serializers.CharField(max_length=100)
#     email = serializers.EmailField(max_length=255)
#     phone = serializers.CharField(max_length=15)
#     dob = serializers.DateField()
    
#     def validate_phone(self, value):
#         if User.objects.filter(phone=value).exists():
#             raise serializers.ValidationError("Phone number already exists.")
#         return value
    
#     def validate_email(self, value):
#         if User.objects.filter(email=value).exists():
#             raise serializers.ValidationError("Email already exists.")
#         return value
    
#     def create(self, validated_data):
#         user = User.objects.create_user(
#             first_name=validated_data['first_name'],
#             last_name=validated_data['last_name'],
#             email=validated_data['email'],
#             phone=validated_data['phone'],
#             dob=validated_data['dob'],
#             username=validated_data['email'],  # Assuming username is based on email
#             password= generate_random_password()
#         )
#         return user
    
# class SignupVerifyOtpSerializer(serializers.Serializer):
#     otp = serializers.CharField(min_length=4, max_length=4)
#     phone = serializers.CharField()

class ListWebinarSerializer(serializers.ModelSerializer):
    category=serializers.CharField(source='category.name')
    join_date=serializers.SerializerMethodField()
    
    class Meta:
        model=Webinar
        fields=['id','category','title','host_name','start_time','end_time','join_link','image','join_date']
    
    def get_join_date(self,instance):
        formatted_date = instance.event_date.strftime("%d %b %Y")
        formatted_time = instance.event_date.strftime("%H:%M:%S")  # Keep time format as before
        return f"{formatted_date}"
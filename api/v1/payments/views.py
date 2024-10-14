import traceback
import logging
import json
from django.utils import timezone
from datetime import timedelta

from datetime import date

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from django.db import transaction
from django.db.models import Q
from django.shortcuts import render
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
#email
from django.core.mail import send_mail
from django.conf import settings
from django.http import HttpResponse

from api.v1.accounts.serializers import *
from accounts.models import *
from general.models import *
# from payments.models import *
# from general.decorators import group_required
from general.functions import *
from general.encryptions import *
from api.v1.accounts.functions import *
from . functions import *

@api_view(["POST"])
@permission_classes((AllowAny,))
def user_signup(request):
    try:
        serialized = UserSignUpSerializer(data=request.data)
        
        if serialized.is_valid():
            with transaction.atomic():  # Ensure database integrity in case of an error
                user = serialized.save()

                # If OTP generation is required
                otp = generate_otp()  # Generate an OTP
                print(f"Generated OTP: {otp}")

               
                expiration_time = timezone.now() + timedelta(minutes=3)

                otp_obj = OTP.objects.create(
                    phone=user.phone,
                    otp=otp,
                    expiration_time=expiration_time
                )
                
                # Send OTP via email and/or SMS
                
                #send_otp_via_fast2sms(phone=user.phone, otp=otp_obj.otp)
                
                # Return success response
                response_data = {
                    "StatusCode": 6000,
                    "data": {
                        "title": "Success",
                        "message": f"OTP sent to {user.phone}"
                    }
                }
                return Response({'app_data': response_data}, status=status.HTTP_200_OK)
        
        else:
            # Validation errors
            response_data = {
                "StatusCode": 6001,
                "data": serialized.errors
            }
            return Response({'app_data': response_data}, status=status.HTTP_200_OK)
    
    except Exception as e:
        # Rollback transaction and handle errors
        transaction.rollback()
        response_data = {
            "StatusCode": 6001,
            "data": {
                "title": "Failed",
                "message": str(e),
                "traceback": traceback.format_exc()
            }
        }
        return Response({'app_data': response_data}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    



@api_view(["POST"])
@permission_classes((AllowAny,))
def verify_otp(request):
    try:
        
        serialized = SignupVerifyOtpSerializer(data=request.data)
        if serialized.is_valid():
                phone = serialized.validated_data.get('phone')
                otp = serialized.validated_data.get('otp')
        
                if not OTP.objects.filter(phone=phone).exists():
                    response_data = {
                        "StatusCode": 6001,
                        "message": "OTP not found"
                    }
                    return Response({'app_data': response_data}, status=status.HTTP_400_BAD_REQUEST)

                # Check if user exists for the given phone number
                if not User.objects.filter(phone=phone).exists():
                    response_data = {
                        "StatusCode": 6001,
                        "message": "User not found"
                    }
                    return Response({'app_data': response_data}, status=status.HTTP_400_BAD_REQUEST)

                otp_model = OTP.objects.filter(phone=phone).latest("date_added")
                user = User.objects.filter(phone=phone).first()

                # Check if OTP is expired
                if otp_model.is_expired():
                    user.delete()
                    response_data = {
                        "StatusCode": 6001,
                        "message": "OTP expired. User deleted."
                    }
                    return Response({'app_data': response_data}, status=status.HTTP_400_BAD_REQUEST)

                # Check if OTP attempt exceeds 3
                if otp_model.attempt >= 3:
                    user.delete()
                    otp_model.delete()  # Also delete the OTP record
                    response_data = {
                        "StatusCode": 6001,
                        "message": "OTP attempt limit exceeded. User deleted."
                    }
                    return Response({'app_data': response_data}, status=status.HTTP_400_BAD_REQUEST)

                # Check if the OTP matches
                if otp_model.otp != otp:
                    otp_model.attempt += 1
                    otp_model.save()
                    response_data = {
                        "StatusCode": 6001,
                        "message": f"Invalid OTP. {3 - otp_model.attempt} attempts left."
                    }
                    return Response({'app_data': response_data}, status=status.HTTP_400_BAD_REQUEST)

                # Mark user as verified and add to the group
                user.is_verified = True
                user.save()
                add_user_to_group(user, user.user_role)

                
                
                otp_model.delete()  # OTP is no longer needed after successful verification
                
                # Assuming you have a function `get_user_login_credentials` that returns a token
                token = get_user_login_credentials(user)
                response_data = {
                    "StatusCode": 6000,
                    "data": {
                        'title': "Success",
                        'message': "User created successfully",
                        'token': token
                    }
                }
                return Response({'app_data': response_data}, status=status.HTTP_200_OK)
        
        
        else:
            response_data = {
                "StatusCode": 6001,
                "data": generate_serializer_errors(serialized.errors)
            }
            return Response({'app_data': response_data}, status=status.HTTP_400_BAD_REQUEST)
    
    except Exception as E:
        transaction.rollback()
        errType = E.__class__.__name__
        errors = {
            errType: traceback.format_exc()
        }
        response_data = {
            "StatusCode": 6001,
            "title": "Failed",
            "api": request.get_full_path(),
            "request": request.data,
            "message": str(E),
            "response": errors
        }
        return Response({'app_data': response_data}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



@api_view(["POST"])
@permission_classes((AllowAny,))
def user_login(request):
    try:
        phone = request.data.get('phone')
    
        user = User.objects.filter(phone=phone).first()

        if not user:
            return Response({
                "StatusCode": 6001,
                "message": "User not found"
            }, status=400)

        if not user.is_verified:
            return Response({
                "StatusCode": 6001,
                "message": f"User not verified."
            }, status=400)

        otp = generate_otp()
        expiration_time = timezone.now() + timedelta(minutes=3)
        print(otp)

        otp_obj = OTP.objects.create(
            phone=user.phone,
            otp=otp,
            expiration_time=expiration_time
        )
        #send_login_otp_via_fast2sms(phone=user.phone, otp=otp_obj.otp)

        return Response({
            "StatusCode": 6000,
            "message": f"OTP sent to {user.phone}"
        }, status=200)

    except Exception as E:
        transaction.rollback()
        errType = E.__class__.__name__
        errors = {
            errType: traceback.format_exc()
        }
        response_data = {
            "StatusCode": 6001,
            "title": "Failed",
            "api": request.get_full_path(),
            "request": request.data,
            "message": str(E),
            "response": errors
        }
        return Response({'app_data': response_data}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    

@api_view(["POST"])
@permission_classes((AllowAny,))
def user_login_verify(request):
    try:
        phone = request.data.get('phone')
        otp = request.data.get('otp')

        if not OTP.objects.filter(phone=phone,is_verified=False).exists():
            return Response({
                "StatusCode": 6001,
                "message": "OTP not found"
            }, status=400)

       
        user = User.objects.filter(phone=phone).first()
        if not user:
            return Response({
                "StatusCode": 6001,
                "message": "User not found"
            }, status=400)

        otp_model = OTP.objects.filter(phone=phone).latest("date_added")

        # Check if OTP is expired
        if otp_model.is_expired():
            return Response({
                "StatusCode": 6001,
                "message": "OTP expired"
            }, status=400)

        # Check if OTP attempt exceeds 3
        if otp_model.attempt >= 3:
            otp_model.delete()  # Delete the OTP record
            return Response({
                "StatusCode": 6001,
                "message": "OTP attempt limit exceeded"
            }, status=400)

        # Check if the OTP matches
        if otp_model.otp != otp:
            otp_model.attempt += 1
            otp_model.save()
            return Response({
                "StatusCode": 6001,
                "message": f"Invalid OTP. {3 - otp_model.attempt} attempts left."
            }, status=400)

        otp_model.is_verified=True 
        token = get_user_login_credentials(user)
        response_data = {
            "StatusCode": 6000,
            "data": {
                'title': "Success",
                'message': "Login successful",
                'token': token
            }
        }
        return Response({'app_data': response_data}, status=200)

    except Exception as E:
        transaction.rollback()
        errType = E.__class__.__name__
        errors = {
            errType: traceback.format_exc()
        }
        response_data = {
            "StatusCode": 6001,
            "title": "Failed",
            "api": request.get_full_path(),
            "request": request.data,
            "message": str(E),
            "response": errors
        }
        return Response({'app_data': response_data}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
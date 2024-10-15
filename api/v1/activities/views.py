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
from courses.models import *
from activities.models import *
from .serializers import *
# from payments.models import *
# from general.decorators import group_required
from general.functions import *
from general.encryptions import *
from api.v1.accounts.functions import *
from . functions import *


@api_view(["GET"])
@permission_classes([AllowAny])
def get_webinar_list(request):
    try:
        webinars=Webinar.objects.filter(is_deleted=False).order_by("date_added")
        
        if webinars.exists():
            paginated_data = paginate_data(webinars, request, items_per_page=10)
            serialized_data =ListWebinarSerializer(
                paginated_data['instances'],
                context={"request": request},
                many=True
            ).data

            response_data = {
                "StatusCode": 6000,
                "title": "Success",
                "data":{
                    "data":serialized_data,
                    
                    "pagination": {
                        "has_next_page": paginated_data['has_next_page'],
                        "next_page_number": paginated_data['next_page_number'],
                        "has_previous_page": paginated_data['has_previous_page'],
                        "previous_page_number": paginated_data['previous_page_number'],
                        "total_pages": paginated_data['total_pages'],
                        "total_items": paginated_data['total_items'],
                        "first_item": paginated_data['first_item'],
                        "last_item": paginated_data['last_item'],
                    }
                },
            }
        else:
            response_data = {
                "StatusCode": 6001,
                "data": [],
                "message": "No Webinars found"
            }
        
        return Response({"app_data": response_data}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({
            'app_data': {
                "StatusCode": 6001,
                "title": "Failed",
                "api": request.get_full_path(),
                "request": request.data,
                "message": str(e),
                "response": {
                    e.__class__.__name__: traceback.format_exc()
                }
            }
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def purchase_course(request):
    try:
        user = request.user
        course_id = request.data.get("course_id")
        # Check if the course exists
        course = Course.objects.filter(id=course_id).first()
        if not course:
            return Response({
                'app_data': {
                    "StatusCode": 6001,
                    "title": "Failed",
                    "message": "Course not found",
                }
            }, status=status.HTTP_404_NOT_FOUND)

        # Check if the user has already purchased this course
        if CoursePurchase.objects.filter(user=user, course=course).exists():
            return Response({
                'app_data': {
                    "StatusCode": 6001,
                    "title": "Failed",
                    "message": "You have already purchased this course",
                }
            }, status=status.HTTP_400_BAD_REQUEST)

        # Create the course purchase record
        CoursePurchase.objects.create(user=user, course=course)

        response_data = {
            "StatusCode": 6000,
            "title": "Success",
            "message": "Course purchased successfully",
        }
        return Response({"app_data": response_data}, status=status.HTTP_201_CREATED)

    except Exception as e:
        return Response({
            'app_data': {
                "StatusCode": 6001,
                "title": "Failed",
                "api": request.get_full_path(),
                "request": request.data,
                "message": str(e),
                "response": {
                    e.__class__.__name__: traceback.format_exc()
                }
            }
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
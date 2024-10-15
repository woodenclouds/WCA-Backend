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
# from payments.models import *
# from general.decorators import group_required
from general.functions import *
from general.encryptions import *
from api.v1.accounts.functions import *
from . functions import *
from .serializers import *



@api_view(["GET"])
@permission_classes([AllowAny])
def get_courses_list(request):
    try:
        courses=Course.objects.filter(is_published=True).order_by("date_added")
        
        if courses.exists():
            paginated_data = paginate_data(courses, request, items_per_page=10)
            serialized_data =ListCourseSerializer(
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
                "message": "No Courses found"
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
    


@api_view(["GET"])
@permission_classes([AllowAny])
def get_course_sub_content_sidebar(request,pk):
    try:
        course=Course.objects.filter(id=pk).first()
        if not course:
            return Response({
                'app_data': {
                    "StatusCode": 6001,
                    "data": {
                        "title": "Failed",
                        "message": "Course Not Found",
                    }
                }
            }, status=status.HTTP_404_NOT_FOUND)
        user = request.user

        
        has_purchased = CoursePurchase.objects.filter(user=user, course=course).exists()


        course_sub_contents=CourseSubContent.objects.filter(course=course).order_by("position")
        
        if course_sub_contents.exists():
            
            serialized_data =ListCourseSubcontentSidebar(
                course_sub_contents,
                many=True
            ).data

            response_data = {
                "StatusCode": 6000,
                "title": "Success",
                "data":{
                    "data":serialized_data,
                    "is_purchased":has_purchased
                },
            }
        else:
            response_data = {
                "StatusCode": 6001,
                "data": [],
                "message": "No Course Subcontent found for this course"
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
    


@api_view(["GET"])
@permission_classes([AllowAny])
def get_chapters_of_sub_content_sidebar(request,pk):
    try:
        subcontent=CourseSubContent.objects.filter(id=pk).first()
        if not subcontent:
            return Response({
                'app_data': {
                    "StatusCode": 6001,
                    "data": {
                        "title": "Failed",
                        "message": "Subcontent Not Found",
                    }
                }
            }, status=status.HTTP_404_NOT_FOUND)


        chapters=subcontent.chapters.filter(is_published=True).order_by("position")
        
        if chapters.exists():
            
            serialized_data =ListChapterofSubcontentSidebar(
                chapters,
                context={"request":request},
                many=True
            ).data

            response_data = {
                "StatusCode": 6000,
                "title": "Success",
                "data":{
                    "data":serialized_data,
                },
            }
        else:
            response_data = {
                "StatusCode": 6001,
                "data": [],
                "message": "No Chapters Found for this subcontent"
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



@api_view(["GET"])
@permission_classes([AllowAny])
def get_chapter_detail(request,pk):
    try:
        chapter=Chapter.objects.filter(id=pk).first()
        if not chapter:
            return Response({
                'app_data': {
                    "StatusCode": 6001,
                    "data": {
                        "title": "Failed",
                        "message": "Chapter Not Found",
                    }
                }
            }, status=status.HTTP_404_NOT_FOUND)
        
        
            
        serialized_data =ViewChapterDetail (
            chapter,
            context={"request":request},
        ).data

        response_data = {
            "StatusCode": 6000,
            "title": "Success",
            "data":{
                "data":serialized_data,
            },
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
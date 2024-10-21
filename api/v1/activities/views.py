import traceback
import logging
import json
import mimetypes
import os
import zipfile
import io

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
        if Course.objects.filter(id=course_id).exists():
            course = Course.objects.filter(id=course_id).first()
        else:
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


@api_view(["PUT"])
@permission_classes([IsAuthenticated])
def update_user_progress(request,pk):
    try:
        user=request.user
        if Chapter.objects.filter(id=pk).exists():
            chapter=Chapter.objects.filter(id=pk).first()
        else:
            response_data={
                "StatusCode":6001,
                "message":"Chapter Not Found"
                }
            return Response({"app_data":response_data},status=status.HTTP_200_OK)
        if UserProgress.objects.filter(user=user,chapter=chapter).exists():
            response_data={
                "StatusCode":6000,
                "message":"Already Watched this Chapter"
            }
            return Response({"app_data":response_data},status=status.HTTP_200_OK)
        UserProgress.objects.create(user=user,chapter=chapter)
        response_data={
            "StatusCode":6000,
            "message":"Succesfully Updated Your Progress"
        }
        return Response({"app_data":response_data},status=status.HTTP_200_OK)
      
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

@api_view(["PUT"])
@permission_classes([IsAuthenticated])
def user_complete_chapter_progress(request,pk):
    try:
        if UserProgress.objects.filter(id=pk).exists():
            userprogress=UserProgress.objects.get(id=pk)
        else:
            response_data={
                "StatusCode":6001,
                "message":"UserProgress Not Found"
            }
            return Response({"app_data":response_data},status=status.HTTP_200_OK)
        if userprogress.is_completed:
            response_data={
                "StatusCode":6001,
                "message":"User Already Completed this Chapter"
            }
            return Response({"app_data":response_data},status=status.HTTP_200_OK)
        userprogress.is_completed=True
        userprogress.completed_time=timezone.now()
        userprogress.save()
        response_data={
            "StatusCode":6000,
            "message":"User completed this chapter"
        }
        return Response({"app_data":response_data},status=status.HTTP_200_OK)
        
      
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
@permission_classes([IsAuthenticated])
def download_attachment(request, pk):
    try:
        # Check if the attachment exists
        if not Attachment.objects.filter(id=pk).exists():
            return Response({
                'app_data': {
                    "StatusCode": 6001,
                    "title": "Failed",
                    "message": "Attachment Not Found"
                }
            }, status=status.HTTP_404_NOT_FOUND)
        
        attachment = Attachment.objects.filter(id=pk).first()

        # Check if the attachment type is a document
        if attachment.type != 'doc':
            return Response({
                'app_data': {
                    "StatusCode": 6001,
                    "title": "Failed",
                    "message": "Attachment is not a document"
                }
            }, status=status.HTTP_400_BAD_REQUEST)

        # Check if the file exists in the file system
        if not attachment.file or not os.path.exists(attachment.file.path):
            return Response({
                'app_data': {
                    "StatusCode": 6001,
                    "title": "Failed",
                    "message": "File not found"
                }
            }, status=status.HTTP_404_NOT_FOUND)

       # Determine the content type of the file
        file_path = attachment.file.path
        uploaded_file_name = os.path.basename(attachment.file.name)  # Get the original uploaded file name
        mime_type, _ = mimetypes.guess_type(file_path)

        # Serve the file for download
        with open(file_path, 'rb') as f:
            response = HttpResponse(f.read(), content_type=mime_type)
            # Set Content-Disposition to use the uploaded file name
            response['Content-Disposition'] = f'attachment; filename="{uploaded_file_name}"'
            return response

    except Exception as e:
        # Handle any unexpected errors
        return Response({
            'app_data': {
                "StatusCode": 6001,
                "title": "Failed",
                "api": request.get_full_path(),
                "request": request.data,
                "message": str(e),
                "response": {
                    e.__class__.__name__: str(e)
                }
            }
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def download_all_documents(request,pk):
    try:
        
        if not Chapter.objects.filter(id=pk).exists():
            return Response({
                'app_data': {
                    "StatusCode": 6001,
                    "title": "Failed",
                    "message": "Chapter Not Found"
                }
            }, status=status.HTTP_404_NOT_FOUND)
        chapter = Chapter.objects.filter(id=pk).first()

        # Fetch all document attachments for the chapter
        documents = chapter.attachments.filter(type='doc', file__isnull=False)
        if not documents.exists():
            return Response({
                'app_data': {
                    "StatusCode": 6001,
                    "title": "Failed",
                    "message": "No documents available for this chapter"
                }
            }, status=status.HTTP_404_NOT_FOUND)

        # Create a zip file in memory
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w') as zip_file:
            for document in documents:
                if document.file:
                    # Add the file to the zip file, using the original file name
                    zip_file.write(document.file.path, arcname=os.path.basename(document.file.name))

        # Prepare the response
        zip_buffer.seek(0)  # Move to the beginning of the BytesIO buffer
        response = HttpResponse(zip_buffer.read(), content_type='application/zip')
        response['Content-Disposition'] = f'attachment; filename="documents_chapter_{pk}.zip"'
        response['Content-Length'] = zip_buffer.tell()  # Optional: set the content length

        return response

    except Exception as e:
        return Response({
            'app_data': {
                "StatusCode": 6001,
                "title": "Failed",
                "api": request.get_full_path(),
                "request": request.data,
                "message": str(e),
                "response": {
                    e.__class__.__name__: str(e)
                }
            }
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



@api_view(["GET"])
@permission_classes([IsAuthenticated])
def latest_attempt_summary(request,pk):
    try:
        # Get the current user
        user = request.user
        assessment=Assessment.objects.filter(id=pk).first()
        if not assessment:
            return Response({
                "app_data":{
                    "StatusCode":6001,
                    "title":"Failed",
                    "message":"No Assesment Found"
                }
            },status=status.HTTP_404_NOT_FOUND)

        # Fetch the latest user attempt
        latest_attempt = UserAssessmentAttempt.objects.filter(user=user,assessment=assessment).order_by('-attempt_number').first()
        if not latest_attempt:
            return Response({
                "app_data": {
                    "StatusCode": 6001,
                    "title": "Failed",
                    "message": "No attempts found for the user for this assessment.",
                }
            }, status=status.HTTP_404_NOT_FOUND)

        # Fetch the related assessment
        assessment = latest_attempt.assessment

        # Calculate max score based on total marks of all questions in the assessment
        max_score = latest_attempt.max_score

        # Prepare the response data
        response_data = {
            'course_title': assessment.course_sub_content.course.title,  # Assuming Assessment has a relation to Course model
            'assessment_title': assessment.title,
            'scoring_policy': assessment.scoring_policy,
            'passing_score': assessment.passing_score,
            'total_questions': assessment.total_questions,
            'assessment_type': assessment.type,
            'max_attempts': assessment.max_attempts,
            'max_score': max_score or 0,
            'total_score': latest_attempt.total_score,
            'status': latest_attempt.status,
            'attempt_number': latest_attempt.attempt_number,
        }

        # Serialize the response data
       

        # Return the serialized data in the response
        return Response({"app_data": {"StatusCode": 6000, "data": response_data}}, status=status.HTTP_200_OK)

    except Exception as E:
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
    

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_assessment_attempt_history_list(request,pk):
    try:
        user=request.user
        assessment=Assessment.objects.filter(id=pk).first()
        if not assessment:
            return Response({
                "app_data":{
                    "StatusCode":6001,
                    "title":"Failed",
                    "message":"No Assesment Found"
                }
            },status=status.HTTP_404_NOT_FOUND)
        user_attempts = UserAssessmentAttempt.objects.filter(
        user=user, 
        assessment=assessment
    ).order_by('attempt_number')
        
        if user_attempts.exists():
            paginated_data = paginate_data(user_attempts, request, items_per_page=10)
            serialized_data =ListUserAssessmentAttemptHistorySerializer(
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
                "message": "No User Attempts Found"
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
@permission_classes([IsAuthenticated])
def get_user_attempt_detail(request,pk):
    try:
        user_assessment_attempt = UserAssessmentAttempt.objects.filter(id=pk).first()
        if not user_assessment_attempt:
            return Response({
                'app_data': {
                    "StatusCode": 6001,
                    "data": {
                        "title": "Failed",
                        "message": "User Assessment Attempt Not Found",
                    }
                }
            }, status=status.HTTP_404_NOT_FOUND)
        
        
            
        serialized_data=UserAssessmentAttemptDetailSerializer(user_assessment_attempt).data

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
    
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def add_assessment_feedback(request):
    try:
        user = request.user
        user_attempt_id = request.data.get("user_assessment_id")
        # Check if the course exists
        if UserAssessmentAttempt.objects.filter(id=user_attempt_id).exists():
            user_assessment_attempt = UserAssessmentAttempt.objects.filter(id=user_attempt_id).first()
        else:
            return Response({
                'app_data': {
                    "StatusCode": 6001,
                    "title": "Failed",
                    "message": "UserAssessment not found",
                }
            }, status=status.HTTP_404_NOT_FOUND)
        
        serialized=AssessmentAttemptFeedbackSerializer(data=request.data)
        if serialized.is_valid():
            comment=serialized.validated_data.get("comment")

        AssessmentAttemptFeedback.objects.create(user=user,user_attempt=user_assessment_attempt,comment=comment)

        response_data = {
            "StatusCode": 6000,
            "title": "Success",
            "message": "Assessment Feedback Submitted Successfully",
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
    


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_task_detail(request,pk):
    try:
        task = Task.objects.filter(id=pk).first()
        if not task:
            return Response({
                'app_data': {
                    "StatusCode": 6001,
                    "data": {
                        "title": "Failed",
                        "message": "Task Not Found",
                    }
                }
            }, status=status.HTTP_404_NOT_FOUND)
        
        
            
        serialized_data=TaskDetailSerializer(task).data

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
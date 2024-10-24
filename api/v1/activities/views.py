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
from django.template.loader import get_template

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

from django.core.files.base import ContentFile
from django.http import HttpResponse
from xhtml2pdf import pisa
from django.template.loader import render_to_string


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
        user=request.user
        course=userprogress.chapter.course_sub_content.course
        certificate_eligible=check_certificate_eligibility(user,course)
        response_data={
            "StatusCode":6000,
            "message":"User completed this chapter",
            "certificate_eligibility":certificate_eligible
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
@permission_classes([AllowAny])
def submit_assessment(request, pk):
    try:
        # Fetch the assessment
        assessment = Assessment.objects.filter(id=pk).first()
        if not assessment:
            return Response({
                "app_data": {
                    "StatusCode": 6001,
                    "data": {
                        "title": "Failed",
                        "message": "Assessment Not Found",
                    }
                }
            }, status=status.HTTP_404_NOT_FOUND)

        # Get submitted answers
        submitted_answers = request.data.get('submit_answer', [])
        if not submitted_answers:
            return Response({
                "app_data": {
                    "StatusCode": 6001,
                    "title": "Failed",
                    "message": "No answers submitted.",
                }
            }, status=status.HTTP_400_BAD_REQUEST)

        # Check for duplicate question submission
        question_ids = [answer['question_id'] for answer in submitted_answers]
        if len(question_ids) != len(set(question_ids)):
            return Response({
                "app_data": {
                    "StatusCode": 6001,
                    "title": "Failed",
                    "message": "Duplicate questions are not allowed.",
                }
            }, status=status.HTTP_400_BAD_REQUEST)

        # Get the current user
        user = request.user

        # Check if the user has exceeded the maximum attempts
        previous_attempts = UserAssessmentAttempt.objects.filter(user=user, assessment=assessment).count()
        if previous_attempts >= assessment.max_attempts:
            return Response({
                "app_data": {
                    "StatusCode": 6001,
                    "title": "Failed",
                    "message": "Maximum attempts exceeded for this assessment.",
                }
            }, status=status.HTTP_400_BAD_REQUEST)

        # Validate questions and answers
        valid_answers = []
        total_score = 0
        max_score = 0
        wrong_answers_count = 0 

        for submitted_answer in submitted_answers:
            question_id = submitted_answer['question_id']
            answer_id = submitted_answer['answer_id']

            # Fetch the question and answer
            question = Question.objects.filter(id=question_id, assessment=assessment).first()
            answer = Answer.objects.filter(id=answer_id, question=question).first()

            if not question or not answer:
                return Response({
                    "app_data": {
                        "StatusCode": 6001,
                        "title": "Failed",
                        "message": f"Invalid question or answer: Question ID {question_id}, Answer ID {answer_id}",
                    }
                }, status=status.HTTP_400_BAD_REQUEST)

            # Determine the marks awarded
            marks_awarded = question.mark if answer.is_correct else 0
            if not answer.is_correct:
                wrong_answers_count += 1  # Increment wrong answer count if the answer is incorrect
            valid_answers.append((question, answer, marks_awarded))
            total_score += marks_awarded
            max_score += question.mark

        # Create UserAssessmentAttempt after validation
        attempt_number = previous_attempts + 1
        user_assessment_attempt = UserAssessmentAttempt.objects.create(
            user=user,
            assessment=assessment,
            attempt_number=attempt_number,
            max_score=max_score,
            total_score=total_score,  # Set the total score directly
            status='pending'  # Initially set to pending
        )

        # Create UserAnswer entries
        for question, answer, marks_awarded in valid_answers:
            UserAnswer.objects.create(
                user_attempt=user_assessment_attempt,
                question=question,
                answer=answer,
                marks_awarded=marks_awarded
            )

        # Determine pass/fail status
        user_assessment_attempt.status = 'passed' if total_score >= assessment.passing_score else 'failed'
        user_assessment_attempt.save()
        attempts_left = assessment.max_attempts - attempt_number
        course=assessment.course_sub_content.course
        certificate_eligible=check_certificate_eligibility(user,course)

        # Success response
        response_data = {
            "StatusCode": 6000,
            "title": "Success",
            "data": {
                "attempt_number": user_assessment_attempt.attempt_number,
                "total_score": user_assessment_attempt.total_score,
                "status": user_assessment_attempt.status,
                "wrong_answers_count": wrong_answers_count,  # Number of wrong answers
                "attempts_left": max(0, attempts_left),
                "certificate_eligible":certificate_eligible
            }
        }
        return Response({"app_data": response_data}, status=status.HTTP_200_OK)

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
    

  
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def submit_task(request):
    try:
        # Get the logged-in user
        user = request.user
        
        # Get task_id and submission_text from the request data
        task_id = request.data.get("task_id")
        submission_text = request.data.get("submission_text")
        links = request.data.get("link", [])
        attachment_ids = request.data.get("file", [])
        
        
        # Fetch the task
        task = Task.objects.filter(id=task_id).first()
        if not task:
            return Response({
                "app_data": {
                    "StatusCode": 6001,
                    "title": "Failed",
                    "message": "Task Not Found"
                }
            }, status=status.HTTP_404_NOT_FOUND)

        # Check if the user has already submitted the task
        existing_submission = TaskSubmission.objects.filter(user=user, task=task).exists()
        if existing_submission:
            return Response({
                "app_data": {
                    "StatusCode": 6001,
                    "title": "Failed",
                    "message": "Task already submitted."
                }
            }, status=status.HTTP_400_BAD_REQUEST)

        # Create TaskSubmission entry
        task_submission = TaskSubmission.objects.create(
            user=user,
            task=task,
            submission_text=submission_text,
            status="submitted"
        )

        # Create Attachments for the links if any are provided
        if links:
            for link in links:
                Attachment.objects.create(
                    name=link.get("title"),
                    url=link.get("link"),
                    type="link",
                    user_task_submission=task_submission
                )

        # Create Attachments for the files if any are provided
        if attachment_ids:
            for attachment_id in attachment_ids:
                try:
                    attachment = Attachment.objects.filter(id=attachment_id).first()
                    attachment.user_task_submission = task_submission
                    attachment.save()
                except Attachment.DoesNotExist:
                     return Response({
                    "app_data": {
                    "StatusCode": 6001,
                    "title": "Failed",
                    "message":  f"Attachment with id {attachment_id} does not exist."}
                    }, status=status.HTTP_400_BAD_REQUEST)
                    
        
        course=task.course_sub_content.course
        certificate_eligible=check_certificate_eligibility(user,course)
        # Success response
        response_data = {
            "StatusCode": 6000,
            "title": "Success",
            "message": "Task submitted successfully.",
            "submission_id": task_submission.id,
            "certificate_eligible":certificate_eligible
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


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def upload_file(request):
    try:
        name = request.data.get("name")
        file = request.FILES.get("file")

        if not name or not file:
            return Response({
                "app_data": {
                    "StatusCode": 6001,
                    "title": "Failed",
                    "message": "Name and File Required"
                }
            }, status=status.HTTP_400_BAD_REQUEST)

        attachment = Attachment.objects.create(name=name, file=file,type='doc')
        response_data = {
            "StatusCode": 6000,
            "title": "Success",
            "message": "File Upload successfully.",
            "attachment_id": attachment.id
        }
        return Response({"app_data": response_data}, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        transaction.rollback()  # Rollback in case of error
        response_data = {
            "StatusCode": 6001,
            "title": "Failed",
            "api": request.get_full_path(),
            "request": request.data,
            "message": str(e),
            "response": {
                e.__class__.__name__: traceback.format_exc()
            }
        }
        return Response({'app_data': response_data}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def delete_attachments(request):
    try:
        attachment_ids = request.data.get("attachment_ids", [])
        if not attachment_ids:
            return Response({
                "app_data": {
                    "StatusCode": 6001,
                    "title": "Failed",
                    "message": "Attachment Id Required"
                }
            }, status=status.HTTP_400_BAD_REQUEST)
        deleted_count, _ = Attachment.objects.filter(id__in=attachment_ids).delete()
        response_data = {
            "StatusCode": 6000,
            "title": "Success",
            "message": f"Attachments({deleted_count}) Deleted successfully.",
            
        }
        return Response({"app_data": response_data}, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        transaction.rollback()  # Rollback in case of error
        response_data = {
            "StatusCode": 6005,
            "title": "Failed",
            "api": request.get_full_path(),
            "request": request.data,
            "message": str(e),
            "response": {
                e.__class__.__name__: traceback.format_exc()
            }
        }
        return Response({'app_data': response_data}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    

def render_html(request):
    current_site = get_current_site(request)
    site_url = f'http://{current_site.domain}'
    css_url = site_url + static('css/style.css')
    logo_url = site_url + static('images/logo.png')
    left_image_url = site_url + static('images/left.png')
    right_image_url = site_url + static('images/right.png')
    context={
        'css_url': css_url,
        'logo_url': logo_url,
        'left_image_url': left_image_url,
        'right_image_url': right_image_url,

    }
    return render(request,"certificate.html",context)

from django.templatetags.static import static
from django.utils.http import urlencode
from django.contrib.sites.shortcuts import get_current_site

# @api_view(["POST"])
# @permission_classes([IsAuthenticated])
# def generate_certificate(request):
#     try:
#         user = request.user
#         if request.data.get("full_name"):
#             full_name = request.data.get('full_name')
#         else:
#             full_name=f"{user.first_name} {user.last_name}"
#         course_id = request.data.get('course_id')
        
#         # Check if course exists
#         course = Course.objects.filter(id=course_id).first()
#         sub_content=course.sub_contents.count()
#         if not course:
#             response_data = {
#                 "StatusCode": 6001,
#                 "message": "Course Not Found"
#             }
#             return Response({"app_data": response_data}, status=status.HTTP_200_OK)
        
#         # Check if the user purchased the course
#         course_purchase = CoursePurchase.objects.filter(user=user, course=course).first()
#         if not course_purchase:
#             response_data = {
#                 "StatusCode": 6001,
#                 "message": "Course Not Purchased"
#             }
#             return Response({"app_data": response_data}, status=status.HTTP_200_OK)
        
#         # Check if the user is eligible for a certificate
#         if not course_purchase.is_certificate_eligible:
#             response_data = {
#                 "StatusCode": 6001,
#                 "message": "User is not eligible for this certificate."
#             }
#             return Response({"app_data": response_data}, status=status.HTTP_200_OK)

#         # Prepare static file paths
#         current_site = get_current_site(request)
#         site_url = f'http://{current_site.domain}'
#         css_url = site_url + static('css/style.css')
#         logo_url = site_url + static('images/logo.png')
#         left_image_url = site_url + static('images/left.png')
#         right_image_url = site_url + static('images/right.png')
#         course_title=f"{course.title} ({sub_content})"

#         # Generate the certificate context
#         context = {
#             'full_name': full_name,
#             'course_title': course_title,
#             'issue_date': course_purchase.certificate_eligible_time or datetime.now().date(),
#             'css_url': css_url,
#             'logo_url': logo_url,
#             'left_image_url': left_image_url,
#             'right_image_url': right_image_url,
#             'instructor_name':course.instructor_name,
#         }
#         file_name = f"{full_name}-{course.title}.pdf"
#         template = get_template("certificate.html")
#         html = template.render(context)
        
#         # Create the PDF response
#         response = HttpResponse(content_type='application/pdf')
#         response['Content-Disposition'] = f'attachment; filename="{file_name}"'
#         pisa_status = pisa.CreatePDF(html, dest=response)
        
#         # Check for errors in PDF generation
#         if pisa_status.err:
#             response_data = {
#                 "StatusCode": 6001,
#                 "message": "Error Generating PDF."
#             }
#             return Response({"app_data": response_data}, status=status.HTTP_200_OK)
        
#         # Return the PDF for download
#         return response
    
#     except Exception as e:
#         return Response({
#             'app_data': {
#                 "StatusCode": 6001,
#                 "title": "Failed",
#                 "api": request.get_full_path(),
#                 "request": request.data,
#                 "message": str(e),
#                 "response": {
#                     e.__class__.__name__: traceback.format_exc()
#                 }
#             }
#         }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def generate_certificate(request):
    try:
        user = request.user
        if request.data.get("full_name"):
            full_name = request.data.get('full_name')
        else:
            full_name=f"{user.first_name} {user.last_name}"
        course_id = request.data.get('course_id')
        
        # Check if course exists
        course = Course.objects.filter(id=course_id).first()
        sub_content=course.sub_contents.count()
        if not course:
            response_data = {
                "StatusCode": 6001,
                "message": "Course Not Found"
            }
            return Response({"app_data": response_data}, status=status.HTTP_200_OK)
        
        # Check if the user purchased the course
        course_purchase = CoursePurchase.objects.filter(user=user, course=course).first()
        if not course_purchase:
            response_data = {
                "StatusCode": 6001,
                "message": "Course Not Purchased"
            }
            return Response({"app_data": response_data}, status=status.HTTP_200_OK)
        
        # Check if the user is eligible for a certificate
        if not course_purchase.is_certificate_eligible:
            response_data = {
                "StatusCode": 6001,
                "message": "User is not eligible for this certificate."
            }
            return Response({"app_data": response_data}, status=status.HTTP_200_OK)

        # Prepare static file paths
        current_site = get_current_site(request)
        site_url = f'http://{current_site.domain}'
        css_url = site_url + static('css/style.css')
        logo_url = site_url + static('images/logo.png')
        left_image_url = site_url + static('images/left.png')
        right_image_url = site_url + static('images/right.png')
        course_title=f"{course.title} ({sub_content})"

        # Generate the certificate context
        context = {
            'full_name': full_name,
            'course_title': course_title,
            'issue_date': course_purchase.certificate_eligible_time or datetime.now().date(),
            'css_url': css_url,
            'logo_url': logo_url,
            'left_image_url': left_image_url,
            'right_image_url': right_image_url,
            'instructor_name':course.instructor_name,
        }
        file_name = f"{full_name}-{course.title}.pdf"

        template = get_template("certificate.html")
        html = template.render(context)
        
        pdf = render_to_pdf(html)
        
        if pdf:
            response = HttpResponse(pdf, content_type='application/pdf')
            filename = file_name
            content = "inline; filename='%s'" %(filename)
            download = request.GET.get("download")
            if download:
                content = "attachment; filename='%s'" %(filename)
            response['Content-Disposition'] = content
            return response
        return HttpResponse("Not found")
    
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
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
from django.db.models import Sum
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
        latest_chapter_id = None

        if has_purchased:
            # Get the latest chapter progress of the user for this course
            latest_progress = UserProgress.objects.filter(
                user=user, 
                chapter__course_sub_content__course=course
            ).order_by('-date_added').first()  # Assuming there's a field `date_completed`

            if latest_progress:
                latest_chapter_id = latest_progress.chapter.id  # Get the chapter ID from user progress


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
                    "is_purchased":has_purchased,
                    "last_chapter_user_watched":latest_chapter_id
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
def get_chapters_of_sub_content_sidebar(request, pk):
    try:
        subcontent = CourseSubContent.objects.filter(id=pk).first()
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

        # Check the type of CourseSubContent
        if subcontent.type == 'assessment':
            # If the type is assessment, fetch related assessments
            assessments = subcontent.assessments.all().order_by("id")
            if assessments.exists():
                serialized_data = ListAssessmentSerializer(
                    assessments,
                    context={"request": request},
                    many=True
                ).data
                response_data = {
                    "StatusCode": 6000,
                    "title": "Success",
                    "data": {
                        "data": serialized_data,
                    },
                }
            else:
                response_data = {
                    "StatusCode": 6001,
                    "data": [],
                    "message": "No Assessments Found for this subcontent"
                }
        elif subcontent.type == 'task':
            # If the type is assessment, fetch related assessments
            tasks = subcontent.tasks.all().order_by("id")
            if tasks.exists():
                serialized_data = ListTaskSerializer(
                    tasks,
                    context={"request": request},
                    many=True
                ).data
                response_data = {
                    "StatusCode": 6000,
                    "title": "Success",
                    "data": {
                        "data": serialized_data,
                    },
                }
            else:
                response_data = {
                    "StatusCode": 6001,
                    "data": [],
                    "message": "No Task Found for this subcontent"
                }
        else:
            # If the type is chapter, fetch related chapters
            chapters = subcontent.chapters.filter(is_published=True).order_by("position")
            if chapters.exists():
                serialized_data = ListChapterofSubcontentSidebar(
                    chapters,
                    context={"request": request},
                    many=True
                ).data
                response_data = {
                    "StatusCode": 6000,
                    "title": "Success",
                    "data": {
                        "data": serialized_data,
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



@api_view(["GET"])
@permission_classes([AllowAny])
def get_course_detail(request,pk):
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
        
        
            
        serialized_data =ViewCourseDetailSerializer(
            course,
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


@api_view(["GET"])
@permission_classes([AllowAny])
def get_purchased_courses_list(request):
    try:
        user = request.user
        # Get the courses the user has enrolled in
        enrolled_courses = Course.objects.filter(purchases__user=user)
        
        if enrolled_courses.exists():
            paginated_data = paginate_data(enrolled_courses, request, items_per_page=10)
            serialized_data =EnrolledCourseSerializer(
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
                "message": "No Enrolled Courses found"
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
def get_assessment_details(request,pk):
    try:
        # Fetch the assessment
        assessment = Assessment.objects.filter(id=pk).first()
        if not assessment:
            return Response({
                'app_data': {
                    "StatusCode": 6001,
                    "data": {
                        "title": "Failed",
                        "message": "Assessment Not Found",
                    }
                }
            }, status=status.HTTP_404_NOT_FOUND)

        # Serialize the assessment details
        serialized_data = AssessmentDetailSerializer(
            assessment, 
            context={"request": request}
        ).data

        response_data = {
            "StatusCode": 6000,
            "title": "Success",
            "data": serialized_data,
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
                "attempts_left": max(0, attempts_left)  # Number of attempts left, ensure it's not negative
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
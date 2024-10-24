import requests
import random
import string

from django.core.mail import EmailMessage
from django.contrib.auth.models import Group
from django.conf import settings
from django.db.models import Q
from accounts.models import User
from courses.models import *
from activities.models import *
from django.utils import timezone
from io import BytesIO
from django.http import HttpResponse
from django.template.loader import get_template

from xhtml2pdf import pisa



#send otp via fast2sms

def send_otp_via_fast2sms(phone, otp):
    api_key = "PtaVjiJ8SE7PqEOMGQXMuFv6kFK5PuFv3HklcAC4QklYpAcaIkOKZjHu423V"
    url = "https://www.fast2sms.com/dev/bulkV2"
    print("phone for otp :", phone)
    print("otp :", otp)
  
    url = "https://www.fast2sms.com/dev/bulkV2"
    message_c = f"Your new  OTP for registration is {otp}. Do not share it with anyone. BY WoodenClouds Academy"

    payload = {
        'authorization': api_key ,
        'variables_values' : otp,
        "route":'otp',
        "numbers":phone,
        'message':message_c
    }
    headers = {
        'authorization': api_key,
        'Content-Type': "application/x-www-form-urlencoded",
        'Cache-Control': "no-cache",
        }

    #response = requests.request("POST", url, data=payload, headers=headers)
    response = requests.post(url, data=payload, headers=headers)

    print("Fast2SMS API response:", response.text)  # Print the response for debugging

    # Check if the request was successful (status code 200)
    if response.status_code == 200:
        return True
    else:
        return False
    
def generate_otp():
    return random.randint(1000, 9999)

def generate_random_password(max_length=15):
    chars = string.ascii_letters + string.digits + string.punctuation
    return "".join(random.choice(chars) for _ in range(max_length))

def add_user_to_group(user, group_name):
    my_group = Group.objects.get(name=group_name) 
    my_group.user_set.add(user)


def send_login_otp_via_fast2sms(phone, otp):
    api_key = "PtaVjiJ8SE7PqEOMGQXMuFv6kFK5PuFv3HklcAC4QklYpAcaIkOKZjHu423V"
    url = "https://www.fast2sms.com/dev/bulkV2"
    print("phone for otp :", phone)
    print("otp :", otp)
  
    url = "https://www.fast2sms.com/dev/bulkV2"
    message_c = f"Your new  OTP for Login is {otp}. Do not share it with anyone. BY WoodenClouds"

    payload = {
        'authorization': api_key ,
        'variables_values' : otp,
        "route":'otp',
        "numbers":phone,
        'message':message_c
    }
    headers = {
        'authorization': api_key,
        'Content-Type': "application/x-www-form-urlencoded",
        'Cache-Control': "no-cache",
        }

    #response = requests.request("POST", url, data=payload, headers=headers)
    response = requests.post(url, data=payload, headers=headers)

    print("Fast2SMS API response:", response.text)  # Print the response for debugging

    # Check if the request was successful (status code 200)
    if response.status_code == 200:
        return True
    else:
        return False
    


def check_certificate_eligibility(user, course):
    # Step 1: Check if the user has completed all chapters in the course
    all_chapters = Chapter.objects.filter(course_sub_content__course=course)
    print(all_chapters)
    completed_chapters = UserProgress.objects.filter(
        user=user, chapter__in=all_chapters, is_completed=True
    ).count()
    total_chapters = all_chapters.count()
    print(f"all chapters {total_chapters} completed chapters {completed_chapters}")

    if completed_chapters != total_chapters:
        return False  # Not all chapters are completed

    # Step 2: Check if the user has passed all assessments related to the course
    all_assessments = Assessment.objects.filter(course_sub_content__course=course)
    passed_assessments = UserAssessmentAttempt.objects.filter(
        user=user, assessment__in=all_assessments, status='passed'
    ).values('assessment').distinct().count()
    total_assessments = all_assessments.count()
    print(f"all assessments {total_assessments} passed assessments {passed_assessments}")

    if passed_assessments != total_assessments:
        return False  # Not all assessments are passed

    # Step 3: Check if the user has passed all tasks related to the course
    all_tasks = Task.objects.filter(course_sub_content__course=course)
    passed_tasks = TaskSubmission.objects.filter(
        user=user, task__in=all_tasks
    ).count()
    total_tasks = all_tasks.count()
    print(f"all tasks {total_tasks} passed task {passed_tasks}")

    if passed_tasks != total_tasks:
        return False  # Not all tasks are passed

    # If all conditions are met, set is_certificate_eligible to True for the CoursePurchase
    course_purchase = CoursePurchase.objects.filter(user=user, course=course).first()
    print(course_purchase)
    if course_purchase:
        course_purchase.is_certificate_eligible = True
        course_purchase.certificate_eligible_time=timezone.now()
        course_purchase.save()

    return True  # User is eligible for the certificate



def render_to_pdf(html):
    result = BytesIO()
    pdf = pisa.pisaDocument(BytesIO(html.encode("ISO-8859-1")), result)
    if not pdf.err:
        return HttpResponse(result.getvalue(), content_type='application/pdf')
    return None
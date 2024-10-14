import requests
import random
import string

from django.core.mail import EmailMessage
from django.contrib.auth.models import Group
from django.conf import settings



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
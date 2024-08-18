import random
import string
from datetime import datetime, timedelta
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from rest_framework_simplejwt.tokens import RefreshToken
from accounts.models import User

from django.utils.crypto import get_random_string
#from accounts.models import *
# from units.models import *
# from mashines.models import *

def generate_random_string(length=12):
    """
    Generate a random string of fixed length.
    
    Parameters:
    length (int): The length of the random string to generate. Default is 12.
    
    Returns:
    str: A random string of the specified length.
    """
    letters = string.ascii_letters + string.digits
    return ''.join(random.choice(letters) for i in range(length))

def calculate_date_difference(date1, date2):
    """
    Calculate the difference between two dates.
    
    Parameters:
    date1 (datetime): The first date.
    date2 (datetime): The second date.
    
    Returns:
    int: The difference in days between the two dates.
    """
    delta = date2 - date1
    return delta.days

def add_days_to_date(date, days):
    """
    Add a specified number of days to a date.
    
    Parameters:
    date (datetime): The original date.
    days (int): The number of days to add.
    
    Returns:
    datetime: The new date after adding the specified number of days.
    """
    return date + timedelta(days=days)

def get_current_datetime():
    """
    Get the current date and time.
    
    Returns:
    datetime: The current date and time.
    """
    return datetime.now()

def format_datetime(date_time, format="%Y-%m-%d %H:%M:%S"):
    """
    Format a datetime object into a string.
    
    Parameters:
    date_time (datetime): The datetime object to format.
    format (str): The format string. Default is "%Y-%m-%d %H:%M:%S".
    
    Returns:
    str: The formatted datetime string.
    """
    return date_time.strftime(format)

def parse_datetime(date_string, format="%Y-%m-%d %H:%M:%S"):
    """
    Parse a string into a datetime object.
    
    Parameters:
    date_string (str): The string to parse.
    format (str): The format string. Default is "%Y-%m-%d %H:%M:%S".
    
    Returns:
    datetime: The parsed datetime object.
    """
    return datetime.strptime(date_string, format)

def is_weekend(date):
    """
    Check if a given date is a weekend.
    
    Parameters:
    date (datetime): The date to check.
    
    Returns:
    bool: True if the date is a weekend, False otherwise.
    """
    return date.weekday() >= 5

def get_week_start_end(date):
    """
    Get the start and end dates of the week for a given date.
    
    Parameters:
    date (datetime): The date to find the week for.
    
    Returns:
    tuple: A tuple containing the start and end dates of the week.
    """
    start = date - timedelta(days=date.weekday())
    end = start + timedelta(days=6)
    return start, end

def generate_unique_identifier(prefix='', length=8):
    """
    Generate a unique identifier with an optional prefix.
    
    Parameters:
    prefix (str): The prefix for the unique identifier. Default is an empty string.
    length (int): The length of the unique identifier. Default is 8.
    
    Returns:
    str: The generated unique identifier.
    """
    unique_id = generate_random_string(length)
    return f"{prefix}{unique_id}"

def convert_to_utc(date_time):
    """
    Convert a datetime object to UTC.
    
    Parameters:
    date_time (datetime): The datetime object to convert.
    
    Returns:
    datetime: The datetime object converted to UTC.
    """
    return date_time.astimezone(datetime.timezone.utc)


def generate_serializer_errors(args):
    message = ""
    for key, values in args.items():
        error_message = ""
        for value in values:
            error_message += value + ","
        error_message = error_message[:-1]

        # message += "%s : %s | " %(key,error_message)
        message += f"{key} - {error_message} | "
    return message[:-3]

# def generate_unique_qr_code(self):
#     while True:
#         code = ''.join(random.choices(string.digits, k=8))
#         if not Machine.objects.filter(qr_code=code).exists():
#             return code


#function to create emp id

import random
from django.utils.crypto import get_random_string




def generate_emp_id():
    emp_id = f"HS{get_random_string(length=6, allowed_chars='0123456789')}"
    return emp_id




#pagination
def paginate_data(instances, request, items_per_page=2):
    paginator = Paginator(instances, items_per_page)
    page = request.GET.get('page')

    try:
        instances = paginator.page(page)
    except PageNotAnInteger:
        instances = paginator.page(1)
    except EmptyPage:
        instances = paginator.page(paginator.num_pages)

    next_page_number = 1
    has_next_page = False
    if instances.has_next():
        has_next_page = True
        next_page_number = instances.next_page_number()

    has_previous_page = False
    previous_page_number = 1
    if instances.has_previous():
        has_previous_page = True
        previous_page_number = instances.previous_page_number()

    return {
        'instances': instances,
        'has_next_page': has_next_page,
        'next_page_number': next_page_number,
        'has_previous_page': has_previous_page,
        'previous_page_number': previous_page_number,
        'total_pages': paginator.num_pages,
        'total_items': paginator.count,
        'first_item': instances.start_index(),
        'last_item': instances.end_index(),
    }
    
    
def get_user_login_credentials(user:User):
    refresh = RefreshToken.for_user(user)
    access_token = str(refresh.access_token)
    refresh_token = str(refresh)
    
    return {
        "access_token":access_token,
        "refresh_token":refresh_token,
    }
from functools import wraps
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
import json

from django.contrib.auth.decorators import user_passes_test
from django.http.response import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.urls import reverse
from rest_framework.response import Response
from functools import wraps
from django.http import HttpResponseForbidden


def json_response_decorator(func):
    """
    Decorator to convert a view's response to JSON.
    """
    @wraps(func)
    def wrapper(request, *args, **kwargs):
        response = func(request, *args, **kwargs)
        if isinstance(response, dict):
            return JsonResponse(response)
        return response
    return wrapper

def csrf_exempt_decorator(func):
    """
    Decorator to exempt a view from CSRF verification.
    """
    return method_decorator(csrf_exempt, name='dispatch')(func)

def require_http_methods_decorator(methods):
    """
    Decorator to restrict a view to certain HTTP methods.
    
    Parameters:
    methods (list): List of allowed HTTP methods.
    """
    def decorator(func):
        @wraps(func)
        def wrapper(request, *args, **kwargs):
            if request.method not in methods:
                return JsonResponse({'error': 'Method not allowed'}, status=405)
            return func(request, *args, **kwargs)
        return wrapper
    return decorator


def group_required(group_names):
    def _method_wrapper(view_method):
        def _arguments_wrapper(request, *args, **kwargs):
            if request.user.is_authenticated:
                if not (request.user.groups.filter(name__in=group_names).exists() or request.user.is_superuser):
                    if request.is_ajax():
                        response_data = {
                            "status": "false",
                            "stable": "true",
                            "title": "Permission Denied",
                            "message": "You have no permission to do this action."
                        }
                        return HttpResponse(
                            json.dumps(response_data),
                            content_type="application/javascript",
                        )
                    else:
                        return HttpResponse("<h1>Permission Denied</h1>")
            return view_method(request, *args, **kwargs)

        return _arguments_wrapper

    return _method_wrapper
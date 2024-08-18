from django.utils.deprecation import MiddlewareMixin
from django.http import JsonResponse

class JsonResponseMiddleware(MiddlewareMixin):
    """
    Middleware to ensure all responses are JSON.
    """
    def process_response(self, request, response):
        if isinstance(response, dict):
            return JsonResponse(response)
        return response

class CsrfExemptMiddleware(MiddlewareMixin):
    """
    Middleware to exempt certain views from CSRF verification.
    """
    def process_view(self, request, callback, callback_args, callback_kwargs):
        if getattr(callback, 'csrf_exempt', False):
            request.csrf_processing_done = True
        return None

class HttpMethodRestrictionMiddleware(MiddlewareMixin):
    """
    Middleware to restrict views to certain HTTP methods.
    """
    def process_view(self, request, callback, callback_args, callback_kwargs):
        allowed_methods = getattr(callback, 'allowed_methods', None)
        if allowed_methods and request.method not in allowed_methods:
            return JsonResponse({'error': 'Method not allowed'}, status=405)
        return None

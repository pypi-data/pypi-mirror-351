"""
Django middleware integration for Loggier with optimized logging (one log entry per request).
"""
import uuid
import time
import json
import functools
from typing import Dict, List, Any, Optional, Union, Callable, Set

from django.conf import settings
from django.http import HttpRequest, HttpResponse

# Import Loggier client
from ..client import Loggier

# Global Loggier instance for the middleware
_loggier_instance = None

# Registry for decorated views
_tracked_views = set()


def track_endpoint(tags=None, statuses=None, capture_request_body=False, capture_response_body=False):
    """
    Decorator to track specific endpoints.
    
    Args:
        tags: Additional tags for this endpoint
        statuses: Status codes to track (defaults to all)
        capture_request_body: Whether to capture the full request body (careful with sensitive data)
        capture_response_body: Whether to capture the full response body
        
    Example:
        @track_endpoint(tags=['critical', 'payment'])
        def my_view(request):
            ...
    """
    def decorator(view_func):
        # Register this view function for tracking
        _tracked_views.add(view_func)
        
        # Store tracking options on the function
        view_func._loggier_track_options = {
            'tags': tags or [],
            'statuses': statuses or [],
            'capture_request_body': capture_request_body,
            'capture_response_body': capture_response_body
        }
        
        @functools.wraps(view_func)
        def wrapped_view(*args, **kwargs):
            return view_func(*args, **kwargs)
        
        return wrapped_view
    
    return decorator


class LoggierDjangoMiddleware:
    """
    Django middleware for Loggier integration with optimized logging (one log entry per request).
    
    Add to your Django MIDDLEWARE setting:
    
    MIDDLEWARE = [
        ...
        'loggier.integrations.django.LoggierDjangoMiddleware',
        ...
    ]
    
    And configure in settings.py:
    
    LOGGIER = {
        'API_KEY': 'your-api-key',
        'API_URL': 'https://api.loggier.com/api/ingest',
        'ENVIRONMENT': 'development',
        'TAGS': ['django', 'web'],
        'PROJECT_NAME': 'your-project',
        'CAPTURE_REQUEST_DATA': True,
        'LOG_SLOW_REQUESTS': True,
        'SLOW_REQUEST_THRESHOLD': 1.0,  # seconds
        'STATUSES_TO_TRACK': [500, 400, 401, 403],  # Status codes to track
        'CAPTURE_REQUEST_BODY': False,  # Capture request body for tracked statuses
        'CAPTURE_RESPONSE_BODY': True,  # Capture response body for tracked statuses
        'MAX_BODY_SIZE': 16384,  # Max body size to capture (16KB)
        'INCLUDE_STACKTRACE': True  # Include stacktrace for errors
    }
    """
    
    def __init__(self, get_response):
        """
        Initialize the middleware.
        
        Args:
            get_response: The next middleware or view in the chain
        """
        self.get_response = get_response
        
        # Get configuration from Django settings
        config = getattr(settings, "LOGGIER", {})
        
        # Create or get global Loggier instance
        global _loggier_instance
        if _loggier_instance is None:
            _loggier_instance = Loggier(
                api_key=config.get("API_KEY"),
                api_url=config.get("API_URL"),
                project_name=config.get("PROJECT_NAME"),
                environment=config.get("ENVIRONMENT", "development"),
                async_mode=config.get("ASYNC_MODE", True),
                max_batch_size=config.get("MAX_BATCH_SIZE", 100),
                flush_interval=config.get("FLUSH_INTERVAL", 5),
                tags=config.get("TAGS", [])
            )
            
            # Add Django information to global context
            _loggier_instance.context.update_global({
                "framework": "django",
                "django_debug": getattr(settings, "DEBUG", False)
            })
        
        self.logger = _loggier_instance
        
        # Middleware configuration
        self.capture_request_data = config.get("CAPTURE_REQUEST_DATA", True)
        self.log_slow_requests = config.get("LOG_SLOW_REQUESTS", True)
        self.slow_request_threshold = config.get("SLOW_REQUEST_THRESHOLD", 1.0)
        
        # Status codes to track - default to server errors only if not specified
        self.statuses_to_track = set(config.get("STATUSES_TO_TRACK", [500]))
        
        # Body capturing settings
        self.capture_request_body = config.get("CAPTURE_REQUEST_BODY", False)
        self.capture_response_body = config.get("CAPTURE_RESPONSE_BODY", True)
        self.max_body_size = config.get("MAX_BODY_SIZE", 16384)  # 16KB default
        self.include_stacktrace = config.get("INCLUDE_STACKTRACE", True)
    
    def __call__(self, request):
        """
        Process the request and response.
        
        Args:
            request: Django HTTP request
            
        Returns:
            Django HTTP response
        """
        # Check if this is a decorated view that should be tracked
        view_func = None
        is_tracked_view = False
        track_options = {}
        
        # Safely check resolver_match and func
        if hasattr(request, 'resolver_match') and request.resolver_match is not None:
            if hasattr(request.resolver_match, 'func'):
                view_func = request.resolver_match.func
                is_tracked_view = view_func in _tracked_views if view_func else False
                track_options = getattr(view_func, '_loggier_track_options', {}) if is_tracked_view else {}
        
        # Generate request ID and record start time
        request_id = str(uuid.uuid4())
        request.loggier_request_id = request_id
        request.loggier_start_time = time.time()
        
        # Update global context with request ID
        self.logger.context.update_global({"request_id": request_id})
        
        # Determine if we should log this request
        should_log_request = is_tracked_view or self.capture_request_data
        
        # Collect request data if needed
        request_data = None
        if should_log_request:
            # Check if we should capture the request body
            capture_req_body = track_options.get('capture_request_body', self.capture_request_body)
            
            # Collect comprehensive request data
            request_data = self._collect_request_data(request, include_body=capture_req_body)
            
            # Add any decorator tags
            decorator_tags = track_options.get('tags', [])
            if decorator_tags:
                self.logger.context.update_global({"endpoint_tags": decorator_tags})
                
        # Get response (try/except to catch exceptions)
        exception_occurred = False
        exception_info = {}
        
        try:
            response = self.get_response(request)
        except Exception as exc:
            # Process exception
            exception_occurred = True
            
            # Get exception details including full traceback
            import traceback
            exception_info = {
                "type": exc.__class__.__name__,
                "message": str(exc),
            }
            
            if self.include_stacktrace:
                exception_info["traceback"] = "".join(traceback.format_exception(type(exc), exc, exc.__traceback__))
            
            # Re-raise the exception after collecting info
            raise
        finally:
            # Only log the request if we should and if we have timing info
            if should_log_request and hasattr(request, "loggier_start_time"):
                # Calculate request time
                request_time = time.time() - request.loggier_start_time
                
                # Check if we should log due to slow request
                is_slow = self.log_slow_requests and request_time > self.slow_request_threshold
                
                if exception_occurred:
                    # If an exception occurred, always log
                    should_record_log = True
                    log_level = "error"
                    status_code = 500  # Assumed server error
                    
                    # Build log message
                    log_message = f"Exception during request: {request.method} {request.path}"
                    
                    # Start building log context
                    log_context = request_data.copy() if request_data else self._collect_request_data(request)
                    log_context["exception"] = exception_info
                    log_context["request_time"] = request_time
                else:
                    # Get status code from response
                    status_code = response.status_code
                    
                    # Get view-specific statuses to track
                    view_statuses = set(track_options.get('statuses', []))
                    track_statuses = self.statuses_to_track.union(view_statuses)
                    
                    # Determine if this status code should be tracked
                    status_tracked = status_code in track_statuses
                    
                    # Decide if we should log this request based on criteria
                    should_record_log = is_slow or status_tracked or is_tracked_view
                    
                    if should_record_log:
                        # Check if we should capture the response body
                        capture_resp_body = track_options.get('capture_response_body', self.capture_response_body)
                        
                        # Get comprehensive response data
                        resp_data = self._collect_response_data(request, response, request_time, include_body=capture_resp_body)
                        
                        # Build log context
                        if request_data is None:
                            request_data = self._collect_request_data(request)
                        
                        # Combine into a single unified log context
                        log_context = {
                            "request": request_data,
                            "response": resp_data,
                            "request_time": request_time
                        }
                        
                        # Determine log level based on status code
                        if 200 <= status_code < 400:
                            log_level = "info"
                            log_message = f"Request completed: {request.method} {request.path} - {status_code}"
                        elif 400 <= status_code < 500:
                            log_level = "warning"
                            log_message = f"Client error: {request.method} {request.path} - {status_code}"
                        else:  # 500+
                            log_level = "error"
                            log_message = f"Server error: {request.method} {request.path} - {status_code}"
                
                # Log the request with appropriate level if needed
                if should_record_log:
                    if log_level == "info":
                        self.logger.info(log_message, context=log_context)
                    elif log_level == "warning":
                        self.logger.warning(log_message, context=log_context)
                    elif log_level == "error":
                        self.logger.error(log_message, context=log_context, exception=exception_info if exception_occurred else None)
            
            # Clear the global context for the next request
            try:
                # Get the current global context
                global_context = self.logger.context.get_global()
                
                # Clear specific keys in global context
                if global_context and "request_id" in global_context:
                    self.logger.context.update_global({"request_id": None})
                if global_context and "endpoint_tags" in global_context:
                    self.logger.context.update_global({"endpoint_tags": None})
            except TypeError:
                # Handle the case where get_global() requires a key argument
                try:
                    # Try to get and clear request_id
                    request_id = self.logger.context.get_global("request_id")
                    if request_id is not None:
                        self.logger.context.update_global({"request_id": None})
                    
                    # Try to get and clear endpoint_tags
                    endpoint_tags = self.logger.context.get_global("endpoint_tags")
                    if endpoint_tags is not None:
                        self.logger.context.update_global({"endpoint_tags": None})
                except Exception:
                    # If all else fails, just continue without clearing context
                    pass
        
        # Return the response if no exception occurred
        if not exception_occurred:
            return response
    
    def _collect_request_data(self, request, include_body=False):
        """
        Collect comprehensive data from the request object.
        
        Args:
            request: Django HTTP request
            include_body: Whether to include the request body
            
        Returns:
            dict: Request data dictionary
        """
        # Basic request data
        req_data = {
            "method": request.method,
            "path": request.path,
            "full_path": request.get_full_path(),
            "scheme": request.scheme if hasattr(request, 'scheme') else None,
            "remote_addr": request.META.get("REMOTE_ADDR", ""),
            "user_agent": request.META.get("HTTP_USER_AGENT", ""),
            "referer": request.META.get("HTTP_REFERER", ""),
        }
        
        # Add user info if available
        if hasattr(request, "user") and request.user.is_authenticated:
            user_data = {
                "user_id": request.user.id,
                "username": getattr(request.user, 'username', str(request.user)),
                "email": getattr(request.user, 'email', None),
            }
            req_data["user"] = user_data
        
        # Add query parameters if present
        if request.GET:
            req_data["query_params"] = self._filter_sensitive_data(dict(request.GET.items()))
        
        # Add request headers (filtered)
        headers = {}
        for key, value in request.META.items():
            if key.startswith('HTTP_') and not self._is_sensitive_field(key):
                header_name = key[5:].lower().replace('_', '-')
                headers[header_name] = value
        if headers:
            req_data["headers"] = headers
        
        # Add content type and length
        if 'CONTENT_TYPE' in request.META:
            req_data['content_type'] = request.META['CONTENT_TYPE']
        if 'CONTENT_LENGTH' in request.META:
            req_data['content_length'] = request.META['CONTENT_LENGTH']
        
        # Add POST data if appropriate (and not sensitive)
        if include_body and request.method in ['POST', 'PUT', 'PATCH']:
            # Handle different types of request bodies
            body_data = None
            
            # For regular form data
            if hasattr(request, 'POST') and request.POST:
                body_data = self._filter_sensitive_data(dict(request.POST.items()))
            
            # For JSON data
            elif request.content_type == 'application/json' and hasattr(request, 'body'):
                try:
                    json_data = json.loads(request.body.decode('utf-8'))
                    body_data = self._filter_sensitive_data(json_data)
                except Exception:
                    # If we can't parse JSON, include raw body up to max size
                    try:
                        body_data = request.body.decode('utf-8', errors='replace')[:self.max_body_size]
                    except Exception:
                        body_data = "[Unable to decode request body]"
            
            # For other body types, include raw body up to max size if needed
            elif hasattr(request, 'body') and request.body:
                try:
                    body_data = request.body.decode('utf-8', errors='replace')[:self.max_body_size]
                    if len(request.body) > self.max_body_size:
                        body_data += "... [truncated]"
                except Exception:
                    body_data = "[Binary data not shown]"
            
            if body_data is not None:
                req_data["body"] = body_data
        
        # Add view information if available
        if hasattr(request, 'resolver_match') and request.resolver_match:
            view_info = {
                "function": request.resolver_match.view_name,
                "url_name": request.resolver_match.url_name,
                "app_name": request.resolver_match.app_name,
                "namespace": request.resolver_match.namespace,
            }
            
            # Add route pattern if available
            if hasattr(request.resolver_match, 'route'):
                view_info["route"] = request.resolver_match.route
            
            # Add arguments and keyword arguments (filtered)
            if request.resolver_match.args:
                view_info["args"] = request.resolver_match.args
            
            if request.resolver_match.kwargs:
                view_info["kwargs"] = self._filter_sensitive_data(request.resolver_match.kwargs)
            
            req_data["view"] = view_info
        
        # Add files if present
        if hasattr(request, 'FILES') and request.FILES:
            files_info = {}
            for name, file_obj in request.FILES.items():
                files_info[name] = {
                    "name": file_obj.name,
                    "size": file_obj.size,
                    "content_type": file_obj.content_type,
                }
            req_data["files"] = files_info
        
        return req_data
    
    def _collect_response_data(self, request, response, request_time, include_body=False):
        """
        Collect comprehensive data from the response object.
        
        Args:
            request: Django HTTP request
            response: Django HTTP response
            request_time: Request processing time in seconds
            include_body: Whether to include the response body
            
        Returns:
            dict: Response data dictionary
        """
        # Basic response data
        resp_data = {
            "status_code": response.status_code,
            "request_time": round(request_time, 4),
        }
        
        # Add response reason phrase if available
        if hasattr(response, 'reason_phrase') and response.reason_phrase:
            resp_data["reason_phrase"] = response.reason_phrase
        
        # Add headers if available (non-sensitive only)
        if hasattr(response, "headers"):
            headers = {}
            for key, value in response.headers.items():
                if not self._is_sensitive_field(key):
                    headers[key.lower()] = value
            if headers:
                resp_data["headers"] = headers
        
        # Add content type if available
        resp_data["content_type"] = response.get("Content-Type", "")
        
        # Add content length if available
        if hasattr(response, "content"):
            resp_data["content_length"] = len(response.content)
        
        # Add response body for tracked statuses or if explicitly requested
        if include_body and hasattr(response, "content"):
            content_type = response.get("Content-Type", "")
            
            # Handle different content types
            if 'application/json' in content_type:
                try:
                    # Try to parse as JSON
                    body_data = json.loads(response.content.decode('utf-8'))
                    resp_data["body"] = self._filter_sensitive_data(body_data)
                except Exception:
                    # Fallback to raw content
                    resp_data["body"] = response.content.decode('utf-8', errors='replace')[:self.max_body_size]
            elif 'text/' in content_type:
                # Text content
                resp_data["body"] = response.content.decode('utf-8', errors='replace')[:self.max_body_size]
                if len(response.content) > self.max_body_size:
                    resp_data["body"] += "... [truncated]"
            elif include_body:
                # For binary content, just note the size
                resp_data["body"] = f"[Binary content, {len(response.content)} bytes]"
        
        # For error responses, try to parse Django debug info
        if response.status_code >= 400 and hasattr(response, "content"):
            try:
                content = response.content.decode('utf-8', errors='replace')
                
                # Look for Django traceback
                if 'Traceback (most recent call last)' in content:
                    # Extract traceback - simple approach, could be improved
                    start_idx = content.find('Traceback (most recent call last)')
                    if start_idx >= 0:
                        end_idx = content.find('\n\n', start_idx)
                        if end_idx >= 0:
                            traceback = content[start_idx:end_idx].strip()
                            resp_data["traceback"] = traceback
                
                # Look for exception type and value
                if 'Exception Type:' in content and 'Exception Value:' in content:
                    exc_type_start = content.find('Exception Type:') + len('Exception Type:')
                    exc_type_end = content.find('\n', exc_type_start)
                    exc_value_start = content.find('Exception Value:') + len('Exception Value:')
                    exc_value_end = content.find('\n', exc_value_start)
                    
                    if exc_type_end >= 0 and exc_value_end >= 0:
                        exc_type = content[exc_type_start:exc_type_end].strip()
                        exc_value = content[exc_value_start:exc_value_end].strip()
                        
                        resp_data["exception"] = {
                            "type": exc_type,
                            "value": exc_value
                        }
            except Exception:
                # If parsing fails, continue without the extra info
                pass
        
        return resp_data
    
    def _filter_sensitive_data(self, data):
        """
        Filter sensitive data from dictionaries.
        
        Args:
            data: Dictionary to filter
            
        Returns:
            dict: Filtered dictionary
        """
        if not isinstance(data, dict):
            return data
        
        filtered = {}
        for key, value in data.items():
            if self._is_sensitive_field(key):
                filtered[key] = "[FILTERED]"
            elif isinstance(value, dict):
                filtered[key] = self._filter_sensitive_data(value)
            else:
                filtered[key] = value
        return filtered
    
    def _is_sensitive_field(self, field_name):
        """
        Check if a field name contains sensitive information.
        
        Args:
            field_name: Field name to check
            
        Returns:
            bool: True if the field is sensitive
        """
        sensitive_keywords = [
            "password", "token", "auth", "secret", "key", "cookie", 
            "csrf", "session", "card", "credit", "cvv", "ssn", "social",
            "security", "private", "api_key", "apikey", "access_token",
            "refresh_token", "authorization"
        ]
        field_lower = str(field_name).lower()
        return any(keyword in field_lower for keyword in sensitive_keywords)


# Backward compatibility class for legacy applications
class LoggierDjango:
    """
    Legacy Django integration class for backward compatibility.
    For new projects, use LoggierDjangoMiddleware directly.
    """
    
    def __init__(self, **kwargs):
        """Initialize Django integration with a configuration."""
        # Just a compatibility wrapper that returns the middleware
        pass
    
    def get_middleware(self):
        """
        Get a middleware class for use in Django MIDDLEWARE setting.
        Returns a reference to the optimized middleware class.
        """
        return LoggierDjangoMiddleware
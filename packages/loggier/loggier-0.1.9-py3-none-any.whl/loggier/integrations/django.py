"""
Django middleware integration for Loggier with improved exception handling.
"""
import uuid
import time
import json
import functools
import traceback
import sys
from typing import Dict, List, Any, Optional, Union, Callable, Set

from django.conf import settings
from django.http import HttpRequest, HttpResponse

# Import Loggier client
from ..client import Loggier
from ..utils.error import format_exception_for_logging

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
    Django middleware for Loggier integration with improved exception handling.
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
        enable_console_logging = config.get("ENABLE_CONSOLE_LOGGING", False)

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
                tags=config.get("TAGS", []),
                enable_caching=config.get("ENABLE_CACHING", True),
                sensitive_fields=config.get("SENSITIVE_FIELDS", None),
                enable_console_logging=config.get("ENABLE_CONSOLE_LOGGING", False),
                enable_performance_monitoring=config.get("ENABLE_PERFORMANCE_MONITORING", False)
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

        self.enable_console_logging = enable_console_logging

        # Debug mesajı sadece console logging aktifse
        if self.enable_console_logging:
            print(f"[LOGGIER-DJANGO] Middleware initialized with console logging: {enable_console_logging}")

    def __call__(self, request):
        """
        Process the request and response with improved exception handling.

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

        # Process request and handle exceptions properly
        exception_occurred = False
        exception_info = {}
        response = None

        try:
            response = self.get_response(request)
            return response

        except Exception as exc:
            exception_occurred = True

            # Get detailed exception information using our helper function
            exception_info = format_exception_for_logging(exc)

            # Add request-specific context to exception
            exception_info["request_context"] = {
                "method": request.method,
                "path": request.path,
                "user": str(getattr(request, 'user', 'Anonymous')),
                "remote_addr": request.META.get("REMOTE_ADDR", "unknown"),
                "user_agent": request.META.get("HTTP_USER_AGENT", "unknown")[:200]  # Limit length
            }

            # Log the exception immediately
            self._log_exception(request, exc, exception_info, request_data)

            # Re-raise the exception to let Django handle it
            raise

        finally:
            # Log request completion if needed
            if should_log_request and hasattr(request, "loggier_start_time"):
                self._log_request_completion(
                    request, response, exception_occurred, exception_info,
                    request_data, track_options, is_tracked_view
                )

            # Clean up global context
            self._cleanup_context()

    def _log_exception(self, request, exception, exception_info, request_data):
        """
        Log exception with full context and traceback.
        """
        try:
            # Calculate request time
            request_time = time.time() - getattr(request, "loggier_start_time", time.time())

            # Build comprehensive context
            log_context = {
                "request": request_data or self._collect_request_data(request),
                "exception_details": exception_info,
                "request_time": request_time,
                "django_debug": getattr(settings, "DEBUG", False)
            }

            # Add current stack trace if different from exception
            try:
                current_stack = traceback.format_stack()
                log_context["current_stack"] = ''.join(current_stack[-10:])  # Last 10 frames
            except:
                pass

            # Log with error level
            message = f"Exception during request: {request.method} {request.path} - {exception.__class__.__name__}: {str(exception)}"

            self.logger.error(
                message,
                exception=exception,
                context=log_context
            )

        except Exception as log_error:
            # If logging fails, try a minimal log
            try:
                self.logger.error(
                    f"Exception during request (logging error: {str(log_error)}): {request.method} {request.path}",
                    exception=exception,
                    context={"logging_error": str(log_error)}
                )
            except:
                # Last resort - console logging aktifse stderr'a yaz
                if self.enable_console_logging:
                    print(f"[LOGGIER-DJANGO] CRITICAL ERROR: Could not log exception: {exception}", file=sys.stderr)

    def _log_request_completion(self, request, response, exception_occurred, exception_info, request_data,
                                track_options, is_tracked_view):
        """
        Log request completion with proper exception handling.
        """
        try:
            request_time = time.time() - request.loggier_start_time

            if exception_occurred:
                # Exception was already logged in _log_exception
                return

            # Get status code from response
            status_code = getattr(response, 'status_code', 500) if response else 500

            # Get view-specific statuses to track
            view_statuses = set(track_options.get('statuses', []))
            track_statuses = self.statuses_to_track.union(view_statuses)

            # Determine if this status code should be tracked
            status_tracked = status_code in track_statuses

            # Check if request is slow
            is_slow = self.log_slow_requests and request_time > self.slow_request_threshold

            # Decide if we should log this request
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
                    "request_time": request_time,
                    "performance": {
                        "is_slow": is_slow,
                        "threshold": self.slow_request_threshold
                    }
                }

                # Determine log level and message based on status code
                if 200 <= status_code < 400:
                    log_level = "info"
                    message = f"Request completed: {request.method} {request.path} - {status_code}"
                elif 400 <= status_code < 500:
                    log_level = "warning"
                    message = f"Client error: {request.method} {request.path} - {status_code}"
                else:  # 500+
                    log_level = "error"
                    message = f"Server error: {request.method} {request.path} - {status_code}"

                # Add slow request indicator
                if is_slow:
                    message += f" [SLOW: {request_time:.2f}s]"

                # Log the request
                if log_level == "info":
                    self.logger.info(message, context=log_context)
                elif log_level == "warning":
                    self.logger.warning(message, context=log_context)
                elif log_level == "error":
                    self.logger.error(message, context=log_context)

        except Exception as log_error:
            # If logging fails, try minimal logging
            try:
                self.logger.error(
                    f"Failed to log request completion: {str(log_error)}",
                    context={"logging_error": str(log_error), "request_path": request.path}
                )
            except:
                print(f"LOGGIER ERROR: Could not log request completion: {log_error}", file=sys.stderr)

    def _cleanup_context(self):
        """
        Clean up global context for the next request.
        """
        try:
            # Clear specific keys in global context
            self.logger.context.update_global({"request_id": None})
            self.logger.context.update_global({"endpoint_tags": None})
        except Exception:
            # If cleanup fails, continue without cleanup
            pass

    def _collect_request_data(self, request, include_body=False):
        """
        Collect comprehensive data from the request object with better error handling.
        """
        try:
            # Basic request data
            req_data = {
                "method": request.method,
                "path": request.path,
                "full_path": request.get_full_path(),
                "scheme": getattr(request, 'scheme', 'unknown'),
                "remote_addr": request.META.get("REMOTE_ADDR", ""),
                "user_agent": request.META.get("HTTP_USER_AGENT", "")[:500],  # Limit length
                "referer": request.META.get("HTTP_REFERER", ""),
            }

            # Add user info if available
            try:
                if hasattr(request, "user") and request.user.is_authenticated:
                    user_data = {
                        "user_id": getattr(request.user, 'id', None),
                        "username": getattr(request.user, 'username', str(request.user)),
                        "email": getattr(request.user, 'email', None),
                    }
                    req_data["user"] = user_data
            except Exception as e:
                req_data["user_error"] = str(e)

            # Add query parameters if present
            try:
                if request.GET:
                    req_data["query_params"] = self._filter_sensitive_data(dict(request.GET.items()))
            except Exception as e:
                req_data["query_params_error"] = str(e)

            # Add request headers (filtered)
            try:
                headers = {}
                for key, value in request.META.items():
                    if key.startswith('HTTP_') and not self._is_sensitive_field(key):
                        header_name = key[5:].lower().replace('_', '-')
                        headers[header_name] = str(value)[:200]  # Limit header value length
                if headers:
                    req_data["headers"] = headers
            except Exception as e:
                req_data["headers_error"] = str(e)

            # Add content type and length
            try:
                if 'CONTENT_TYPE' in request.META:
                    req_data['content_type'] = request.META['CONTENT_TYPE']
                if 'CONTENT_LENGTH' in request.META:
                    req_data['content_length'] = request.META['CONTENT_LENGTH']
            except Exception as e:
                req_data["content_info_error"] = str(e)

            # Add POST data if appropriate
            if include_body and request.method in ['POST', 'PUT', 'PATCH']:
                try:
                    body_data = self._extract_request_body(request)
                    if body_data is not None:
                        req_data["body"] = body_data
                except Exception as e:
                    req_data["body_error"] = str(e)

            # Add view information if available
            try:
                if hasattr(request, 'resolver_match') and request.resolver_match:
                    view_info = {
                        "function": getattr(request.resolver_match, 'view_name', 'unknown'),
                        "url_name": getattr(request.resolver_match, 'url_name', 'unknown'),
                        "app_name": getattr(request.resolver_match, 'app_name', 'unknown'),
                        "namespace": getattr(request.resolver_match, 'namespace', 'unknown'),
                    }

                    # Add route pattern if available
                    if hasattr(request.resolver_match, 'route'):
                        view_info["route"] = str(request.resolver_match.route)

                    # Add arguments safely
                    if hasattr(request.resolver_match, 'args') and request.resolver_match.args:
                        view_info["args"] = [str(arg) for arg in request.resolver_match.args]

                    if hasattr(request.resolver_match, 'kwargs') and request.resolver_match.kwargs:
                        view_info["kwargs"] = self._filter_sensitive_data(request.resolver_match.kwargs)

                    req_data["view"] = view_info
            except Exception as e:
                req_data["view_error"] = str(e)

            # Add files if present
            try:
                if hasattr(request, 'FILES') and request.FILES:
                    files_info = {}
                    for name, file_obj in request.FILES.items():
                        files_info[name] = {
                            "name": getattr(file_obj, 'name', 'unknown'),
                            "size": getattr(file_obj, 'size', 0),
                            "content_type": getattr(file_obj, 'content_type', 'unknown'),
                        }
                    req_data["files"] = files_info
            except Exception as e:
                req_data["files_error"] = str(e)

            return req_data

        except Exception as e:
            # If everything fails, return minimal data
            return {
                "method": getattr(request, 'method', 'unknown'),
                "path": getattr(request, 'path', 'unknown'),
                "collection_error": str(e)
            }

    def _extract_request_body(self, request):
        """
        Safely extract request body data.
        """
        try:
            # For regular form data
            if hasattr(request, 'POST') and request.POST:
                return self._filter_sensitive_data(dict(request.POST.items()))

            # For JSON data
            if hasattr(request, 'content_type') and 'application/json' in str(request.content_type):
                if hasattr(request, 'body'):
                    try:
                        json_data = json.loads(request.body.decode('utf-8'))
                        return self._filter_sensitive_data(json_data)
                    except json.JSONDecodeError:
                        # If JSON parsing fails, return raw body (truncated)
                        try:
                            return request.body.decode('utf-8', errors='replace')[:self.max_body_size]
                        except:
                            return "[Could not decode request body]"

            # For other body types, include raw body up to max size if needed
            elif hasattr(request, 'body') and request.body:
                try:
                    body_str = request.body.decode('utf-8', errors='replace')[:self.max_body_size]
                    if len(request.body) > self.max_body_size:
                        body_str += "... [truncated]"
                    return body_str
                except Exception:
                    return "[Binary data not shown]"

            return None

        except Exception as e:
            return f"[Error extracting body: {str(e)}]"

    def _collect_response_data(self, request, response, request_time, include_body=False):
        """
        Collect comprehensive data from the response object with better error handling.
        """
        try:
            if response is None:
                return {"error": "No response received", "request_time": round(request_time, 4)}

            # Basic response data
            resp_data = {
                "status_code": getattr(response, 'status_code', 500),
                "request_time": round(request_time, 4),
            }

            # Add response reason phrase if available
            try:
                if hasattr(response, 'reason_phrase') and response.reason_phrase:
                    resp_data["reason_phrase"] = str(response.reason_phrase)
            except Exception as e:
                resp_data["reason_phrase_error"] = str(e)

            # Add headers if available (non-sensitive only)
            try:
                if hasattr(response, "headers"):
                    headers = {}
                    for key, value in response.headers.items():
                        if not self._is_sensitive_field(key):
                            headers[key.lower()] = str(value)[:200]  # Limit header length
                    if headers:
                        resp_data["headers"] = headers
                elif hasattr(response, '_headers'):
                    # Django HttpResponse._headers format
                    headers = {}
                    for key, (header_name, value) in response._headers.items():
                        if not self._is_sensitive_field(key):
                            headers[key.lower()] = str(value)[:200]
                    if headers:
                        resp_data["headers"] = headers
            except Exception as e:
                resp_data["headers_error"] = str(e)

            # Add content type if available
            try:
                content_type = ""
                if hasattr(response, "get") and callable(response.get):
                    content_type = response.get("Content-Type", "")
                elif hasattr(response, "_headers") and "content-type" in response._headers:
                    content_type = response._headers["content-type"][1]
                resp_data["content_type"] = content_type
            except Exception as e:
                resp_data["content_type_error"] = str(e)

            # Add content length if available
            try:
                if hasattr(response, "content"):
                    resp_data["content_length"] = len(response.content)
                elif hasattr(response, "_container"):
                    # Try to estimate content length from container
                    try:
                        total_length = sum(len(chunk) for chunk in response._container if chunk)
                        resp_data["content_length"] = total_length
                    except:
                        resp_data["content_length"] = "unknown"
            except Exception as e:
                resp_data["content_length_error"] = str(e)

            # Add response body for tracked statuses or if explicitly requested
            if include_body:
                try:
                    resp_data["body"] = self._extract_response_body(response)
                except Exception as e:
                    resp_data["body_error"] = str(e)

            # For error responses, try to parse Django debug info
            if response and getattr(response, 'status_code', 500) >= 400:
                try:
                    resp_data["error_details"] = self._extract_error_details(response)
                except Exception as e:
                    resp_data["error_extraction_error"] = str(e)

            return resp_data

        except Exception as e:
            # If everything fails, return minimal data
            return {
                "status_code": getattr(response, 'status_code', 500) if response else 500,
                "request_time": round(request_time, 4),
                "collection_error": str(e)
            }

    def _extract_response_body(self, response):
        """
        Safely extract response body.
        """
        try:
            if not hasattr(response, "content"):
                return "[No content available]"

            content_type = ""
            try:
                if hasattr(response, "get") and callable(response.get):
                    content_type = response.get("Content-Type", "")
                elif hasattr(response, "_headers") and "content-type" in response._headers:
                    content_type = response._headers["content-type"][1]
            except:
                pass

            # Handle different content types
            if 'application/json' in content_type:
                try:
                    # Try to parse as JSON
                    body_data = json.loads(response.content.decode('utf-8'))
                    return self._filter_sensitive_data(body_data)
                except (json.JSONDecodeError, UnicodeDecodeError):
                    # Fallback to raw content
                    return response.content.decode('utf-8', errors='replace')[:self.max_body_size]
            elif 'text/' in content_type:
                # Text content
                body_str = response.content.decode('utf-8', errors='replace')[:self.max_body_size]
                if len(response.content) > self.max_body_size:
                    body_str += "... [truncated]"
                return body_str
            else:
                # For binary content, just note the size
                return f"[Binary content, {len(response.content)} bytes]"

        except Exception as e:
            return f"[Error extracting response body: {str(e)}]"

    def _extract_error_details(self, response):
        """
        Extract error details from Django error responses.
        """
        try:
            if not hasattr(response, "content"):
                return "No error content available"

            content = response.content.decode('utf-8', errors='replace')
            error_details = {}

            # Look for Django traceback
            if 'Traceback (most recent call last)' in content:
                start_idx = content.find('Traceback (most recent call last)')
                if start_idx >= 0:
                    # Find the end of traceback (usually before HTML starts or double newline)
                    end_patterns = ['\n\n<', '</pre>', '\n\n\n']
                    end_idx = len(content)
                    for pattern in end_patterns:
                        pattern_idx = content.find(pattern, start_idx)
                        if pattern_idx >= 0:
                            end_idx = min(end_idx, pattern_idx)

                    traceback_text = content[start_idx:end_idx].strip()
                    error_details["django_traceback"] = traceback_text[:2000]  # Limit size

            # Look for exception type and value
            if 'Exception Type:' in content and 'Exception Value:' in content:
                try:
                    exc_type_start = content.find('Exception Type:') + len('Exception Type:')
                    exc_type_end = content.find('\n', exc_type_start)
                    exc_value_start = content.find('Exception Value:') + len('Exception Value:')
                    exc_value_end = content.find('\n', exc_value_start)

                    if exc_type_end >= 0 and exc_value_end >= 0:
                        exc_type = content[exc_type_start:exc_type_end].strip()
                        exc_value = content[exc_value_start:exc_value_end].strip()

                        error_details["django_exception"] = {
                            "type": exc_type,
                            "value": exc_value
                        }
                except Exception:
                    pass

            # Look for request information in debug page
            if 'Request Method:' in content:
                try:
                    method_start = content.find('Request Method:') + len('Request Method:')
                    method_end = content.find('\n', method_start)
                    if method_end >= 0:
                        method = content[method_start:method_end].strip()
                        error_details["debug_request_method"] = method
                except Exception:
                    pass

            return error_details if error_details else "Could not extract error details"

        except Exception as e:
            return f"Error extracting error details: {str(e)}"

    def _filter_sensitive_data(self, data):
        """
        Filter sensitive data from dictionaries with better error handling.
        """
        try:
            if not isinstance(data, dict):
                return data

            filtered = {}
            for key, value in data.items():
                try:
                    if self._is_sensitive_field(str(key)):
                        filtered[str(key)] = "[FILTERED]"
                    elif isinstance(value, dict):
                        filtered[str(key)] = self._filter_sensitive_data(value)
                    elif isinstance(value, list):
                        # Handle lists of dictionaries
                        if value and isinstance(value[0], dict):
                            filtered[str(key)] = [self._filter_sensitive_data(item) for item in value]
                        else:
                            filtered[str(key)] = value
                    else:
                        # Safely convert value to string and limit length
                        filtered[str(key)] = str(value)[:500] if value is not None else None
                except Exception:
                    # If individual field processing fails, mark it as error
                    filtered[str(key)] = "[PROCESSING_ERROR]"

            return filtered

        except Exception:
            # If filtering completely fails, return safe representation
            return {"filtering_error": "Could not filter sensitive data"}

    def _is_sensitive_field(self, field_name):
        """
        Check if a field name contains sensitive information.
        """
        try:
            sensitive_keywords = [
                "password", "token", "auth", "secret", "key", "cookie",
                "csrf", "session", "card", "credit", "cvv", "ssn", "social",
                "security", "private", "api_key", "apikey", "access_token",
                "refresh_token", "authorization", "x-api-key"
            ]
            field_lower = str(field_name).lower()
            return any(keyword in field_lower for keyword in sensitive_keywords)
        except Exception:
            # If checking fails, err on the side of caution
            return True


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
# PyLogHub/Loggier Documentation

## Overview

PyLogHub (Loggier) is a comprehensive logging solution for Python applications, with specialized integrations for web frameworks like Django, Flask, and FastAPI. It offers a flexible and powerful way to collect, process, and analyze logs from your applications with features like asynchronous logging, local caching, performance monitoring, and web framework integrations.

## Table of Contents

1. [Installation](#installation)
2. [Core Concepts](#core-concepts)
3. [Basic Usage](#basic-usage)
4. [Advanced Configuration](#advanced-configuration)
5. [Django Integration](#django-integration)
6. [Flask Integration](#flask-integration)
7. [FastAPI Integration](#fastapi-integration)
8. [Performance Monitoring](#performance-monitoring)
9. [Error Tracking](#error-tracking)
10. [Architecture](#architecture)
11. [API Reference](#api-reference)

## Installation

Install using pip:

```bash
pip install loggier
```

## Core Concepts

PyLogHub/Loggier is built around these core concepts:

- **Client**: The main Loggier class that handles log collection and sending
- **Handlers**: Components that process and deliver logs (API, Async, Cache)
- **Formatters**: Components that format logs for output
- **Context**: A system for adding and organizing contextual information
- **Integrations**: Framework-specific components for seamless integration

## Basic Usage

Simple example of using Loggier:

```python
from loggier import Loggier

# Create a Loggier instance
logger = Loggier(
    api_key="your-api-key",
    environment="development",
    service_name="my-service"
)

# Log basic messages
logger.info("Application started")
logger.warning("Something might be wrong", context={"user_id": 123})
logger.error("Something went wrong", context={"order_id": "ORD-123456"})

# Log exceptions
try:
    # Some code that might raise an exception
    result = 1 / 0
except Exception as e:
    logger.exception("Error calculating result", exception=e)

# Use context for adding structured information
with logger.context(user_id=123, transaction_id="TX12345"):
    logger.info("Processing transaction")
    try:
        # Transaction processing code
        logger.info("Transaction completed")
    except Exception as e:
        logger.exception("Transaction failed", exception=e)

# Make sure to flush logs before application exits
logger.flush()
```

## Advanced Configuration

Loggier provides many configuration options:

```python
from loggier import Loggier

logger = Loggier(
    api_key="your-api-key",
    project_name="my-project",
    environment="production",
    service_name="payment-service",
    api_url="https://api.loggier.com/api/ingest",  # Custom API endpoint
    async_mode=True,                              # Send logs asynchronously
    capture_uncaught=True,                        # Capture uncaught exceptions
    log_level=logging.INFO,                       # Minimum log level
    enable_caching=True,                          # Cache logs when offline
    cache_dir="/path/to/cache",                   # Custom cache directory
    max_batch_size=20,                            # Logs per batch
    flush_interval=5,                             # Auto-flush interval (seconds)
    sensitive_fields=["password", "credit_card"], # Fields to mask
    max_retries=3,                                # API retry attempts
    http_timeout=5,                               # API timeout (seconds)
    network_check_interval=60,                    # Network check interval
    tags=["api", "payments"],                     # Global tags
    enable_performance_monitoring=True            # Enable performance monitoring
)
```

## Django Integration

Loggier offers a powerful Django integration that can track requests, responses, and errors.

### Basic Setup

Add the middleware to your Django settings:

```python
# settings.py
MIDDLEWARE = [
    # other middleware...
    'loggier.integrations.django.LoggierDjangoMiddleware',
    # other middleware...
]

# Configure Loggier
LOGGIER = {
    'API_KEY': 'your-api-key-here',
    'API_URL': 'https://api.loggier.com/api/ingest',
    'ENVIRONMENT': 'production',
    'TAGS': ['django', 'web'],
    'CAPTURE_REQUEST_DATA': True,
    'LOG_SLOW_REQUESTS': True,
    'SLOW_REQUEST_THRESHOLD': 1.0,  # seconds
    'STATUSES_TO_TRACK': [500, 400, 401, 403],  # Status codes to track
    'CAPTURE_REQUEST_BODY': False,  # Be careful with sensitive data
    'CAPTURE_RESPONSE_BODY': True,  # Capture response bodies for errors
    'MAX_BODY_SIZE': 16384,  # Max body size to capture (16KB)
    'INCLUDE_STACKTRACE': True  # Include stacktrace for errors
}
```

### Tracking Specific Endpoints

Use the `track_endpoint` decorator to track specific views or endpoints:

```python
from loggier.integrations.django import track_endpoint
from django.http import JsonResponse

# Track this endpoint with custom settings
@track_endpoint(
    tags=['critical', 'payment'],
    capture_request_body=True,
    capture_response_body=True,
    statuses=[200, 201, 400, 500]
)
def payment_process(request):
    # This endpoint will have complete request/response tracking
    return JsonResponse({"status": "success"})
```

### Django Rest Framework Integration

With Django Rest Framework, you can track specific ViewSet methods:

```python
from rest_framework import viewsets
from loggier.integrations.django import track_endpoint

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    # Track only the list action
    @track_endpoint(tags=['user', 'list'])
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    # Track the create action with body capturing
    @track_endpoint(
        tags=['user', 'create'],
        capture_request_body=True,
        capture_response_body=True
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)
```

### Complete Transaction Tracking

The Django middleware can track the complete context of HTTP transactions:

1. **Request Information**:

   - HTTP method, path, query parameters
   - Headers (filtered for sensitive data)
   - Request body (if enabled)
   - User information
   - View/controller information

2. **Response Information**:

   - Status code
   - Response headers
   - Response time
   - Response body (if enabled)

3. **Error Information**:

   - Exception type and message
   - Full traceback
   - Application state at time of error

4. **Custom Context**:
   - Add custom context using `logger.context.update_global()`

### Example Log Output (Error):

```json
{
  "level": "ERROR",
  "message": "Server error: GET /api/v1/templates/ - 500",
  "timestamp": "2025-03-09T11:41:29.000Z",
  "context": {
    "request_id": "3c4e6f8g-9h0i-1j2k-3l4m-5n6o7p8q9r0s",
    "transaction": {
      "request": {
        "method": "GET",
        "path": "/api/v1/templates/",
        "query_params": {
          "limit": "100",
          "offset": "0"
        },
        "user": {
          "user_id": 5,
          "username": "john.doe@example.com"
        }
      },
      "response": {
        "status_code": 500,
        "content_type": "text/plain; charset=utf-8",
        "traceback": "Traceback (most recent call last):...",
        "exception": {
          "type": "ValueError",
          "value": "Uncaught"
        }
      }
    }
  }
}
```

## Flask Integration

Loggier provides integration with Flask:

```python
from flask import Flask
from loggier.integrations.flask import LoggierFlask

app = Flask(__name__)

# Initialize Loggier
loggier = LoggierFlask(
    api_key="your-api-key",
    environment="production",
    capture_request_data=True,
    log_slow_requests=True,
    slow_request_threshold=1.0
)

# Register with Flask
loggier.init_app(app)

@app.route('/')
def index():
    return "Hello World!"

if __name__ == '__main__':
    app.run()
```

## FastAPI Integration

Loggier integrates with FastAPI:

```python
from fastapi import FastAPI
from loggier.integrations.fastapi import LoggierFastAPI

app = FastAPI()

# Initialize Loggier
loggier = LoggierFastAPI(
    api_key="your-api-key",
    environment="production",
    capture_request_data=True,
    log_slow_requests=True,
    slow_request_threshold=1.0
)

# Register with FastAPI
loggier.init_app(app)

@app.get("/")
def read_root():
    return {"Hello": "World"}
```

## Performance Monitoring

Loggier includes tools for performance monitoring:

```python
from loggier import Loggier

logger = Loggier(
    api_key="your-api-key",
    environment="production",
    enable_performance_monitoring=True
)

# Track function performance
@logger.trace_function(threshold_ms=100)
def process_data(data):
    # Function execution time will be tracked
    # If it exceeds 100ms, it will be logged
    return data

# Track HTTP requests
@logger.trace_http(threshold_ms=1000)
def fetch_external_api():
    import requests
    return requests.get("https://api.example.com/data")

# Track database operations
@logger.trace_database(threshold_ms=50)
def get_user(user_id):
    # Database operation time will be tracked
    return User.objects.get(id=user_id)
```

## Error Tracking

Loggier provides comprehensive error tracking capabilities:

```python
from loggier import Loggier

logger = Loggier(
    api_key="your-api-key",
    environment="production",
    capture_uncaught=True  # Automatically capture uncaught exceptions
)

# Manually log exceptions
try:
    # Some code that might raise an exception
    result = 1 / 0
except Exception as e:
    logger.exception(
        "Division error",
        exception=e,
        context={
            "operation": "division",
            "numerator": 1,
            "denominator": 0
        }
    )

# Capture exceptions in functions
@logger.capture_exceptions
def risky_function():
    # If this function raises an exception, it will be logged
    return 1 / 0
```

## Architecture

PyLogHub/Loggier uses a modular architecture:

1. **Client (Loggier)**: Main interface for applications
2. **Handlers**:
   - **APIHandler**: Communicates with the PyLogHub API
   - **AsyncHandler**: Handles asynchronous log sending
   - **CacheHandler**: Manages local caching of logs
3. **Formatters**:
   - **JSONFormatter**: Formats logs as JSON
4. **Utils**:
   - **Context**: Manages contextual information
   - **Error**: Handles exception capturing
   - **Network**: Monitors network connectivity

## API Reference

### Loggier Class

The main client class for interacting with PyLogHub.

#### Constructor

```python
Loggier(
    api_key: str,
    project_name: Optional[str] = None,
    environment: str = "development",
    api_url: Optional[str] = None,
    service_name: Optional[str] = None,
    async_mode: bool = True,
    capture_uncaught: bool = True,
    log_level: int = logging.INFO,
    enable_caching: bool = True,
    cache_dir: Optional[str] = None,
    max_batch_size: int = 20,
    flush_interval: int = 5,
    sensitive_fields: Optional[List[str]] = None,
    max_retries: int = 3,
    http_timeout: int = 5,
    network_check_interval: int = 60,
    tags: Optional[List[str]] = None,
    enable_performance_monitoring: bool = True
)
```

#### Logging Methods

```python
# Basic logging methods
log(level: str, message: str, exception: Optional[Exception] = None, context: Optional[Dict[str, Any]] = None, tags: Optional[List[str]] = None) -> bool
debug(message: str, exception: Optional[Exception] = None, context: Optional[Dict[str, Any]] = None, tags: Optional[List[str]] = None) -> bool
info(message: str, exception: Optional[Exception] = None, context: Optional[Dict[str, Any]] = None, tags: Optional[List[str]] = None) -> bool
warning(message: str, exception: Optional[Exception] = None, context: Optional[Dict[str, Any]] = None, tags: Optional[List[str]] = None) -> bool
error(message: str, exception: Optional[Exception] = None, context: Optional[Dict[str, Any]] = None, tags: Optional[List[str]] = None) -> bool
critical(message: str, exception: Optional[Exception] = None, context: Optional[Dict[str, Any]] = None, tags: Optional[List[str]] = None) -> bool
exception(message: str, exception: Optional[Exception] = None, context: Optional[Dict[str, Any]] = None, tags: Optional[List[str]] = None) -> bool

# Context management
context(**kwargs) -> Context

# Performance monitoring decorators
trace_function(name: Optional[str] = None, threshold_ms: int = 500, tags: Optional[List[str]] = None, include_args: bool = False, include_return: bool = False, log_level: str = "INFO") -> Callable
trace_http(name: Optional[str] = None, threshold_ms: int = 1000, tags: Optional[List[str]] = None, mask_headers: Optional[List[str]] = None, mask_params: Optional[List[str]] = None, include_body: bool = False, log_level: str = "INFO") -> Callable
trace_database(name: Optional[str] = None, threshold_ms: int = 100, tags: Optional[List[str]] = None, include_params: bool = False, log_level: str = "INFO") -> Callable

# Utility methods
flush(timeout: Optional[float] = None) -> bool
get_stats() -> Dict[str, Any]
shutdown(timeout: Optional[float] = None) -> None
```

### Django Integration

#### LoggierDjangoMiddleware

```python
# In settings.py
MIDDLEWARE = [
    'loggier.integrations.django.LoggierDjangoMiddleware',
    # other middleware...
]

LOGGIER = {
    'API_KEY': 'your-api-key',
    'API_URL': 'https://api.loggier.com/api/ingest',
    'ENVIRONMENT': 'production',
    'STATUSES_TO_TRACK': [500, 400, 401, 403],
    'CAPTURE_REQUEST_BODY': False,
    'CAPTURE_RESPONSE_BODY': True,
    'MAX_BODY_SIZE': 16384,
    'INCLUDE_STACKTRACE': True
}
```

#### track_endpoint Decorator

```python
from loggier.integrations.django import track_endpoint

@track_endpoint(
    tags=None,                   # List of tags to add
    statuses=None,               # Status codes to track
    capture_request_body=False,  # Whether to capture request body
    capture_response_body=False  # Whether to capture response body
)
def my_view(request):
    # View implementation
    return HttpResponse("Hello")
```

### Flask Integration

```python
from flask import Flask
from loggier.integrations.flask import LoggierFlask

app = Flask(__name__)
loggier = LoggierFlask(api_key="your-api-key")
loggier.init_app(app)
```

### FastAPI Integration

```python
from fastapi import FastAPI
from loggier.integrations.fastapi import LoggierFastAPI

app = FastAPI()
loggier = LoggierFastAPI(api_key="your-api-key")
loggier.init_app(app)
```

## Troubleshooting

### Common Issues

1. **Logs not appearing**:

   - Check API key and URL
   - Ensure network connectivity
   - Check if async_mode is enabled and call flush() before exit

2. **High memory usage**:

   - Reduce max_batch_size
   - Increase flush_interval
   - Disable caching if not needed

3. **Performance impact**:

   - Use async_mode=True (default)
   - Be selective with STATUSES_TO_TRACK
   - Use track_endpoint only on critical endpoints
   - Limit body capturing (CAPTURE_REQUEST_BODY, CAPTURE_RESPONSE_BODY)

4. **Django middleware error**:
   - Ensure correct middleware order
   - Check LOGGIER settings in settings.py

## Best Practices

1. **Use context for structured logging**:

   ```python
   with logger.context(user_id=123):
       logger.info("User logged in")
   ```

2. **Add custom context to Django requests**:

   ```python
   from loggier import _loggier_instance
   if _loggier_instance:
       _loggier_instance.context.update_global({
           "user_id": request.user.id,
           "transaction_id": "TX12345"
       })
   ```

3. **Call flush() before application exit**:

   ```python
   # Ensure all logs are sent
   logger.flush()
   ```

4. **Filter sensitive data**:

   ```python
   logger = Loggier(
       api_key="your-api-key",
       sensitive_fields=["password", "credit_card", "ssn"]
   )
   ```

5. **Use decorators for performance monitoring**:
   ```python
   @logger.trace_function(threshold_ms=100)
   def slow_function():
       # Performance will be logged if execution exceeds 100ms
   ```

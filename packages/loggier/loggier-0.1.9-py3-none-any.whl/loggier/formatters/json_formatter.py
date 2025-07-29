import json
import datetime
import traceback
import platform
import socket
import os
import sys
import linecache
from typing import Any, Dict, List, Optional, Union


class JSONFormatter:
    """
    Log kayıtlarını JSON formatına dönüştüren formatter with improved exception handling
    """

    def __init__(
        self,
        include_runtime_info: bool = True,
        include_timestamp: bool = True,
        include_hostname: bool = True,
        include_process_info: bool = True,
        max_traceback_length: int = 8192,  # Increased from 4096
        max_message_length: int = 2048,  # Increased from 1024
        sensitive_fields: Optional[List[str]] = None,
        include_local_variables: bool = False,  # New option
        max_frame_count: int = 20  # New option to limit frame count
    ):
        """
        JSONFormatter'ı başlat

        Args:
            include_runtime_info (bool, optional): Çalışma zamanı bilgilerini ekle
            include_timestamp (bool, optional): Zaman damgasını ekle
            include_hostname (bool, optional): Sunucu adını ekle
            include_process_info (bool, optional): Proses bilgilerini ekle
            max_traceback_length (int, optional): Maksimum traceback uzunluğu
            max_message_length (int, optional): Maksimum mesaj uzunluğu
            sensitive_fields (List[str], optional): Hassas veri içeren anahtar listesi
            include_local_variables (bool, optional): Local değişkenleri dahil et
            max_frame_count (int, optional): Maksimum frame sayısı
        """
        self.include_runtime_info = include_runtime_info
        self.include_timestamp = include_timestamp
        self.include_hostname = include_hostname
        self.include_process_info = include_process_info
        self.max_traceback_length = max_traceback_length
        self.max_message_length = max_message_length
        self.include_local_variables = include_local_variables
        self.max_frame_count = max_frame_count
        self.sensitive_fields = sensitive_fields or [
            "password", "token", "auth", "secret", "key", "cookie",
            "csrf", "session", "card", "credit", "cvv", "ssn", "social",
            "api_key", "apikey", "access_token", "refresh_token"
        ]

    def format(self, log_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Log verisini JSON formatına dönüştür

        Args:
            log_data (Dict[str, Any]): Format edilecek log verisi

        Returns:
            Dict[str, Any]: JSON formatında log verisi
        """
        try:
            # Parametre adlarını düzeltmek için burayı yeniden yazıyoruz
            message = log_data.get('message', '')
            level = log_data.get('level', 'INFO')
            exception = log_data.get('exception')
            context = log_data.get('context', {})
            tags = log_data.get('tags', [])
            environment = log_data.get('environment', 'development')

            return self._format_log_data(message, level, exception, context, tags, environment)
        except Exception as format_error:
            # If formatting fails, return safe minimal log
            return {
                "message": str(log_data.get('message', 'Unknown message')),
                "level": str(log_data.get('level', 'ERROR')),
                "timestamp": datetime.datetime.utcnow().isoformat(),
                "environment": str(log_data.get('environment', 'unknown')),
                "formatting_error": str(format_error),
                "original_data_keys": list(log_data.keys()) if isinstance(log_data, dict) else "Not a dict"
            }

    def _format_log_data(
        self,
        message: str,
        level: str,
        exception: Optional[Union[Exception, Dict[str, Any]]] = None,
        context: Optional[Dict[str, Any]] = None,
        tags: Optional[List[str]] = None,
        environment: str = "development"
    ) -> Dict[str, Any]:
        """
        Log kaydını JSON formatına dönüştür with improved exception handling
        """
        try:
            # Temel log verisini oluştur
            log_data = {
                "message": self._safe_truncate(str(message), self.max_message_length),
                "level": str(level).upper(),
                "environment": str(environment)
            }

            # Zaman damgası ekle
            if self.include_timestamp:
                try:
                    log_data["timestamp"] = datetime.datetime.utcnow().isoformat() + "Z"
                except Exception as ts_error:
                    log_data["timestamp"] = "ERROR_GETTING_TIMESTAMP"
                    log_data["timestamp_error"] = str(ts_error)

            # Hassas verileri temizle ve metadata ekle
            if context:
                try:
                    log_data["context"] = self._sanitize_sensitive_data(context)
                except Exception as ctx_error:
                    log_data["context"] = {"sanitization_error": str(ctx_error)}

            # Etiketleri ekle
            if tags:
                try:
                    log_data["tags"] = [str(tag) for tag in tags if tag is not None]
                except Exception as tag_error:
                    log_data["tags"] = []
                    log_data["tags_error"] = str(tag_error)

            # İstisna bilgilerini ekle - improved handling
            if exception:
                try:
                    log_data["exception"] = self._format_exception(exception)
                except Exception as exc_error:
                    log_data["exception"] = {
                        "formatting_error": str(exc_error),
                        "exception_type": str(type(exception).__name__) if hasattr(exception,
                                                                                   '__class__') else "Unknown",
                        "exception_str": str(exception) if exception else "None"
                    }

            # Çalışma zamanı bilgilerini ekle
            if self.include_runtime_info:
                try:
                    log_data["runtime_context"] = self._get_runtime_info()
                except Exception as runtime_error:
                    log_data["runtime_context"] = {"error": str(runtime_error)}

            return log_data

        except Exception as format_error:
            # If entire formatting fails, return minimal safe data
            return {
                "message": str(message) if message else "FORMATTING_ERROR",
                "level": str(level) if level else "ERROR",
                "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
                "environment": str(environment) if environment else "unknown",
                "critical_formatting_error": str(format_error)
            }

    def _format_exception(self, exception: Union[Exception, Dict[str, Any]]) -> Dict[str, Any]:
        """
        İstisna nesnesini formatla with comprehensive error handling
        """
        try:
            # If exception is already a dict (from format_exception_for_logging), use it
            if isinstance(exception, dict):
                return self._format_exception_dict(exception)

            # If it's an actual Exception object, format it
            if isinstance(exception, Exception):
                return self._format_exception_object(exception)

            # If it's something else, try to handle it
            return {
                "type": str(type(exception).__name__),
                "message": str(exception),
                "note": "Exception was not a standard Exception object or dict"
            }

        except Exception as format_error:
            return {
                "formatting_error": str(format_error),
                "exception_repr": repr(exception) if exception else "None",
                "exception_type": str(type(exception)) if exception else "None"
            }

    def _format_exception_dict(self, exc_dict: Dict[str, Any]) -> Dict[str, Any]:
        """
        Format pre-processed exception dictionary
        """
        try:
            formatted = {}

            # Copy basic fields safely
            safe_fields = ["type", "message", "module", "args"]
            for field in safe_fields:
                if field in exc_dict:
                    formatted[field] = str(exc_dict[field])

            # Handle traceback
            if "traceback" in exc_dict:
                traceback_str = str(exc_dict["traceback"])
                formatted["traceback"] = self._safe_truncate(traceback_str, self.max_traceback_length)

            # Handle traceback summary
            if "traceback_summary" in exc_dict:
                try:
                    summary = exc_dict["traceback_summary"]
                    if isinstance(summary, list):
                        formatted["traceback_summary"] = [str(item) for item in summary]
                    else:
                        formatted["traceback_summary"] = str(summary)
                except Exception:
                    formatted["traceback_summary"] = "Could not format traceback summary"

            # Handle frames
            if "frames" in exc_dict and isinstance(exc_dict["frames"], list):
                try:
                    formatted_frames = []
                    for i, frame in enumerate(exc_dict["frames"][:self.max_frame_count]):
                        if isinstance(frame, dict):
                            formatted_frame = {
                                "filename": str(frame.get("filename", "unknown")),
                                "function": str(frame.get("function", "unknown")),
                                "line_number": frame.get("line_number", 0),
                                "code_context": str(frame.get("code_context", ""))[:200]
                            }
                            formatted_frames.append(formatted_frame)
                        else:
                            formatted_frames.append({"frame_error": f"Frame {i} is not a dict"})

                    formatted["frames"] = formatted_frames
                    if len(exc_dict["frames"]) > self.max_frame_count:
                        formatted[
                            "frames_truncated"] = f"Showing {self.max_frame_count} of {len(exc_dict['frames'])} frames"
                except Exception as frame_error:
                    formatted["frames_error"] = str(frame_error)

            # Handle local variables if available and requested
            if self.include_local_variables and "local_variables" in exc_dict:
                try:
                    local_vars = exc_dict["local_variables"]
                    if isinstance(local_vars, dict):
                        formatted["local_variables"] = self._sanitize_sensitive_data(local_vars)
                    else:
                        formatted["local_variables"] = str(local_vars)
                except Exception as vars_error:
                    formatted["local_variables_error"] = str(vars_error)

            # Handle custom attributes
            if "custom_attributes" in exc_dict:
                try:
                    custom_attrs = exc_dict["custom_attributes"]
                    if isinstance(custom_attrs, dict):
                        formatted["custom_attributes"] = self._sanitize_sensitive_data(custom_attrs)
                    else:
                        formatted["custom_attributes"] = str(custom_attrs)
                except Exception as attrs_error:
                    formatted["custom_attributes_error"] = str(attrs_error)

            return formatted

        except Exception as dict_format_error:
            return {
                "dict_formatting_error": str(dict_format_error),
                "original_keys": list(exc_dict.keys()) if isinstance(exc_dict, dict) else "Not a dict"
            }

    def _format_exception_object(self, exception: Exception) -> Dict[str, Any]:
        """
        Format actual Exception object
        """
        try:
            exc_type = type(exception)

            exception_data = {
                "type": exc_type.__name__,
                "message": str(exception),
                "module": getattr(exc_type, '__module__', 'unknown'),
                "args": [str(arg) for arg in getattr(exception, 'args', [])]
            }

            # Get traceback information
            try:
                if hasattr(exception, "__traceback__") and exception.__traceback__:
                    # Format full traceback
                    tb_lines = traceback.format_exception(exc_type, exception, exception.__traceback__)
                    full_traceback = ''.join(tb_lines)
                    exception_data["traceback"] = self._safe_truncate(full_traceback, self.max_traceback_length)

                    # Format traceback summary
                    summary_lines = traceback.format_exception_only(exc_type, exception)
                    exception_data["traceback_summary"] = [line.strip() for line in summary_lines]

                    # Extract frame information
                    frames = []
                    tb = exception.__traceback__
                    frame_count = 0

                    while tb and frame_count < self.max_frame_count:
                        frame = tb.tb_frame
                        try:
                            # Get source line
                            filename = frame.f_code.co_filename
                            line_number = tb.tb_lineno
                            source_line = linecache.getline(filename, line_number).strip()

                            frame_info = {
                                "filename": filename,
                                "function": frame.f_code.co_name,
                                "line_number": line_number,
                                "code_context": source_line
                            }

                            # Add local variables if requested and it's the last frame
                            if self.include_local_variables and tb.tb_next is None:
                                try:
                                    local_vars = {}
                                    for k, v in frame.f_locals.items():
                                        if not k.startswith('_'):
                                            try:
                                                local_vars[k] = str(v)[:100]  # Limit variable value length
                                            except:
                                                local_vars[k] = "<could not serialize>"

                                    if local_vars:
                                        frame_info["local_variables"] = self._sanitize_sensitive_data(local_vars)
                                except Exception:
                                    frame_info["local_variables_error"] = "Could not extract local variables"

                            frames.append(frame_info)
                        except Exception as frame_error:
                            frames.append({
                                "frame_error": str(frame_error),
                                "frame_index": frame_count
                            })

                        tb = tb.tb_next
                        frame_count += 1

                    exception_data["frames"] = frames
                    if tb:  # There are more frames
                        exception_data["frames_truncated"] = f"Showing {frame_count} frames, more available"
                else:
                    # Try to get current traceback
                    current_tb = traceback.format_exc()
                    if current_tb and current_tb.strip() != "NoneType: None":
                        exception_data["traceback"] = self._safe_truncate(current_tb, self.max_traceback_length)
                        exception_data["note"] = "Traceback from current context"

            except Exception as tb_error:
                exception_data["traceback_error"] = str(tb_error)
                exception_data["traceback"] = "Could not extract traceback information"

            # Add custom exception attributes
            try:
                if hasattr(exception, '__dict__') and exception.__dict__:
                    custom_attrs = {}
                    for key, value in exception.__dict__.items():
                        if not key.startswith('_'):
                            try:
                                custom_attrs[key] = str(value)[:200]  # Limit attribute length
                            except:
                                custom_attrs[key] = "<could not serialize>"

                    if custom_attrs:
                        exception_data["custom_attributes"] = self._sanitize_sensitive_data(custom_attrs)
            except Exception as attrs_error:
                exception_data["custom_attributes_error"] = str(attrs_error)

            return exception_data

        except Exception as obj_format_error:
            return {
                "object_formatting_error": str(obj_format_error),
                "exception_type": str(type(exception).__name__) if hasattr(exception, '__class__') else "Unknown",
                "exception_str": str(exception) if exception else "None"
            }

    def _get_runtime_info(self) -> Dict[str, Any]:
        """
        Çalışma zamanı bilgilerini topla with better error handling
        """
        info = {}

        try:
            info["python_version"] = platform.python_version()
        except Exception as e:
            info["python_version_error"] = str(e)

        try:
            info["platform"] = platform.platform()
        except Exception as e:
            info["platform_error"] = str(e)

        try:
            info["system"] = platform.system()
        except Exception as e:
            info["system_error"] = str(e)

        try:
            info["python_implementation"] = platform.python_implementation()
        except Exception as e:
            info["python_implementation_error"] = str(e)

        if self.include_hostname:
            try:
                info["hostname"] = socket.gethostname()
                info["ip"] = socket.gethostbyname(socket.gethostname())
            except Exception as e:
                info["hostname_error"] = str(e)

        if self.include_process_info:
            try:
                info["process_id"] = os.getpid()
                import threading
                info["thread_id"] = threading.get_ident()
            except Exception as e:
                info["process_info_error"] = str(e)

        # Uygulama bilgilerini topla
        try:
            main_module = sys.modules.get('__main__')
            if main_module:
                main_file = getattr(main_module, '__file__', None)
                if main_file:
                    info["main_file"] = os.path.basename(main_file)
        except Exception as e:
            info["main_file_error"] = str(e)

        return info

    def _sanitize_sensitive_data(self, data: Any) -> Any:
        """
        Hassas verileri maskele with comprehensive handling
        """
        try:
            if data is None:
                return None

            if isinstance(data, dict):
                return self._sanitize_dict(data)
            elif isinstance(data, list):
                return self._sanitize_list(data)
            elif isinstance(data, (str, int, float, bool)):
                return data
            else:
                # For other types, convert to string safely
                try:
                    return str(data)[:500]  # Limit length
                except:
                    return "<could not serialize object>"

        except Exception as sanitize_error:
            return {"sanitization_error": str(sanitize_error)}

    def _sanitize_dict(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Sanitize dictionary data
        """
        try:
            sanitized = {}

            for key, value in data.items():
                try:
                    key_str = str(key)

                    # Check if key is sensitive
                    if self._is_sensitive_key(key_str):
                        sanitized[key_str] = "[FILTERED]"
                    else:
                        sanitized[key_str] = self._sanitize_sensitive_data(value)

                except Exception as item_error:
                    # If individual item fails, mark it
                    sanitized[f"error_key_{len(sanitized)}"] = f"<processing error: {str(item_error)}>"

            return sanitized

        except Exception as dict_error:
            return {"dict_sanitization_error": str(dict_error)}

    def _sanitize_list(self, data: List[Any]) -> List[Any]:
        """
        Sanitize list data
        """
        try:
            sanitized = []

            for i, item in enumerate(data):
                try:
                    sanitized.append(self._sanitize_sensitive_data(item))
                except Exception as item_error:
                    sanitized.append(f"<list item {i} processing error: {str(item_error)}>")

            return sanitized

        except Exception as list_error:
            return [f"<list sanitization error: {str(list_error)}>"]

    def _is_sensitive_key(self, key: str) -> bool:
        """
        Check if a key contains sensitive information
        """
        try:
            key_lower = key.lower()
            return any(sensitive in key_lower for sensitive in self.sensitive_fields)
        except Exception:
            # If checking fails, err on the side of caution
            return True

    def _safe_truncate(self, text: str, max_length: int) -> str:
        """
        Metni belirli bir uzunlukta güvenli şekilde kısalt
        """
        try:
            if not text:
                return ""

            text_str = str(text)
            if len(text_str) <= max_length:
                return text_str

            # Try to truncate at word boundary if possible
            if max_length > 50:
                truncated = text_str[:max_length - 20]
                last_space = truncated.rfind(' ')
                if last_space > max_length // 2:  # Only if we don't lose too much
                    return truncated[:last_space] + "... [truncated]"

            # Simple truncation
            return text_str[:max_length - 15] + "... [truncated]"

        except Exception:
            return f"<truncation error for text of length {len(str(text)) if text else 0}>"

    def to_json_string(self, log_data: Dict[str, Any]) -> str:
        """
        Log verisini JSON string'e dönüştür with better error handling
        """
        try:
            class SafeDateTimeEncoder(json.JSONEncoder):
                """JSON encoder that handles datetime objects and other complex types safely."""

                def default(self, obj):
                    try:
                        if isinstance(obj, datetime.datetime):
                            return obj.isoformat()
                        elif isinstance(obj, datetime.date):
                            return obj.isoformat()
                        elif isinstance(obj, datetime.time):
                            return obj.isoformat()
                        elif hasattr(obj, '__dict__'):
                            # For objects with __dict__, try to serialize their attributes
                            return {k: str(v)[:100] for k, v in obj.__dict__.items() if not k.startswith('_')}
                        else:
                            # For anything else, convert to string
                            return str(obj)[:200]
                    except Exception:
                        return f"<{type(obj).__name__} object - could not serialize>"

            return json.dumps(
                log_data,
                cls=SafeDateTimeEncoder,
                ensure_ascii=False,
                separators=(',', ':'),  # Compact JSON
                default=str  # Final fallback
            )

        except Exception as json_error:
            # If JSON serialization completely fails, return a safe JSON string
            safe_data = {
                "message": str(log_data.get('message', 'JSON serialization failed')),
                "level": str(log_data.get('level', 'ERROR')),
                "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
                "json_serialization_error": str(json_error),
                "original_data_type": str(type(log_data))
            }

            try:
                return json.dumps(safe_data, ensure_ascii=False, default=str)
            except Exception:
                # Last resort - return a basic JSON string
                return '{"message": "Critical JSON formatting error", "level": "ERROR", "timestamp": "' + datetime.datetime.utcnow().isoformat() + 'Z"}'
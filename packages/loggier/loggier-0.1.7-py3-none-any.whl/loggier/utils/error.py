import sys
import traceback
from functools import wraps
from typing import Any, Callable, Dict, Optional, Type, TypeVar, cast

# Client referansını Type Hinting için tanımla
LoggierType = TypeVar('LoggierType')


def capture_exceptions(
    logger: LoggierType,
    level: str = "error",
    reraise: bool = True,
    exc_types: Optional[Type[Exception]] = None,
    message: str = "Fonksiyon çalışırken bir hata oluştu",
    context: Optional[Dict[str, Any]] = None
):
    """
    Fonksiyon çalışırken oluşan hataları otomatik olarak yakala ve logla

    Args:
        logger (Loggier): Loggier instance
        level (str, optional): Log seviyesi. Defaults to "error".
        reraise (bool, optional): Hatayı yeniden fırlat. Defaults to True.
        exc_types (Type[Exception], optional): Yakalanacak hata tipleri. Defaults to None (tüm hatalar).
        message (str, optional): Log mesajı. Defaults to "Fonksiyon çalışırken bir hata oluştu".
        context (Dict[str, Any], optional): Ek bağlam bilgileri. Defaults to None.

    Returns:
        Callable: Decorator fonksiyonu

    Example:
        @capture_exceptions(logger, level="error", message="Kullanıcı işlemi başarısız")
        def process_user(user_id):
            # ...
    """

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                # Belirli hata tipleri belirtilmişse kontrol et
                if exc_types and not isinstance(e, exc_types):
                    raise

                # Fonksiyon bilgilerini topla
                func_info = {
                    "function": func.__name__,
                    "module": func.__module__,
                    "args": str(args)[:200],  # Çok uzun olmasın diye kısıtla
                    "kwargs": str({k: str(v)[:50] for k, v in kwargs.items()})  # Hassas veriler için kısıtla
                }

                # Bağlam bilgilerini birleştir
                combined_context = {**func_info, **(context or {})}

                # Traceback bilgisini ekle
                combined_context["traceback_details"] = {
                    "exception_type": type(e).__name__,
                    "exception_message": str(e),
                    "traceback": traceback.format_exc()
                }

                # Hatayı logla
                if level == "critical":
                    logger.critical(message, exception=e, context=combined_context)
                elif level == "error":
                    logger.error(message, exception=e, context=combined_context)
                elif level == "warning":
                    logger.warning(message, exception=e, context=combined_context)
                else:
                    logger.error(message, exception=e, context=combined_context)

                # Yeniden fırlat
                if reraise:
                    raise

                return None

        return wrapper

    return decorator


class ExceptionReporter:
    """
    Yakalanmayan (uncaught) istisnaları raporlamak için sınıf
    """

    def __init__(self, logger: LoggierType):
        """
        ExceptionReporter'ı başlat

        Args:
            logger (Loggier): Loggier instance
        """
        self.logger = logger
        self.original_excepthook = sys.excepthook

    def handle_exception(self, exc_type, exc_value, exc_traceback):
        """
        Yakalanmayan istisnaları için excepthook metodu
        """
        # Tam traceback bilgisini al
        try:
            # Formatlanmış traceback'i al
            tb_lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
            formatted_traceback = ''.join(tb_lines)

            # Exception detaylarını topla
            exception_details = {
                "exception_type": exc_type.__name__ if exc_type else "Unknown",
                "exception_message": str(exc_value) if exc_value else "No message",
                "exception_module": getattr(exc_type, '__module__', 'Unknown') if exc_type else "Unknown",
                "traceback": formatted_traceback,
                "traceback_summary": traceback.format_exception_only(exc_type, exc_value)
            }

            # Eğer traceback varsa, son frame bilgisini de ekle
            if exc_traceback:
                last_frame = exc_traceback
                while last_frame.tb_next:
                    last_frame = last_frame.tb_next

                frame_info = last_frame.tb_frame
                exception_details["last_frame"] = {
                    "filename": frame_info.f_code.co_filename,
                    "function": frame_info.f_code.co_name,
                    "line_number": last_frame.tb_lineno,
                    "local_vars": {k: str(v)[:100] for k, v in frame_info.f_locals.items() if not k.startswith('_')}
                }

        except Exception as format_error:
            # Traceback formatlarken hata olursa basit bilgi ver
            exception_details = {
                "exception_type": str(exc_type) if exc_type else "Unknown",
                "exception_message": str(exc_value) if exc_value else "No message",
                "format_error": str(format_error),
                "traceback": "Could not format traceback"
            }

        # Hatayı logla
        self.logger.critical(
            "Yakalanmayan bir istisna oluştu",
            exception=exc_value,
            context=exception_details
        )

        # Orijinal excepthook'u çağır
        self.original_excepthook(exc_type, exc_value, exc_traceback)

    # Geriye dönük uyumluluk için excepthook metod adını da kullanılabilir tut
    excepthook = handle_exception

    def enable(self):
        """
        Yakalanmayan istisna raporlamayı etkinleştir
        """
        sys.excepthook = self.handle_exception

    def disable(self):
        """
        Yakalanmayan istisna raporlamayı devre dışı bırak
        """
        sys.excepthook = self.original_excepthook


def patch_thread_excepthook():
    """
    Thread'lerde yakalanmayan istisnaları raporlamak için threading modülünü yama
    """
    import threading

    # Orijinal thread run metodunu kaydet
    old_thread_run = threading.Thread.run

    def new_thread_run(self, *args, **kwargs):
        try:
            old_thread_run(self, *args, **kwargs)
        except Exception:
            # Thread excepthook'u çağır (sys.excepthook veya özel excepthook)
            exc_info = sys.exc_info()
            if exc_info[0] is not None:
                sys.excepthook(*exc_info)

    # Thread sınıfının run metodunu değiştir
    threading.Thread.run = new_thread_run


def format_exception_for_logging(exception: Exception) -> Dict[str, Any]:
    """
    Exception'ı loglama için detaylı formatlama yapar

    Args:
        exception: Formatlanacak exception

    Returns:
        Dict: Detaylı exception bilgisi
    """
    try:
        exc_type = type(exception)
        exc_value = exception
        exc_traceback = exception.__traceback__

        # Temel exception bilgileri
        exception_data = {
            "type": exc_type.__name__,
            "message": str(exc_value),
            "module": getattr(exc_type, '__module__', 'Unknown'),
            "args": [str(arg) for arg in getattr(exception, 'args', [])]
        }

        # Traceback bilgisi
        if exc_traceback:
            # Formatlanmış traceback
            tb_lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
            exception_data["traceback"] = ''.join(tb_lines)

            # Traceback özeti
            exception_data["traceback_summary"] = traceback.format_exception_only(exc_type, exc_value)

            # Frame bilgileri
            frames = []
            tb = exc_traceback
            while tb:
                frame = tb.tb_frame
                frames.append({
                    "filename": frame.f_code.co_filename,
                    "function": frame.f_code.co_name,
                    "line_number": tb.tb_lineno,
                    "code_context": linecache.getline(frame.f_code.co_filename, tb.tb_lineno).strip()
                })
                tb = tb.tb_next

            exception_data["frames"] = frames

            # Son frame'in local değişkenleri (güvenli şekilde)
            if frames:
                last_frame = exc_traceback
                while last_frame.tb_next:
                    last_frame = last_frame.tb_next

                try:
                    local_vars = {}
                    for k, v in last_frame.tb_frame.f_locals.items():
                        if not k.startswith('_'):
                            try:
                                # Güvenli string dönüşümü
                                local_vars[k] = str(v)[:100]
                            except:
                                local_vars[k] = "<could not serialize>"

                    exception_data["local_variables"] = local_vars
                except:
                    exception_data["local_variables"] = "Could not extract local variables"

        # Eğer exception'ın özel attributeleri varsa
        if hasattr(exception, '__dict__'):
            custom_attrs = {}
            for key, value in exception.__dict__.items():
                if not key.startswith('_'):
                    try:
                        custom_attrs[key] = str(value)[:100]
                    except:
                        custom_attrs[key] = "<could not serialize>"

            if custom_attrs:
                exception_data["custom_attributes"] = custom_attrs

        return exception_data

    except Exception as format_error:
        # Formatlarken hata olursa minimal bilgi döndür
        return {
            "type": str(type(exception).__name__),
            "message": str(exception),
            "format_error": str(format_error),
            "traceback": "Could not format exception details"
        }


# Linecache import ekle
import linecache
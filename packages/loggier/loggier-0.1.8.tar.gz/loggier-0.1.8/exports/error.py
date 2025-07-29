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
                    "args": str(args),
                    "kwargs": str(kwargs)
                }
                
                # Bağlam bilgilerini birleştir
                combined_context = {**func_info, **(context or {})}
                
                # Hatayı logla
                if level == "critical":
                    logger.critical(message, exception=e, context=combined_context)  # exc_info -> exception, extra -> context olarak değiştirildi
                elif level == "error":
                    logger.error(message, exception=e, context=combined_context)  # exc_info -> exception, extra -> context olarak değiştirildi
                elif level == "warning":
                    logger.warning(message, exception=e, context=combined_context)  # exc_info -> exception, extra -> context olarak değiştirildi
                else:
                    logger.error(message, exception=e, context=combined_context)  # exc_info -> exception, extra -> context olarak değiştirildi
                
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
        (excepthook -> handle_exception olarak değiştirildi)
        """
        # Hata bilgilerini topla
        exception_str = ''.join(traceback.format_exception(exc_type, exc_value, exc_traceback))
        
        # Hatayı logla
        self.logger.critical(
            "Yakalanmayan bir istisna oluştu",
            exception=exc_value,  # exc_info -> exception olarak değiştirildi
            context={"traceback": exception_str}  # extra -> context olarak değiştirildi
        )
        
        # Orijinal excepthook'u çağır
        self.original_excepthook(exc_type, exc_value, exc_traceback)
    
    # Geriye dönük uyumluluk için excepthook metod adını da kullanılabilir tut
    excepthook = handle_exception
    
    def enable(self):
        """
        Yakalanmayan istisna raporlamayı etkinleştir
        """
        sys.excepthook = self.handle_exception  # excepthook -> handle_exception olarak değiştirildi
    
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
            sys.excepthook(*sys.exc_info())
    
    # Thread sınıfının run metodunu değiştir
    threading.Thread.run = new_thread_run
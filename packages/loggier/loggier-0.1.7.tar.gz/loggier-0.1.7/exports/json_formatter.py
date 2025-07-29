import json
import datetime
import traceback
import platform
import socket
import os
import sys
from typing import Any, Dict, List, Optional, Union

class JSONFormatter:
    """
    Log kayıtlarını JSON formatına dönüştüren formatter
    """
    
    def __init__(
        self,
        include_runtime_info: bool = True,
        include_timestamp: bool = True,
        include_hostname: bool = True,
        include_process_info: bool = True,
        max_traceback_length: int = 4096,
        max_message_length: int = 1024,
        sensitive_fields: Optional[List[str]] = None
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
        """
        self.include_runtime_info = include_runtime_info
        self.include_timestamp = include_timestamp
        self.include_hostname = include_hostname
        self.include_process_info = include_process_info
        self.max_traceback_length = max_traceback_length
        self.max_message_length = max_message_length
        self.sensitive_fields = sensitive_fields or [
            "password", "token", "auth", "secret", "key", "cookie", 
            "csrf", "session", "card", "credit", "cvv", "ssn", "social"
        ]
    
    def format(self, log_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Log verisini JSON formatına dönüştür
        
        Args:
            log_data (Dict[str, Any]): Format edilecek log verisi
            
        Returns:
            Dict[str, Any]: JSON formatında log verisi
        """
        # Parametre adlarını düzeltmek için burayı yeniden yazıyoruz
        message = log_data.get('message', '')
        level = log_data.get('level', 'INFO')
        exception = log_data.get('exception')
        context = log_data.get('context', {})
        tags = log_data.get('tags', [])
        environment = log_data.get('environment', 'development')
        
        return self._format_log_data(message, level, exception, context, tags, environment)
    
    def _format_log_data(
        self,
        message: str,
        level: str,
        exception: Optional[Exception] = None,
        context: Optional[Dict[str, Any]] = None,
        tags: Optional[List[str]] = None,
        environment: str = "development"
    ) -> Dict[str, Any]:
        """
        Log kaydını JSON formatına dönüştür
        
        Args:
            message (str): Log mesajı
            level (str): Log seviyesi (info, warning, error, critical)
            exception (Exception, optional): İstisna nesnesi
            context (Dict[str, Any], optional): Bağlam bilgileri
            tags (List[str], optional): Etiketler
            environment (str, optional): Ortam adı
        
        Returns:
            Dict[str, Any]: JSON formatında log verisi
        """
        # Temel log verisini oluştur
        log_data = {
            "message": self._truncate(message, self.max_message_length),
            "level": level,
            "environment": environment
        }
        
        # Zaman damgası ekle
        if self.include_timestamp:
            log_data["timestamp"] = datetime.datetime.utcnow().isoformat()
        
        # Hassas verileri temizle ve metadata ekle
        if context:
            log_data["context"] = self._sanitize_sensitive_data(context)
        
        # Etiketleri ekle
        if tags:
            log_data["tags"] = tags
        
        # İstisna bilgilerini ekle
        if exception:
            log_data["exception"] = self._format_exception(exception)
        
        # Çalışma zamanı bilgilerini ekle
        if self.include_runtime_info:
            log_data["runtime_context"] = self._get_runtime_info()
        
        return log_data
    
    def _format_exception(self, exception: Exception) -> Dict[str, Any]:
        """
        İstisna nesnesini formatla
        
        Args:
            exception (Exception): İstisna nesnesi
        
        Returns:
            Dict[str, Any]: Formatlanmış istisna verisi
        """
        exc_type = type(exception)
        
        exception_data = {
            "type": exc_type.__name__,
            "message": str(exception),
            "args": [str(arg) for arg in getattr(exception, 'args', [])],
        }
        
        if hasattr(exception, "__traceback__") and exception.__traceback__:
            tb_text = ''.join(traceback.format_exception(
                exc_type, exception, exception.__traceback__
            ))
            exception_data["traceback"] = self._truncate(tb_text, self.max_traceback_length)
        else:
            tb_text = traceback.format_exc()
            if tb_text and tb_text.strip() != "NoneType: None":
                exception_data["traceback"] = self._truncate(tb_text, self.max_traceback_length)
        
        return exception_data
    
    def _get_runtime_info(self) -> Dict[str, Any]:
        """
        Çalışma zamanı bilgilerini topla
        
        Returns:
            Dict[str, Any]: Çalışma zamanı bilgileri
        """
        info = {
            "python_version": platform.python_version(),
            "platform": platform.platform(),
            "system": platform.system(),
            "python_implementation": platform.python_implementation(),
        }
        
        if self.include_hostname:
            try:
                info["hostname"] = socket.gethostname()
                info["ip"] = socket.gethostbyname(socket.gethostname())
            except Exception:
                pass
        
        if self.include_process_info:
            info["process_id"] = os.getpid()
            info["thread_id"] = os.getpid()  # Gerçek thread ID'sini almak için threading modülü kullanılabilir
        
        # Uygulama bilgilerini topla
        try:
            main_module = sys.modules['__main__']
            main_file = getattr(main_module, '__file__', None)
            if main_file:
                info["main_file"] = os.path.basename(main_file)
        except Exception:
            pass
        
        return info
    
    def _sanitize_sensitive_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Hassas verileri maskele
        
        Args:
            data (Dict[str, Any]): Temizlenecek veri
        
        Returns:
            Dict[str, Any]: Temizlenmiş veri
        """
        if not data:
            return data
        
        sanitized = {}
        
        for key, value in data.items():
            # Anahtarın hassas olup olmadığını kontrol et
            key_lower = key.lower()
            is_sensitive = any(sensitive in key_lower for sensitive in self.sensitive_fields)
            
            if is_sensitive and isinstance(value, (str, int, float, bool)):
                # Hassas veriyi maskele
                sanitized[key] = "********"
            elif isinstance(value, dict):
                # İç içe sözlükleri temizle
                sanitized[key] = self._sanitize_sensitive_data(value)
            elif isinstance(value, list) and all(isinstance(item, dict) for item in value):
                # Sözlük listelerini temizle
                sanitized[key] = [self._sanitize_sensitive_data(item) for item in value]
            else:
                # Normal verileri aynen kopyala
                sanitized[key] = value
        
        return sanitized
    
    def _truncate(self, text: str, max_length: int) -> str:
        """
        Metni belirli bir uzunlukta kısalt
        
        Args:
            text (str): Kısaltılacak metin
            max_length (int): Maksimum uzunluk
        
        Returns:
            str: Kısaltılmış metin
        """
        if len(text) <= max_length:
            return text
        
        # Metni kısalt ve sonuna "..." ekle
        return text[:max_length - 3] + "..."
    
    def to_json_string(self, log_data: Dict[str, Any]) -> str:
        """
        Log verisini JSON string'e dönüştür
        
        Args:
            log_data (Dict[str, Any]): Log verisi
        
        Returns:
            str: JSON formatında string
        """
        class DateTimeEncoder(json.JSONEncoder):
            """JSON encoder that handles datetime objects."""
            def default(self, obj):
                if isinstance(obj, datetime.datetime):
                    return obj.isoformat()
                return super().default(obj)
        
        return json.dumps(log_data, cls=DateTimeEncoder, ensure_ascii=False)
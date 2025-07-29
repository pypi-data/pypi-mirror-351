import time
import traceback
from typing import Any, Dict, Optional, Union, List
from flask import Flask, request, g, Request, Response
from werkzeug.exceptions import HTTPException

from ..client import Loggier

class LoggierFlask(Loggier):
    """
    Flask uygulamaları için Loggier entegrasyonu
    """
    
    def __init__(
        self,
        app: Optional[Flask] = None,
        api_key: Optional[str] = None,
        api_url: str = "https://api.loggier.com/api/ingest",  # host -> api_url olarak değiştirildi
        environment: str = "development",
        async_mode: bool = True,
        max_batch_size: int = 100,  # max_queue_size -> max_batch_size olarak değiştirildi
        flush_interval: int = 5,
        tags: Optional[List[str]] = None,
        context: Optional[Dict[str, Any]] = None,
        log_level: str = "info",  # min_level -> log_level olarak değiştirildi
        capture_request_data: bool = True,
        log_slow_requests: bool = True,
        slow_request_threshold: float = 1.0  # saniye cinsinden
    ):
        """
        Flask entegrasyonunu başlat
        
        Args:
            app (Flask, optional): Flask uygulaması
            api_key (str, optional): Loggier API anahtarı (app.config'den de alınabilir)
            api_url (str, optional): API endpoint URL'i (host -> api_url olarak değiştirildi)
            environment (str, optional): Ortam adı
            async_mode (bool, optional): Asenkron log gönderimi yapılsın mı?
            max_batch_size (int, optional): Asenkron modda maksimum kuyruk boyutu
            flush_interval (int, optional): Asenkron modda otomatik gönderim aralığı (saniye)
            tags (List[str], optional): Tüm loglara eklenecek etiketler
            context (Dict[str, Any], optional): Global bağlam bilgileri
            log_level (str, optional): Minimum log seviyesi (min_level -> log_level olarak değiştirildi)
            capture_request_data (bool, optional): HTTP istek verilerini yakala
            log_slow_requests (bool, optional): Yavaş istekleri logla
            slow_request_threshold (float, optional): Yavaş istek eşiği (saniye)
        """
        # Flask uygulamasından yapılandırma al
        self.app = app
        if app is not None:
            api_key = api_key or app.config.get("Loggier_API_KEY")
            environment = environment or app.config.get("Loggier_ENVIRONMENT", environment)
            tags = tags or app.config.get("Loggier_TAGS", [])
            context = context or app.config.get("Loggier_CONTEXT", {})
        
        # Ana Loggier sınıfını başlat
        super().__init__(
            api_key=api_key,
            api_url=api_url,  # host -> api_url olarak değiştirildi
            environment=environment,
            async_mode=async_mode,
            max_batch_size=max_batch_size,  # max_queue_size -> max_batch_size olarak değiştirildi
            flush_interval=flush_interval,
            tags=tags,
            context=context,
            log_level=log_level  # min_level -> log_level olarak değiştirildi (eğer varsa)
        )
        
        # Flask özellikleri
        self.capture_request_data = capture_request_data
        self.log_slow_requests = log_slow_requests
        self.slow_request_threshold = slow_request_threshold
        
        # Entegrasyonu kur
        if app is not None:
            self.init_app(app)
    
    def init_app(self, app: Flask) -> None:
        """
        Flask uygulamasına entegre et
        
        Args:
            app (Flask): Flask uygulaması
        """
        self.app = app
        
        # Flask app için default yapılandırmaları ayarla
        app.config.setdefault("Loggier_API_KEY", self.api_key)
        app.config.setdefault("Loggier_ENVIRONMENT", self.environment)
        
        # İstek öncesi hook
        @app.before_request
        def before_request():
            # İstek başlangıç zamanını kaydet
            g.start_time = time.time()
            
            # İstek ID'si oluştur ve bağlama ekle
            g.request_id = self._generate_request_id()
            
            # İstek bağlamını ekle
            with self.context(request_id=g.request_id):
                self._capture_request_start()
        
        # İstek sonrası hook
        @app.after_request
        def after_request(response: Response):
            if hasattr(g, "start_time"):
                # İstek süresini hesapla
                request_time = time.time() - g.start_time
                
                # İstek bağlamı ile log
                with self.context(request_id=getattr(g, "request_id", None)):
                    self._capture_request_end(response, request_time)
                
                # Yavaş istek kontrolü
                if self.log_slow_requests and request_time > self.slow_request_threshold:
                    with self.context(request_id=getattr(g, "request_id", None)):
                        self.warning(
                            f"Yavaş istek tespit edildi: {request.path} ({request_time:.2f}s)",
                            context={  # extra -> context olarak değiştirildi
                                "request_time": request_time,
                                "threshold": self.slow_request_threshold,
                                "path": request.path,
                                "method": request.method
                            }
                        )
            
            return response
        
        # Hata yakalama
        @app.errorhandler(Exception)
        def handle_exception(e):
            # HTTP istisnaları için normal davranış
            if isinstance(e, HTTPException):
                return e
            
            # Flask'ın orijinal hata işleyicisini çağırmadan önce hatayı logla
            with self.context(request_id=getattr(g, "request_id", None)):
                self._capture_exception(e)
            
            # Hata işlemeyi Flask'a bırak
            raise e
    
    def _generate_request_id(self) -> str:
        """
        Benzersiz istek ID'si oluştur
        
        Returns:
            str: İstek ID'si
        """
        import uuid
        return str(uuid.uuid4())
    
    def _capture_request_start(self) -> None:
        """
        İstek başlangıcını yakala
        """
        if not self.capture_request_data:
            return
        
        # İstek bilgilerini topla
        req_data = {
            "method": request.method,
            "path": request.path,
            "endpoint": request.endpoint,
            "remote_addr": request.remote_addr,
            "user_agent": request.user_agent.string,
        }
        
        # Hassas bilgileri filtreleyerek query parametrelerini al
        if request.args:
            filtered_args = {}
            for key, value in request.args.items():
                if not self._is_sensitive_data(key):
                    filtered_args[key] = value
            req_data["args"] = filtered_args
        
        # Debug modda daha fazla bilgi logla
        if self.app.debug:
            self.debug(f"İstek başladı: {request.method} {request.path}", context=req_data)  # extra -> context olarak değiştirildi
        else:
            self.info(f"İstek başladı: {request.method} {request.path}", context=req_data)  # extra -> context olarak değiştirildi
    
    def _capture_request_end(self, response: Response, request_time: float) -> None:
        """
        İstek sonucunu yakala
        
        Args:
            response (Response): Flask yanıtı
            request_time (float): İstek süresi (saniye)
        """
        if not self.capture_request_data:
            return
        
        # Yanıt bilgilerini topla
        resp_data = {
            "status_code": response.status_code,
            "content_type": response.content_type,
            "content_length": response.content_length,
            "request_time": round(request_time, 4)
        }
        
        # Başarılı yanıtlar
        if 200 <= response.status_code < 400:
            self.info(
                f"İstek tamamlandı: {request.method} {request.path} - {response.status_code}",
                context=resp_data  # extra -> context olarak değiştirildi
            )
        # Yönlendirmeler
        elif 300 <= response.status_code < 400:
            self.info(
                f"İstek yönlendirildi: {request.method} {request.path} - {response.status_code}",
                context=resp_data  # extra -> context olarak değiştirildi
            )
        # İstemci hataları
        elif 400 <= response.status_code < 500:
            self.warning(
                f"İstemci hatası: {request.method} {request.path} - {response.status_code}",
                context=resp_data  # extra -> context olarak değiştirildi
            )
        # Sunucu hataları
        else:
            self.error(
                f"Sunucu hatası: {request.method} {request.path} - {response.status_code}",
                context=resp_data  # extra -> context olarak değiştirildi
            )
    
    def _capture_exception(self, exception: Exception) -> None:
        """
        İstek sırasında oluşan hatayı yakala
        
        Args:
            exception (Exception): Yakalanan hata
        """
        # İstek bilgilerini topla
        req_data = {
            "method": request.method,
            "path": request.path,
            "endpoint": request.endpoint,
            "remote_addr": request.remote_addr,
            "user_agent": request.user_agent.string,
        }
        
        # Hatayı logla
        self.exception(
            f"İstek işlenirken hata oluştu: {request.method} {request.path}",
            exception=exception,  # exc_info -> exception olarak değiştirildi
            context=req_data  # extra -> context olarak değiştirildi
        )
    
    def _is_sensitive_data(self, key: str) -> bool:
        """
        Hassas veri kontrolü
        
        Args:
            key (str): Kontrol edilecek anahtar
        
        Returns:
            bool: Hassas veri ise True
        """
        sensitive_fields = [
            "password", "token", "auth", "secret", "key", "cookie", 
            "csrf", "session", "card", "credit", "cvv", "ssn", "social"
        ]
        key_lower = key.lower()
        return any(sensitive in key_lower for sensitive in sensitive_fields)
import time
import uuid
from typing import Any, Dict, List, Optional, Callable, Union

from fastapi import FastAPI, Request, Response
from fastapi.middleware.base import BaseHTTPMiddleware
from starlette.middleware.base import RequestResponseEndpoint
from starlette.responses import JSONResponse

from ..client import Loggier

class LoggierFastAPI(Loggier):
    """
    FastAPI uygulamaları için Loggier entegrasyonu
    """
    
    def __init__(
        self,
        app: Optional[FastAPI] = None,
        api_key: str = None,
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
        slow_request_threshold: float = 1.0,  # saniye cinsinden
        exclude_paths: Optional[List[str]] = None
    ):
        """
        FastAPI entegrasyonunu başlat
        
        Args:
            app (FastAPI, optional): FastAPI uygulaması
            api_key (str): Loggier API anahtarı
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
            exclude_paths (List[str], optional): Loglama dışında tutulacak path'ler
        """
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
        
        # FastAPI özellikleri
        self.capture_request_data = capture_request_data
        self.log_slow_requests = log_slow_requests
        self.slow_request_threshold = slow_request_threshold
        self.exclude_paths = exclude_paths or []
        
        # Eğer bir FastAPI uygulaması verilmişse, middleware'i ekle
        if app:
            self.init_app(app)
    
    def init_app(self, app: FastAPI) -> None:
        """
        FastAPI uygulamasına middleware olarak ekle
        
        Args:
            app (FastAPI): FastAPI uygulaması
        """
        app.add_middleware(self.middleware_class)
        
        # Exception handler ekle
        @app.exception_handler(Exception)
        async def exception_handler(request: Request, exc: Exception):
            """
            Yakalanmayan hataları logla
            """
            # Hata bağlamını oluştur
            if hasattr(request.state, "loggier_request_id"):
                with self.context(request_id=request.state.loggier_request_id):
                    await self._capture_exception(request, exc)
            else:
                await self._capture_exception(request, exc)
            
            # Hata yanıtını oluştur
            return JSONResponse(
                status_code=500,
                content={"detail": "Internal Server Error"}
            )
    
    @property
    def middleware_class(self):
        """
        FastAPI middleware sınıfını oluştur
        
        Returns:
            BaseHTTPMiddleware: FastAPI middleware sınıfı
        """
        loggier_instance = self
        
        class LoggierMiddleware(BaseHTTPMiddleware):
            async def dispatch(
                self, request: Request, call_next: RequestResponseEndpoint
            ) -> Response:
                # İstek path'inin hariç tutulanlar arasında olup olmadığını kontrol et
                path = request.url.path
                if any(path.startswith(exclude) for exclude in loggier_instance.exclude_paths):
                    return await call_next(request)
                
                # İstek ID'si oluştur
                request_id = str(uuid.uuid4())
                request.state.loggier_request_id = request_id
                
                # İstek başlangıç zamanını kaydet
                start_time = time.time()
                
                if loggier_instance.capture_request_data:
                    # İstek bağlamını ekle
                    with loggier_instance.context(request_id=request_id):
                        await loggier_instance._capture_request_start(request)
                
                try:
                    # İsteği işle
                    response = await call_next(request)
                    
                    # İstek süresini hesapla
                    request_time = time.time() - start_time
                    
                    if loggier_instance.capture_request_data:
                        # İstek bağlamını ekle
                        with loggier_instance.context(request_id=request_id):
                            await loggier_instance._capture_request_end(request, response, request_time)
                    
                    # Yavaş istek kontrolü
                    if (loggier_instance.log_slow_requests and 
                            request_time > loggier_instance.slow_request_threshold):
                        with loggier_instance.context(request_id=request_id):
                            loggier_instance.warning(
                                f"Yavaş istek tespit edildi: {path} ({request_time:.2f}s)",
                                context={  # extra -> context olarak değiştirildi
                                    "request_time": request_time,
                                    "threshold": loggier_instance.slow_request_threshold,
                                    "path": path,
                                    "method": request.method
                                }
                            )
                    
                    return response
                
                except Exception as exc:
                    # İstek süresini hesapla
                    request_time = time.time() - start_time
                    
                    # Hatayı logla
                    with loggier_instance.context(request_id=request_id):
                        await loggier_instance._capture_exception(request, exc)
                    
                    # Hatayı yeniden fırlat
                    raise exc
        
        return LoggierMiddleware
    
    async def _capture_request_start(self, request: Request) -> None:
        """
        İstek başlangıcını yakala
        
        Args:
            request (Request): FastAPI istek nesnesi
        """
        # İstek bilgilerini topla
        path = request.url.path
        client_host = request.client.host if request.client else "unknown"
        
        req_data = {
            "method": request.method,
            "path": path,
            "remote_addr": client_host,
            "url": str(request.url),
        }
        
        # Query parametrelerini al (hassas veriler hariç)
        if request.query_params:
            filtered_params = {}
            for key, value in request.query_params.items():
                if not self._is_sensitive_data(key):
                    filtered_params[key] = value
            req_data["query_params"] = filtered_params
        
        # HTTP başlıklarını al (hassas veriler hariç)
        if request.headers:
            filtered_headers = {}
            for key, value in request.headers.items():
                if not self._is_sensitive_data(key) and key.lower() not in ["authorization", "cookie"]:
                    filtered_headers[key] = value
            req_data["headers"] = filtered_headers
        
        self.info(f"İstek başladı: {request.method} {path}", context=req_data)  # extra -> context olarak değiştirildi
    
    async def _capture_request_end(self, request: Request, response: Response, request_time: float) -> None:
        """
        İstek sonucunu yakala
        
        Args:
            request (Request): FastAPI istek nesnesi
            response (Response): FastAPI yanıt nesnesi
            request_time (float): İstek süresi (saniye)
        """
        path = request.url.path
        
        # Yanıt bilgilerini topla
        resp_data = {
            "status_code": response.status_code,
            "content_type": response.headers.get("content-type", ""),
            "request_time": round(request_time, 4)
        }
        
        # Başarılı yanıtlar
        if 200 <= response.status_code < 400:
            self.info(
                f"İstek tamamlandı: {request.method} {path} - {response.status_code}",
                context=resp_data  # extra -> context olarak değiştirildi
            )
        # Yönlendirmeler
        elif 300 <= response.status_code < 400:
            self.info(
                f"İstek yönlendirildi: {request.method} {path} - {response.status_code}",
                context=resp_data  # extra -> context olarak değiştirildi
            )
        # İstemci hataları
        elif 400 <= response.status_code < 500:
            self.warning(
                f"İstemci hatası: {request.method} {path} - {response.status_code}",
                context=resp_data  # extra -> context olarak değiştirildi
            )
        # Sunucu hataları
        else:
            self.error(
                f"Sunucu hatası: {request.method} {path} - {response.status_code}",
                context=resp_data  # extra -> context olarak değiştirildi
            )
    
    async def _capture_exception(self, request: Request, exception: Exception) -> None:
        """
        İstek sırasında oluşan hatayı yakala
        
        Args:
            request (Request): FastAPI istek nesnesi
            exception (Exception): Yakalanan hata
        """
        # İstek bilgilerini topla
        path = request.url.path
        client_host = request.client.host if request.client else "unknown"
        
        req_data = {
            "method": request.method,
            "path": path,
            "remote_addr": client_host,
            "url": str(request.url),
        }
        
        # Hatayı logla
        self.exception(
            f"İstek işlenirken hata oluştu: {request.method} {path}",
            exception=exception,  # exception olarak düzeltildi
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
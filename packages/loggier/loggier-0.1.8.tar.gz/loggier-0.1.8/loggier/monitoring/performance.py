# monitoring/performance.py

import functools
import inspect
import time
import traceback
import urllib.parse
from typing import Dict, List, Any, Optional, Union, Callable, Type, TypeVar
import logging
from datetime import datetime

# Decorator için tip tanımlaması
F = TypeVar('F', bound=Callable[..., Any])


class PerformanceMonitor:
    """
    Fonksiyon çağrıları, database işlemleri ve HTTP isteklerini izlemek için
    kullanılan performans izleme araçları.
    """
    
    def __init__(self, client, log_level: int = logging.INFO):
        """
        PerformanceMonitor sınıfını başlatır.
        
        Args:
            client: Loggier istemcisi
            log_level: Logging seviyesi
        """
        self.logger = logging.getLogger("loggier.performance")
        self.logger.setLevel(log_level)
        
        self.client = client
        self.stats = {
            "total_monitored_calls": 0,
            "slow_calls": 0,
            "error_calls": 0
        }
    
    def trace_function(
        self,
        name: Optional[str] = None,
        threshold_ms: int = 500,
        tags: Optional[List[str]] = None,
        include_args: bool = False,
        include_return: bool = False,
        log_level: str = "INFO"
    ) -> Callable[[F], F]:
        """
        Fonksiyon çağrılarını izleyen bir dekoratör.
        
        Args:
            name: İzleme için özel isim. None ise fonksiyon adı kullanılır
            threshold_ms: Bu süreden uzun süren çağrılar "yavaş" kabul edilir (milisaniye)
            tags: Logda kullanılacak ek etiketler
            include_args: True ise çağrı argümanları loglanır
            include_return: True ise dönüş değeri loglanır
            log_level: Log seviyesi (INFO, WARNING, vb.)
            
        Returns:
            Callable: Dekorasyonlu fonksiyon
        """
        def decorator(func: F) -> F:
            # Fonksiyon adını belirle
            func_name = name or func.__qualname__
            
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                start_time = time.time()
                exception = None
                return_value = None
                
                # Fonksiyon bilgilerini topla
                module_name = func.__module__
                file_name = inspect.getfile(func)
                line_number = inspect.getsourcelines(func)[1]
                
                # Argümanları hazırla (eğer istenirse)
                call_args = None
                if include_args:
                    # İçeriği güvenli şekilde string'e çevirme
                    try:
                        # kwargs doğrudan alınabilir
                        safe_kwargs = {k: str(v) for k, v in kwargs.items()}
                        
                        # Fonksiyon imzasından argüman isimlerini al
                        sig = inspect.signature(func)
                        param_names = list(sig.parameters.keys())
                        
                        # Pozisyonel argümanları isimleriyle eşleştir
                        safe_args = {}
                        for i, arg in enumerate(args):
                            if i < len(param_names):
                                safe_args[param_names[i]] = str(arg)
                            else:
                                safe_args[f"arg{i}"] = str(arg)
                        
                        call_args = {"args": safe_args, "kwargs": safe_kwargs}
                    except Exception as e:
                        call_args = {"error": f"Could not serialize arguments: {str(e)}"}
                
                try:
                    # Fonksiyonu çağır
                    return_value = func(*args, **kwargs)
                    return return_value
                except Exception as e:
                    # Hatayı yakala ve tekrar fırlat
                    exception = e
                    raise
                finally:
                    # Çalışma süresini hesapla
                    end_time = time.time()
                    duration_ms = (end_time - start_time) * 1000
                    
                    # Loglamayı gerçekleştir
                    self._log_function_call(
                        func_name=func_name,
                        module_name=module_name,
                        file_name=file_name,
                        line_number=line_number,
                        duration_ms=duration_ms,
                        threshold_ms=threshold_ms,
                        call_args=call_args,
                        return_value=return_value if include_return else None,
                        exception=exception,
                        tags=tags,
                        log_level=log_level
                    )
            
            return wrapper
        
        return decorator
    
    def trace_http(
        self,
        name: Optional[str] = None,
        threshold_ms: int = 1000,
        tags: Optional[List[str]] = None,
        mask_headers: Optional[List[str]] = None,
        mask_params: Optional[List[str]] = None,
        include_body: bool = False,
        log_level: str = "INFO"
    ) -> Callable[[F], F]:
        """
        HTTP isteklerini izleyen bir dekoratör.
        
        Args:
            name: İzleme için özel isim. None ise fonksiyon adı kullanılır
            threshold_ms: Bu süreden uzun süren istekler "yavaş" kabul edilir (milisaniye)
            tags: Logda kullanılacak ek etiketler
            mask_headers: Maskelenecek HTTP header'ları
            mask_params: Maskelenecek URL parametreleri
            include_body: True ise istek/yanıt gövdeleri loglanır (dikkatli kullanın)
            log_level: Log seviyesi (INFO, WARNING, vb.)
            
        Returns:
            Callable: Dekorasyonlu fonksiyon
        """
        # Varsayılan maskeleme listeleri
        default_mask_headers = [
            "authorization", "x-api-key", "api-key", "password", "token",
            "cookie", "session", "x-csrf", "csrf", "secret"
        ]
        
        default_mask_params = [
            "api_key", "apikey", "key", "token", "password", "secret", "auth"
        ]
        
        # Maskeleme listelerini birleştir
        mask_headers = (mask_headers or []) + default_mask_headers
        mask_params = (mask_params or []) + default_mask_params
        
        def decorator(func: F) -> F:
            # Fonksiyon adını belirle
            func_name = name or func.__qualname__
            
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                start_time = time.time()
                exception = None
                response = None
                
                # HTTP isteği bilgilerini yakala
                request_info = self._extract_request_info(args, kwargs, mask_headers, mask_params, include_body)
                
                try:
                    # Fonksiyonu çağır
                    response = func(*args, **kwargs)
                    return response
                except Exception as e:
                    # Hatayı yakala ve tekrar fırlat
                    exception = e
                    raise
                finally:
                    # Çalışma süresini hesapla
                    end_time = time.time()
                    duration_ms = (end_time - start_time) * 1000
                    
                    # Yanıt bilgilerini yakala
                    response_info = self._extract_response_info(response, include_body)
                    
                    # Loglamayı gerçekleştir
                    self._log_http_call(
                        func_name=func_name,
                        request_info=request_info,
                        response_info=response_info,
                        duration_ms=duration_ms,
                        threshold_ms=threshold_ms,
                        exception=exception,
                        tags=tags,
                        log_level=log_level
                    )
            
            return wrapper
        
        return decorator
    
    def trace_database(
        self,
        name: Optional[str] = None,
        threshold_ms: int = 100,
        tags: Optional[List[str]] = None,
        include_params: bool = False,
        log_level: str = "INFO"
    ) -> Callable[[F], F]:
        """
        Veritabanı işlemlerini izleyen bir dekoratör.
        
        Args:
            name: İzleme için özel isim. None ise fonksiyon adı kullanılır
            threshold_ms: Bu süreden uzun süren sorgular "yavaş" kabul edilir (milisaniye)
            tags: Logda kullanılacak ek etiketler
            include_params: True ise sorgu parametreleri loglanır (hassas veriler olabilir)
            log_level: Log seviyesi (INFO, WARNING, vb.)
            
        Returns:
            Callable: Dekorasyonlu fonksiyon
        """
        def decorator(func: F) -> F:
            # Fonksiyon adını belirle
            func_name = name or func.__qualname__
            
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                start_time = time.time()
                exception = None
                
                # Sorgu bilgilerini toplamaya çalış
                query_info = self._extract_query_info(args, kwargs, include_params)
                
                try:
                    # Fonksiyonu çağır
                    result = func(*args, **kwargs)
                    return result
                except Exception as e:
                    # Hatayı yakala ve tekrar fırlat
                    exception = e
                    raise
                finally:
                    # Çalışma süresini hesapla
                    end_time = time.time()
                    duration_ms = (end_time - start_time) * 1000
                    
                    # Loglamayı gerçekleştir
                    self._log_database_call(
                        func_name=func_name,
                        query_info=query_info,
                        duration_ms=duration_ms,
                        threshold_ms=threshold_ms,
                        exception=exception,
                        tags=tags,
                        log_level=log_level
                    )
            
            return wrapper
        
        return decorator
    
    def _log_function_call(
        self,
        func_name: str,
        module_name: str,
        file_name: str,
        line_number: int,
        duration_ms: float,
        threshold_ms: int,
        call_args: Optional[Dict[str, Any]] = None,
        return_value: Optional[Any] = None,
        exception: Optional[Exception] = None,
        tags: Optional[List[str]] = None,
        log_level: str = "INFO"
    ) -> None:
        """Fonksiyon çağrısını loglar."""
        # İstatistikleri güncelle
        self.stats["total_monitored_calls"] += 1
        
        # Yavaş çağrı kontrolü
        is_slow = duration_ms >= threshold_ms
        if is_slow:
            self.stats["slow_calls"] += 1
        
        # Hata kontrolü
        has_error = exception is not None
        if has_error:
            self.stats["error_calls"] += 1
        
        # Log seviyesini belirle
        effective_log_level = log_level
        if has_error:
            effective_log_level = "ERROR"
        elif is_slow:
            effective_log_level = "WARNING"
        
        # Mesajı oluştur
        message = f"Function call: {func_name}"
        if is_slow:
            message += f" [SLOW: {duration_ms:.2f}ms >= {threshold_ms}ms]"
        if has_error:
            message += f" [ERROR: {exception.__class__.__name__}]"
        
        # Etiketleri hazırla
        all_tags = ["performance", "function_call"]
        if tags:
            all_tags.extend(tags)
        if is_slow:
            all_tags.append("slow")
        if has_error:
            all_tags.append("error")
        
        # Bağlam bilgisini hazırla
        context = {
            "function": {
                "name": func_name,
                "module": module_name,
                "file": file_name,
                "line": line_number
            },
            "duration_ms": duration_ms,
            "performance": {
                "is_slow": is_slow,
                "threshold_ms": threshold_ms
            }
        }
        
        # Argümanları ekle (varsa)
        if call_args:
            context["call_args"] = call_args
            
        # Dönüş değerini ekle (varsa ve hata yoksa)
        if return_value is not None and not has_error:
            try:
                context["return_value"] = str(return_value)
            except Exception:
                context["return_value"] = "<non-serializable>"
        
        # Loggier aracılığıyla log gönder
        if has_error:
            self.client.error(message, exception=exception, context=context, tags=all_tags)
        elif is_slow:
            self.client.warning(message, context=context, tags=all_tags)
        else:
            log_method = getattr(self.client, effective_log_level.lower(), self.client.info)
            log_method(message, context=context, tags=all_tags)
    
    def _extract_request_info(
        self,
        args: tuple,
        kwargs: dict,
        mask_headers: List[str],
        mask_params: List[str],
        include_body: bool
    ) -> Dict[str, Any]:
        """HTTP isteği bilgilerini çıkarır."""
        # İstek bilgilerini toplayabileceğimiz popüler HTTP kütüphanelerini dene
        request_info = {
            "library": "unknown",
            "method": "unknown",
            "url": "unknown"
        }
        
        try:
            # requests, httpx, urllib3 gibi kütüphaneler için destek
            
            # requests kütüphanesi tespiti
            if len(args) > 0 and hasattr(args[0], "upper") and callable(args[0].upper):
                # İlk argüman muhtemelen HTTP method (GET, POST, vb.)
                request_info["method"] = args[0].upper()
                
                # URL ikinci argüman olabilir
                if len(args) > 1 and isinstance(args[1], str):
                    request_info["url"] = self._mask_url_params(args[1], mask_params)
                    request_info["library"] = "requests"
                
                # kwargs'da url var mı?
                elif "url" in kwargs and isinstance(kwargs["url"], str):
                    request_info["url"] = self._mask_url_params(kwargs["url"], mask_params)
                    request_info["library"] = "requests"
            
            # Headers bilgisini topla
            if "headers" in kwargs and isinstance(kwargs["headers"], dict):
                request_info["headers"] = self._mask_headers(kwargs["headers"], mask_headers)
            
            # Body ekle (istenirse)
            if include_body and "data" in kwargs:
                try:
                    if isinstance(kwargs["data"], dict):
                        request_info["body"] = kwargs["data"]
                    elif isinstance(kwargs["data"], str):
                        request_info["body"] = kwargs["data"][:1000]  # İlk 1000 karakter
                    else:
                        request_info["body"] = str(kwargs["data"])[:1000]
                except Exception:
                    request_info["body"] = "<non-serializable>"
            
            if include_body and "json" in kwargs:
                request_info["json_body"] = kwargs["json"]
        
        except Exception as e:
            request_info["error"] = f"Could not extract request info: {str(e)}"
        
        return request_info
    
    def _extract_response_info(self, response: Any, include_body: bool) -> Dict[str, Any]:
        """HTTP yanıt bilgilerini çıkarır."""
        if response is None:
            return {"error": "No response received"}
        
        response_info = {
            "type": type(response).__name__
        }
        
        try:
            # Status code
            if hasattr(response, "status_code"):
                response_info["status_code"] = response.status_code
            
            # Headers
            if hasattr(response, "headers"):
                response_info["headers"] = dict(response.headers)
            
            # Content-Type
            if hasattr(response, "headers") and "content-type" in response.headers:
                response_info["content_type"] = response.headers["content-type"]
            
            # Body (istenirse)
            if include_body:
                if hasattr(response, "text"):
                    # İlk 1000 karakteri al
                    response_info["body"] = response.text[:1000]
                elif hasattr(response, "content"):
                    try:
                        # İlk 1000 karakteri al
                        response_info["body"] = response.content.decode("utf-8")[:1000]
                    except Exception:
                        response_info["body"] = "<binary-data>"
        
        except Exception as e:
            response_info["error"] = f"Could not extract response info: {str(e)}"
        
        return response_info
    
    def _extract_query_info(self, args: tuple, kwargs: dict, include_params: bool) -> Dict[str, Any]:
        """Veritabanı sorgu bilgilerini çıkarır."""
        query_info = {
            "type": "unknown"
        }
        
        try:
            # SQLAlchemy sorgusu tespiti
            if len(args) > 0:
                arg = args[0]
                # SQLAlchemy Statement
                if hasattr(arg, "compile") and callable(arg.compile):
                    query_info["type"] = "sqlalchemy"
                    
                    if hasattr(arg, "statement") and hasattr(arg.statement, "__str__"):
                        query_info["query"] = str(arg.statement)
                    else:
                        try:
                            query_info["query"] = str(arg)
                        except:
                            query_info["query"] = "<non-serializable>"
                
                # SQL string
                elif isinstance(arg, str) and ("SELECT" in arg.upper() or "INSERT" in arg.upper() 
                                            or "UPDATE" in arg.upper() or "DELETE" in arg.upper()):
                    query_info["type"] = "sql"
                    query_info["query"] = arg
                
                # Django QuerySet tespiti
                elif hasattr(arg, "query") and hasattr(arg.query, "get_compiler"):
                    query_info["type"] = "django"
                    try:
                        query_info["query"] = str(arg.query)
                    except:
                        query_info["query"] = "<django-queryset>"
            
            # Parametreleri ekle (istenirse)
            if include_params:
                if len(args) > 1:
                    query_info["params"] = str(args[1])
                elif "params" in kwargs:
                    query_info["params"] = str(kwargs["params"])
        
        except Exception as e:
            query_info["error"] = f"Could not extract query info: {str(e)}"
        
        return query_info
    
    def _mask_url_params(self, url: str, mask_params: List[str]) -> str:
        """URL'deki hassas parametreleri maskeler."""
        try:
            # URL'yi parse et
            parsed_url = urllib.parse.urlparse(url)
            
            # Query parametrelerini al
            query_params = urllib.parse.parse_qs(parsed_url.query)
            
            # Hassas parametreleri maskele
            for param in mask_params:
                if param in query_params:
                    query_params[param] = ["***MASKED***"]
            
            # URL'yi yeniden oluştur
            masked_query = urllib.parse.urlencode(query_params, doseq=True)
            masked_url = urllib.parse.urlunparse((
                parsed_url.scheme,
                parsed_url.netloc,
                parsed_url.path,
                parsed_url.params,
                masked_query,
                parsed_url.fragment
            ))
            
            return masked_url
        except Exception:
            # Hata durumunda orijinal URL'yi döndür
            return url
    
    def _mask_headers(self, headers: Dict[str, str], mask_headers: List[str]) -> Dict[str, str]:
        """HTTP başlıklarındaki hassas bilgileri maskeler."""
        masked_headers = {}
        
        for key, value in headers.items():
            # Anahtar isimlerini küçük harfe çevirerek karşılaştır
            if any(mask_key in key.lower() for mask_key in mask_headers):
                masked_headers[key] = "***MASKED***"
            else:
                masked_headers[key] = value
        
        return masked_headers
    
    def _log_http_call(
        self,
        func_name: str,
        request_info: Dict[str, Any],
        response_info: Dict[str, Any],
        duration_ms: float,
        threshold_ms: int,
        exception: Optional[Exception] = None,
        tags: Optional[List[str]] = None,
        log_level: str = "INFO"
    ) -> None:
        """HTTP isteğini loglar."""
        # İstatistikleri güncelle
        self.stats["total_monitored_calls"] += 1
        
        # Yavaş çağrı kontrolü
        is_slow = duration_ms >= threshold_ms
        if is_slow:
            self.stats["slow_calls"] += 1
        
        # Hata kontrolü
        has_error = exception is not None
        if has_error:
            self.stats["error_calls"] += 1
        
        # Log seviyesini belirle
        effective_log_level = log_level
        if has_error:
            effective_log_level = "ERROR"
        elif is_slow:
            effective_log_level = "WARNING"
        
        # HTTP yanıt durum kodunu kontrol et
        status_code = response_info.get("status_code")
        is_error_status = False
        if status_code and status_code >= 400:
            is_error_status = True
            effective_log_level = "WARNING"
            if status_code >= 500:
                effective_log_level = "ERROR"
        
        # Mesajı oluştur
        method = request_info.get("method", "HTTP")
        url = request_info.get("url", "unknown")
        message = f"HTTP {method} {url}"
        
        if is_slow:
            message += f" [SLOW: {duration_ms:.2f}ms >= {threshold_ms}ms]"
        if has_error:
            message += f" [ERROR: {exception.__class__.__name__}]"
        elif is_error_status:
            message += f" [HTTP {status_code}]"
        
        # Etiketleri hazırla
        all_tags = ["performance", "http_request"]
        if tags:
            all_tags.extend(tags)
        if is_slow:
            all_tags.append("slow")
        if has_error or is_error_status:
            all_tags.append("error")
        
        # Bağlam bilgisini hazırla
        context = {
            "http_call": {
                "function": func_name,
                "request": request_info,
                "response": response_info,
                "duration_ms": duration_ms,
                "performance": {
                    "is_slow": is_slow,
                    "threshold_ms": threshold_ms
                }
            }
        }
        
        # Loggier aracılığıyla log gönder
        if has_error:
            self.client.error(message, exception=exception, context=context, tags=all_tags)
        elif effective_log_level == "ERROR":
            self.client.error(message, context=context, tags=all_tags)
        elif effective_log_level == "WARNING":
            self.client.warning(message, context=context, tags=all_tags)
        else:
            log_method = getattr(self.client, effective_log_level.lower(), self.client.info)
            log_method(message, context=context, tags=all_tags)
    
    def _log_database_call(
        self,
        func_name: str,
        query_info: Dict[str, Any],
        duration_ms: float,
        threshold_ms: int,
        exception: Optional[Exception] = None,
        tags: Optional[List[str]] = None,
        log_level: str = "INFO"
    ) -> None:
        """Veritabanı sorgusunu loglar."""
        # İstatistikleri güncelle
        self.stats["total_monitored_calls"] += 1
        
        # Yavaş çağrı kontrolü
        is_slow = duration_ms >= threshold_ms
        if is_slow:
            self.stats["slow_calls"] += 1
        
        # Hata kontrolü
        has_error = exception is not None
        if has_error:
            self.stats["error_calls"] += 1
        
        # Log seviyesini belirle
        effective_log_level = log_level
        if has_error:
            effective_log_level = "ERROR"
        elif is_slow:
            effective_log_level = "WARNING"
        
        # Mesajı oluştur
        query_type = query_info.get("type", "Database")
        query_text = query_info.get("query", "")
        # Sorgu metnini kısalt
        query_summary = query_text[:50] + "..." if len(query_text) > 50 else query_text
        
        message = f"{query_type.upper()} query: {query_summary}"
        
        if is_slow:
            message += f" [SLOW: {duration_ms:.2f}ms >= {threshold_ms}ms]"
        if has_error:
            message += f" [ERROR: {exception.__class__.__name__}]"
        
        # Etiketleri hazırla
        all_tags = ["performance", "database", query_info.get("type", "unknown").lower()]
        if tags:
            all_tags.extend(tags)
        if is_slow:
            all_tags.append("slow_query")
        if has_error:
            all_tags.append("error")
        
        # Bağlam bilgisini hazırla
        context = {
            "database_call": {
                "function": func_name,
                "query": query_info,
                "duration_ms": duration_ms,
                "performance": {
                    "is_slow": is_slow,
                    "threshold_ms": threshold_ms
                }
            }
        }
        
        # Loggier aracılığıyla log gönder
        if has_error:
            self.client.error(message, exception=exception, context=context, tags=all_tags)
        elif is_slow:
            self.client.warning(message, context=context, tags=all_tags)
        else:
            log_method = getattr(self.client, effective_log_level.lower(), self.client.info)
            log_method(message, context=context, tags=all_tags)
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Performans izleme istatistiklerini döndürür.
        
        Returns:
            Dict[str, Any]: İstatistik bilgileri
        """
        return self.stats.copy()
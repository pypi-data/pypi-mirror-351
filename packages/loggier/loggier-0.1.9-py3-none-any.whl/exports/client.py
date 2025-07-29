# client.py

import os
import sys
import platform
import socket
import uuid
import threading
import traceback
import logging
import json
import time
from typing import Dict, List, Any, Optional, Union, Callable
from datetime import datetime

# Dahili modüller
from .handlers.api_handler import APIHandler
from .handlers.async_handler import AsyncLogHandler
from .handlers.cache_handler import CacheHandler
from .formatters.json_formatter import JSONFormatter
from .utils.context import Context
from .utils.error import ExceptionReporter, capture_exceptions, patch_thread_excepthook
from .utils.network import NetworkMonitor

class Loggier:
    """
    Loggier/Loggier istemci kütüphanesi ana sınıfı.
    Bu sınıf, log kayıtlarını toplar, biçimlendirir ve API'ye gönderir.
    """
    
    DEFAULT_LOG_LEVEL = logging.INFO
    
    # client.py içindeki Loggier sınıfına yapılacak eklemeler

    def __init__(
        self,
        api_key: str,
        project_name: Optional[str] = None,
        environment: str = "development",
        api_url: Optional[str] = None,
        service_name: Optional[str] = None,
        async_mode: bool = True,
        capture_uncaught: bool = True,
        log_level: int = DEFAULT_LOG_LEVEL,
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
    ):
        """
        Loggier istemcisini yapılandırır.
        
        Args:
            api_key: Loggier API anahtarı
            project_name: Proje adı. Belirtilmezse API anahtarına bağlı projeyi kullanır.
            environment: Çalışma ortamı (development, staging, production vb.)
            api_url: API URL adresi. Belirtilmezse varsayılan kullanılır.
            service_name: Servis/uygulama adı. Belirtilmezse otomatik oluşturulur.
            async_mode: True ise loglar arka planda gönderilir, False ise senkron gönderilir.
            capture_uncaught: True ise yakalanmayan istisnalar otomatik raporlanır.
            log_level: Minimum log seviyesi
            enable_caching: Yerel önbellek sistemini etkinleştirir/devre dışı bırakır.
            cache_dir: Önbellek dizini yolu. None ise varsayılan konum kullanılır.
            max_batch_size: Bir defada gönderilecek maksimum log sayısı.
            flush_interval: Saniye cinsinden otomatik boşaltma aralığı.
            sensitive_fields: Maskelenecek hassas alan adları listesi.
            max_retries: Başarısız istekler için maksimum yeniden deneme sayısı.
            http_timeout: HTTP istekleri için zaman aşımı süresi (saniye).
            network_check_interval: Ağ bağlantısı kontrol aralığı (saniye).
            tags: Tüm loglara eklenecek etiketler listesi.
            enable_performance_monitoring: Performans izleme araçlarını etkinleştirir/devre dışı bırakır.
        """
        self.api_key = api_key
        self.project_name = project_name
        self.environment = environment
        self.service_name = service_name or self._generate_service_name()
        self.tags = tags or []
        
        # Logger yapılandırması
        self.logger = logging.getLogger("loggier")
        self.logger.setLevel(log_level)
        
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
        
        # Bağlam yönetimi
        self.context = Context()
        # Global bağlam oluşturma
        self.context.update_global({
            "environment": environment,
            "service_name": self.service_name,
            "tags": self.tags
        })
        
        # API Handler oluşturma
        api_url = api_url or "https://api.loggier.app"
        self.api_handler = APIHandler(
            api_key=api_key,
            api_url=api_url,
            project_name=project_name,
            max_retries=max_retries,
            timeout=http_timeout
        )
        
        # Biçimlendirici oluşturma
        self.formatter = JSONFormatter(
            sensitive_fields=sensitive_fields or ["password", "token", "api_key", "secret"]
        )
        
        # Ağ durumu izleme
        self.network_monitor = NetworkMonitor(
            check_interval=network_check_interval,
            api_handler=self.api_handler
        )
        
        # Önbellek sistemi
        self.cache_handler = None
        if enable_caching:
            self.cache_handler = CacheHandler(
                cache_dir=cache_dir,
                max_cache_size_mb=100,  # Varsayılan 100MB
                max_cache_age_days=7,  # Varsayılan 7 gün
                use_sqlite=True,
                sync_interval_seconds=60,
                log_level=log_level
            )
            # Ağ durumu değişikliklerini önbelleğe bildir
            self.network_monitor.add_status_callback(self.cache_handler.set_online_status)
        
        # Async handler (arka planda gönderim için)
        self.async_handler = None
        if async_mode:
            self.async_handler = AsyncLogHandler(
                api_handler=self.api_handler,
                max_batch_size=max_batch_size,
                flush_interval=flush_interval,
                cache_handler=self.cache_handler
            )
        
        # Çalışma zamanı bilgisi toplama
        self.runtime_info = self._collect_runtime_info()
        
        # İstisna yakalama
        if capture_uncaught:
            self.exception_reporter = ExceptionReporter(self)
            sys.excepthook = self.exception_reporter.handle_exception
            patch_thread_excepthook()
        
        # Performance Monitor eklendi
        self.performance_monitor = None
        if enable_performance_monitoring:
            from .monitoring.performance import PerformanceMonitor
            self.performance_monitor = PerformanceMonitor(client=self, log_level=log_level)
        
        # İstatistikler
        self.stats = {
            "logs_sent": 0,
            "logs_failed": 0,
            "start_time": datetime.now().isoformat()
        }
        
        self.logger.info(f"Loggier initialized for project '{project_name}' in {environment} environment")


    # Loggier sınıfına eklenecek yeni performans izleme metodları

    def trace_function(
        self,
        name: Optional[str] = None,
        threshold_ms: int = 500,
        tags: Optional[List[str]] = None,
        include_args: bool = False,
        include_return: bool = False,
        log_level: str = "INFO"
    ):
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
            Callable: Dekorasyon fonksiyonu
            
        Örnek kullanım:
            @loggier.trace_function(threshold_ms=100)
            def slow_function():
                time.sleep(0.2)
        """
        if self.performance_monitor is None:
            # PerformanceMonitor etkin değil, noop dekoratör döndür
            def noop_decorator(func):
                return func
            return noop_decorator
        
        return self.performance_monitor.trace_function(
            name=name,
            threshold_ms=threshold_ms,
            tags=tags,
            include_args=include_args,
            include_return=include_return,
            log_level=log_level
        )

    def trace_http(
        self,
        name: Optional[str] = None,
        threshold_ms: int = 1000,
        tags: Optional[List[str]] = None,
        mask_headers: Optional[List[str]] = None,
        mask_params: Optional[List[str]] = None,
        include_body: bool = False,
        log_level: str = "INFO"
    ):
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
            Callable: Dekorasyon fonksiyonu
            
        Örnek kullanım:
            @loggier.trace_http(threshold_ms=2000)
            def fetch_data(url):
                return requests.get(url)
        """
        if self.performance_monitor is None:
            # PerformanceMonitor etkin değil, noop dekoratör döndür
            def noop_decorator(func):
                return func
            return noop_decorator
        
        return self.performance_monitor.trace_http(
            name=name,
            threshold_ms=threshold_ms,
            tags=tags,
            mask_headers=mask_headers,
            mask_params=mask_params,
            include_body=include_body,
            log_level=log_level
        )

    def trace_database(
        self,
        name: Optional[str] = None,
        threshold_ms: int = 100,
        tags: Optional[List[str]] = None,
        include_params: bool = False,
        log_level: str = "INFO"
    ):
        """
        Veritabanı işlemlerini izleyen bir dekoratör.
        
        Args:
            name: İzleme için özel isim. None ise fonksiyon adı kullanılır
            threshold_ms: Bu süreden uzun süren sorgular "yavaş" kabul edilir (milisaniye)
            tags: Logda kullanılacak ek etiketler
            include_params: True ise sorgu parametreleri loglanır (hassas veriler olabilir)
            log_level: Log seviyesi (INFO, WARNING, vb.)
            
        Returns:
            Callable: Dekorasyon fonksiyonu
            
        Örnek kullanım:
            @loggier.trace_database(threshold_ms=50)
            def get_user(user_id):
                return session.query(User).filter_by(id=user_id).first()
        """
        if self.performance_monitor is None:
            # PerformanceMonitor etkin değil, noop dekoratör döndür
            def noop_decorator(func):
                return func
            return noop_decorator
        
        return self.performance_monitor.trace_database(
            name=name,
            threshold_ms=threshold_ms,
            tags=tags,
            include_params=include_params,
            log_level=log_level
        )

    def _generate_service_name(self) -> str:
        """Servis adı belirtilmemişse, çalıştırılan Python dosyasından otomatik bir ad oluşturur."""
        try:
            main_module = sys.modules['__main__']
            if hasattr(main_module, '__file__'):
                return os.path.basename(main_module.__file__).split('.')[0]
            else:
                return f"python-{os.getpid()}"
        except Exception:
            return f"python-{os.getpid()}"
    
    def _collect_runtime_info(self) -> Dict[str, Any]:
        """Sistem ve çalışma zamanı bilgilerini toplar."""
        info = {
            "python_version": platform.python_version(),
            "platform": platform.platform(),
            "system": platform.system(),
            "release": platform.release(),
            "hostname": socket.gethostname(),
            "process_id": os.getpid(),
            "thread_id": threading.get_ident()
        }
        
        # Python paketlerini toplama (sadece ilgili olanları)
        try:
            import pkg_resources
            packages = {pkg.key: pkg.version for pkg in pkg_resources.working_set}
            important_packages = {}
            
            # Önemli paketleri seç
            frameworks = ["django", "flask", "fastapi", "tornado", "bottle", "pyramid", "sanic"]
            databases = ["sqlalchemy", "psycopg2", "pymongo", "redis", "pymysql", "cx_oracle"]
            web = ["requests", "aiohttp", "httpx", "urllib3"]
            
            for pkg_type, pkg_list in [
                ("framework", frameworks), 
                ("database", databases), 
                ("web", web)
            ]:
                for pkg in pkg_list:
                    if pkg in packages:
                        important_packages[pkg] = {
                            "version": packages[pkg],
                            "type": pkg_type
                        }
                        
            info["packages"] = important_packages
        except Exception:
            pass
        
        return info
    
    def _prepare_log_data(
        self,
        level: str,
        message: str,
        exception: Optional[Exception] = None,
        context: Optional[Dict[str, Any]] = None,
        tags: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Log verisini hazırlar."""
        # Context birleştirme
        merged_context = self.context.get_context().copy()
        if context:
            merged_context.update(context)
        
        # Etiketleri birleştirme
        merged_tags = self.tags.copy()
        if tags:
            merged_tags.extend(tags)
        
        # Temel log verisi
        log_data = {
            "level": level,
            "message": message,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "context": merged_context,
            "runtime_info": self.runtime_info,
            "environment": self.environment,
            "service_name": self.service_name,
            "tags": merged_tags
        }
        
        # İstisna bilgisi varsa ekle
        if exception:
            log_data["exception"] = {
                "type": exception.__class__.__name__,
                "message": str(exception),
                "traceback": "".join(traceback.format_exception(
                    type(exception), exception, exception.__traceback__
                ))
            }
        
        return log_data
    
    def _send_log(self, log_data: Dict[str, Any]) -> bool:
        """
        Log verisini gönderir. Async_mode'a göre doğrudan veya arka planda gönderim yapar.
        Bağlantı yoksa veya gönderim başarısız olursa önbelleğe alır.
        
        Args:
            log_data: Gönderilecek log verisi
            
        Returns:
            bool: İşlemin başarı durumu
        """
        # Log verisini biçimlendir
        formatted_data = self.formatter.format(log_data)
        
        # Ağ durumu kontrol et
        is_online = self.network_monitor.is_online()
        
        if not is_online and self.cache_handler:
            # Offline durumda ve önbellek varsa doğrudan önbelleğe al
            success = self.cache_handler.cache_log(formatted_data)
            if success:
                self.logger.debug(f"Log cached: {log_data.get('message', '')[:50]}...")
            else:
                self.logger.warning(f"Failed to cache log: {log_data.get('message', '')[:50]}...")
            return success
        
        if self.async_handler:
            # Async modda kuyruğa ekle
            self.async_handler.enqueue(formatted_data)
            return True
        else:
            # Senkron modda doğrudan gönder
            try:
                self.api_handler.send_log(formatted_data)
                self.stats["logs_sent"] += 1
                return True
            except Exception as e:
                self.logger.warning(f"Failed to send log: {str(e)}")
                self.stats["logs_failed"] += 1
                
                # Gönderim başarısız olursa ve önbellek varsa önbelleğe al
                if self.cache_handler:
                    success = self.cache_handler.cache_log(formatted_data)
                    if success:
                        self.logger.debug(f"Log cached after send failure")
                    else:
                        self.logger.warning(f"Failed to cache log after send failure")
                    return success
                return False
    
    # Log seviyesi metodları
    
    def log(
        self,
        level: str,
        message: str,
        exception: Optional[Exception] = None,
        context: Optional[Dict[str, Any]] = None,
        tags: Optional[List[str]] = None
    ) -> bool:
        """
        Belirtilen seviyede bir log kaydı oluşturur.
        
        Args:
            level: Log seviyesi (DEBUG, INFO, WARNING, ERROR, CRITICAL)
            message: Log mesajı
            exception: İlişkili istisna nesnesi (varsa)
            context: Ek bağlam bilgileri
            tags: Log için özel etiketler
            
        Returns:
            bool: İşlemin başarı durumu
        """
        log_data = self._prepare_log_data(level, message, exception, context, tags)
        return self._send_log(log_data)
    
    def debug(
        self,
        message: str,
        exception: Optional[Exception] = None,
        context: Optional[Dict[str, Any]] = None,
        tags: Optional[List[str]] = None
    ) -> bool:
        """DEBUG seviyesinde log kaydı oluşturur."""
        return self.log("DEBUG", message, exception, context, tags)
    
    def info(
        self,
        message: str,
        exception: Optional[Exception] = None,
        context: Optional[Dict[str, Any]] = None,
        tags: Optional[List[str]] = None
    ) -> bool:
        """INFO seviyesinde log kaydı oluşturur."""
        return self.log("INFO", message, exception, context, tags)
    
    def warning(
        self,
        message: str,
        exception: Optional[Exception] = None,
        context: Optional[Dict[str, Any]] = None,
        tags: Optional[List[str]] = None
    ) -> bool:
        """WARNING seviyesinde log kaydı oluşturur."""
        return self.log("WARNING", message, exception, context, tags)
    
    def error(
        self,
        message: str,
        exception: Optional[Exception] = None,
        context: Optional[Dict[str, Any]] = None,
        tags: Optional[List[str]] = None
    ) -> bool:
        """ERROR seviyesinde log kaydı oluşturur."""
        return self.log("ERROR", message, exception, context, tags)
    
    def critical(
        self,
        message: str,
        exception: Optional[Exception] = None,
        context: Optional[Dict[str, Any]] = None,
        tags: Optional[List[str]] = None
    ) -> bool:
        """CRITICAL seviyesinde log kaydı oluşturur."""
        return self.log("CRITICAL", message, exception, context, tags)
    
    def exception(
        self,
        message: str,
        exception: Optional[Exception] = None,
        context: Optional[Dict[str, Any]] = None,
        tags: Optional[List[str]] = None
    ) -> bool:
        """
        Mevcut istisnayı yakalar ve ERROR seviyesinde log kaydı oluşturur.
        exception parametresi belirtilmezse, en son yakalanan istisna kullanılır.
        """
        if exception is None:
            exception = sys.exc_info()[1]
            if exception is None:
                raise ValueError("No exception is being handled")
                
        return self.error(message, exception, context, tags)
    
    def context(self, **kwargs) -> Context:
        """
        Geçici bağlam eklemek için bir context manager döndürür.
        
        Örnek kullanım:
            with loggier.context(user_id=123, action="login"):
                loggier.info("User logged in")
        """
        return self.context.push(kwargs)
    
    def flush(self, timeout: Optional[float] = None) -> bool:
        """
        Bekleyen tüm logları hemen gönderir.
        
        Args:
            timeout: Maksimum bekleme süresi (saniye). None ise tüm loglar gönderilene kadar bekler.
            
        Returns:
            bool: Tüm loglar başarıyla gönderildiyse True, değilse False
        """
        if self.async_handler:
            return self.async_handler.flush(timeout)
        return True
    

    # Mevcut get_stats metoduna yapılacak ekleme
    def get_stats(self) -> Dict[str, Any]:
        """
        Loggier istatistiklerini döndürür.
        
        Returns:
            Dict[str, Any]: İstatistik bilgileri
        """
        stats = self.stats.copy()
        
        # Async handler istatistiklerini ekle
        if self.async_handler:
            async_stats = self.async_handler.get_stats()
            stats.update({
                "async_queue_size": async_stats.get("queue_size", 0),
                "async_processed": async_stats.get("processed", 0),
                "async_failed": async_stats.get("failed", 0),
                "async_last_flush": async_stats.get("last_flush", None)
            })
        
        # Önbellek istatistiklerini ekle
        if self.cache_handler:
            cache_stats = self.cache_handler.get_stats()
            stats.update({
                "cache_pending": cache_stats.get("pending_logs", 0),
                "cache_stored": cache_stats.get("stored_logs", 0),
                "cache_synced": cache_stats.get("synced_logs", 0),
                "cache_size": cache_stats.get("cache_size", "0MB"),
                "cache_last_sync": cache_stats.get("last_sync_time", None)
            })
        
        # Ağ durumu bilgisini ekle
        stats["is_online"] = self.network_monitor.is_online()
        stats["network_last_check"] = self.network_monitor.last_check_time
        
        # Performans izleme istatistiklerini ekle
        if self.performance_monitor:
            perf_stats = self.performance_monitor.get_stats()
            stats.update({
                "performance_monitored_calls": perf_stats.get("total_monitored_calls", 0),
                "performance_slow_calls": perf_stats.get("slow_calls", 0),
                "performance_error_calls": perf_stats.get("error_calls", 0)
            })
        
        return stats
  
    def shutdown(self, timeout: Optional[float] = None) -> None:
        """
        Loggier'ı güvenli bir şekilde kapatır ve bekleyen tüm logları göndermeye çalışır.
        
        Args:
            timeout: Maksimum bekleme süresi (saniye). None ise tüm işlemler tamamlanana kadar bekler.
        """
        self.logger.info("Shutting down Loggier")
        
        # Async handler'ı kapat
        if self.async_handler:
            self.async_handler.shutdown(timeout)
        
        # Önbellek handler'ı kapat
        if self.cache_handler:
            self.cache_handler.shutdown()
        
        # Ağ monitörünü kapat
        self.network_monitor.stop()
        
        self.logger.info("Loggier shutdown complete")
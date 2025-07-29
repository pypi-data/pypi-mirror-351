# handlers/async_handler.py

import logging
import queue
import threading
import time
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
import json

class AsyncLogHandler:
    """
    Log verilerini arka planda asenkron olarak gönderen handler.
    """
    
    def __init__(
        self,
        api_handler,
        max_batch_size: int = 20,
        flush_interval: int = 5,
        max_queue_size: int = 10000,
        log_level: int = logging.INFO,
        cache_handler = None  # CacheHandler eklendi
    ):
        """
        AsyncLogHandler sınıfını yapılandırır.
        
        Args:
            api_handler: Log gönderimi için kullanılacak API handler
            max_batch_size: Bir seferde gönderilecek maksimum log sayısı
            flush_interval: Otomatik gönderim aralığı (saniye)
            max_queue_size: Maksimum kuyruk boyutu
            log_level: Logging seviyesi
            cache_handler: Bağlantı sorunlarında kullanılacak cache handler (opsiyonel)
        """
        self.logger = logging.getLogger("loggier.async")
        self.logger.setLevel(log_level)
        
        self.api_handler = api_handler
        self.max_batch_size = max_batch_size
        self.flush_interval = flush_interval
        self.cache_handler = cache_handler
        
        # Kuyruk ve durum bilgisi
        self.queue = queue.Queue(maxsize=max_queue_size)
        self.flush_lock = threading.RLock()
        self.stats = {
            "processed": 0,
            "failed": 0,
            "last_flush": None
        }
        
        # Worker thread'i başlat
        self._start_worker()
    
    def _start_worker(self):
        """Worker thread'i başlatır."""
        self.stop_thread = False
        self.worker_thread = threading.Thread(
            target=self._worker,
            name="LoggierAsyncWorker",
            daemon=True
        )
        self.worker_thread.start()
        self.logger.debug("Async worker thread started")
    
    def _worker(self):
        """Arka planda çalışan ve periyodik olarak kuyruktan logları işleyen thread."""
        while not self.stop_thread:
            try:
                # Kuyrukta log varsa veya flush_interval süresi geçtiyse işle
                if not self.queue.empty():
                    self._process_queue()
                
                # Bir sonraki işleme için bekle
                time.sleep(self.flush_interval)
            except Exception as e:
                self.logger.error(f"Error in async worker: {str(e)}")
    
    def _process_queue(self):
        """Kuyrukta bekleyen logları işler ve gönderir."""
        with self.flush_lock:
            batch = []
            batch_size = 0
            
            # Kuyruktan max_batch_size kadar log al
            while len(batch) < self.max_batch_size and not self.queue.empty():
                try:
                    log_data = self.queue.get_nowait()
                    batch.append(log_data)
                    batch_size += 1
                    self.queue.task_done()
                except queue.Empty:
                    break
            
            if not batch:
                return
            
            # Batch'i gönder
            self.logger.debug(f"Sending batch of {len(batch)} logs")
            success, failed = self._send_logs(batch)
            
            # İstatistikleri güncelle
            self.stats["processed"] += success
            self.stats["failed"] += failed
            self.stats["last_flush"] = datetime.now().isoformat()
    
    def _send_logs(self, logs: List[Dict[str, Any]]) -> Tuple[int, int]:
        """
        Log batch'ini API'ye gönderir.
        
        Args:
            logs: Gönderilecek log verisi listesi
            
        Returns:
            Tuple[int, int]: (Başarılı gönderim sayısı, Başarısız gönderim sayısı)
        """
        # Tek log ise doğrudan gönder
        if len(logs) == 1:
            try:
                self.api_handler.send_log(logs[0])
                return 1, 0
            except Exception as e:
                self.logger.warning(f"Failed to send log: {str(e)}")
                
                # Bağlantı hatası ve cache_handler varsa önbelleğe al
                if self.cache_handler:
                    self.cache_handler.cache_log(logs[0])
                
                return 0, 1
        
        # Multiple logs - batch send
        try:
            self.api_handler.send_logs_batch(logs)
            return len(logs), 0
        except Exception as e:
            self.logger.warning(f"Failed to send log batch: {str(e)}")
            
            # Bağlantı hatası ve cache_handler varsa her logu ayrı ayrı önbelleğe al
            if self.cache_handler:
                success_count = 0
                for log in logs:
                    if self.cache_handler.cache_log(log):
                        success_count += 1
                
                self.logger.debug(f"Cached {success_count}/{len(logs)} logs after batch send failure")
                
                # Önbelleğe alınan logları başarılı sayalım, tamamı kaybedilmedi
                return success_count, len(logs) - success_count
            
            return 0, len(logs)
    
    def enqueue(self, log_data: Dict[str, Any]) -> bool:
        """
        Log verisini kuyruğa ekler.
        
        Args:
            log_data: Kuyruğa eklenecek log verisi
            
        Returns:
            bool: Başarılı ise True, değilse False
        """
        try:
            self.queue.put_nowait(log_data)
            return True
        except queue.Full:
            self.logger.warning("Async queue is full, logging directly")
            
            # Kuyruk doluysa doğrudan göndermeyi dene
            try:
                self.api_handler.send_log(log_data)
                return True
            except Exception as e:
                self.logger.warning(f"Failed to send log directly: {str(e)}")
                
                # Bağlantı hatası ve cache_handler varsa önbelleğe al
                if self.cache_handler:
                    return self.cache_handler.cache_log(log_data)
                
                return False
    
    def flush(self, timeout: Optional[float] = None) -> bool:
        """
        Kuyruktaki tüm logları işleyip gönderir.
        
        Args:
            timeout: Maksimum bekleme süresi (saniye). None ise sonsuza kadar bekler.
            
        Returns:
            bool: Tüm loglar başarıyla gönderildiyse True, değilse False
        """
        with self.flush_lock:
            start_time = time.time()
            initial_size = self.queue.qsize()
            
            self.logger.debug(f"Flushing {initial_size} logs from queue")
            
            # Kuyrukta log varsa işle
            while not self.queue.empty():
                # Timeout kontrolü
                if timeout is not None and time.time() - start_time > timeout:
                    remaining = self.queue.qsize()
                    self.logger.warning(f"Flush timeout after {timeout}s, {remaining} logs remaining")
                    return False
                
                # Batch oluşturup gönder
                self._process_queue()
            
            # Cache handler varsa, oradaki logları da senkronize et
            if self.cache_handler:
                self.logger.debug("Flushing logs from cache")
                
                # Timeout hesaplama
                remaining_timeout = None
                if timeout is not None:
                    elapsed = time.time() - start_time
                    remaining_timeout = max(0, timeout - elapsed)
                
                # Cache başarısı veya başarısızlığı burada döndürülemez,
                # çünkü bu fonksiyon sadece kuyruk boşalmasını bekliyor
                self.cache_handler.sync_logs()
            
            return True
    
    def shutdown(self, timeout: Optional[float] = None) -> None:
        """
        Handler'ı güvenli bir şekilde kapatır ve bekleyen logları göndermeye çalışır.
        
        Args:
            timeout: Maksimum bekleme süresi (saniye). None ise sonsuza kadar bekler.
        """
        self.logger.info("Shutting down async handler")
        
        # Önce kuyruktaki tüm logları göndermeyi dene
        self.flush(timeout)
        
        # Worker thread'i durdur
        self.stop_thread = True
        
        # Thread'in durmasını bekle
        if self.worker_thread.is_alive():
            self.worker_thread.join(timeout=2.0 if timeout is None else min(2.0, timeout))
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Handler istatistiklerini döndürür.
        
        Returns:
            Dict[str, Any]: İstatistik bilgileri
        """
        stats = self.stats.copy()
        stats["queue_size"] = self.queue.qsize()
        return stats
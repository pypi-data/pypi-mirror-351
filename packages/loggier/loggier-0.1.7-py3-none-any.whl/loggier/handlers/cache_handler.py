# handlers/cache_handler.py

import json
import os
import time
import uuid
import logging
import threading
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Union, Tuple

class CacheHandler:
    """
    Bağlantı sorunlarında log verilerini yerel olarak önbelleğe alan ve 
    bağlantı yeniden kurulduğunda senkronize eden handler.
    """
    
    def __init__(
        self,
        cache_dir: Optional[str] = None,
        max_cache_size_mb: int = 100,
        max_cache_age_days: int = 7,
        use_sqlite: bool = True, 
        sync_interval_seconds: int = 60,
        log_level: int = logging.INFO
    ):
        """
        Yerel önbellek handler'ını yapılandırır.
        
        Args:
            cache_dir: Önbellek dosyalarının saklanacağı dizin. None ise varsayılan konum kullanılır.
            max_cache_size_mb: Maksimum önbellek boyutu (MB)
            max_cache_age_days: Önbellekte saklanacak log kayıtlarının maksimum yaşı (gün)
            use_sqlite: SQLite veritabanı kullanmak için True, JSON dosyaları için False
            sync_interval_seconds: Otomatik senkronizasyon aralığı (saniye)
            log_level: Handler için log seviyesi
        """
        self.logger = logging.getLogger("loggier.cache")
        self.logger.setLevel(log_level)
        
        # Önbellek yapılandırması
        self.cache_dir = self._init_cache_dir(cache_dir)
        self.max_cache_size_bytes = max_cache_size_mb * 1024 * 1024
        self.max_cache_age_seconds = max_cache_age_days * 24 * 60 * 60
        self.use_sqlite = use_sqlite
        self.sync_interval = sync_interval_seconds
        
        # Durum değişkenleri
        self.is_online = True
        self.sync_lock = threading.RLock()
        self.stats = {
            "cached_logs": 0,
            "synced_logs": 0,
            "failed_logs": 0,
            "last_sync_time": None,
            "current_cache_size_bytes": 0
        }
        
        # SQLite veritabanı veya JSON dosya depolama için hazırlık
        if self.use_sqlite:
            self._init_sqlite_db()
        
        # Önbellek temizleme ve kontrol thread'i başlatma
        self._start_maintenance_thread()
        
    def _init_cache_dir(self, cache_dir: Optional[str]) -> Path:
        """Önbellek dizinini hazırlar ve döndürür."""
        if cache_dir is None:
            # Varsayılan olarak kullanıcı dizininde .loggier/cache klasörü oluştur
            cache_path = Path.home() / ".loggier" / "cache"
        else:
            cache_path = Path(cache_dir)
            
        # Dizini oluştur (yoksa)
        cache_path.mkdir(parents=True, exist_ok=True)
        
        self.logger.info(f"Cache directory initialized at: {cache_path}")
        return cache_path
    
    def _init_sqlite_db(self):
        """SQLite veritabanını başlatır ve gerekli tabloları oluşturur."""
        db_path = self.cache_dir / "loggier_cache.db"
        self.db_path = db_path
        
        try:
            conn = sqlite3.connect(str(db_path))
            cursor = conn.cursor()
            
            # Tablo oluştur
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS log_cache (
                id TEXT PRIMARY KEY,
                timestamp REAL,
                log_level TEXT,
                retry_count INTEGER DEFAULT 0,
                log_data TEXT,
                size_bytes INTEGER,
                synced INTEGER DEFAULT 0
            )
            ''')
            
            # İndeks oluştur
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_timestamp ON log_cache (timestamp)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_synced ON log_cache (synced)')
            
            conn.commit()
            conn.close()
            
            self.logger.info(f"SQLite cache database initialized at: {db_path}")
        except Exception as e:
            self.logger.error(f"Failed to initialize SQLite cache database: {str(e)}")
            # SQLite başarısız olursa JSON kullan
            self.use_sqlite = False
    
    def _start_maintenance_thread(self):
        """Periyodik bakım ve senkronizasyon için arka plan thread'i başlatır."""
        self.stop_thread = False
        self.maintenance_thread = threading.Thread(
            target=self._maintenance_worker,
            name="LoggierCacheMaintenance",
            daemon=True
        )
        self.maintenance_thread.start()
        self.logger.info("Cache maintenance thread started")
    
    def _maintenance_worker(self):
        """Önbellek bakımı ve senkronizasyon için arka plan worker."""
        while not self.stop_thread:
            try:
                # Eski önbellek kayıtlarını temizle
                self._cleanup_old_cache()
                
                # Önbellek boyutunu kontrol et ve gerekirse azalt
                self._enforce_cache_size_limit()
                
                # Online ise senkronize et
                if self.is_online:
                    self.sync_logs()
                
            except Exception as e:
                self.logger.error(f"Error in cache maintenance: {str(e)}")
            
            # Bir sonraki çalışma için bekle
            time.sleep(self.sync_interval)
    
    def _cleanup_old_cache(self):
        """Belirlenen yaş sınırından daha eski önbellek kayıtlarını temizler."""
        current_time = time.time()
        cutoff_time = current_time - self.max_cache_age_seconds
        
        if self.use_sqlite:
            try:
                conn = sqlite3.connect(str(self.db_path))
                cursor = conn.cursor()
                
                # Senkronize edilmiş eski kayıtları say ve boyutunu al
                cursor.execute('SELECT COUNT(*), SUM(size_bytes) FROM log_cache WHERE timestamp < ? AND synced = 1', 
                               (cutoff_time,))
                count, size = cursor.fetchone()
                size = size or 0  # None olabilir
                
                # Senkronize edilmiş eski kayıtları sil
                cursor.execute('DELETE FROM log_cache WHERE timestamp < ? AND synced = 1', 
                               (cutoff_time,))
                
                conn.commit()
                conn.close()
                
                if count and count > 0:
                    self.logger.info(f"Cleaned up {count} old synced log entries ({size/1024:.2f} KB)")
                    with self.sync_lock:
                        self.stats["current_cache_size_bytes"] -= size
            except Exception as e:
                self.logger.error(f"Failed to clean up old cache records: {str(e)}")
        else:
            # JSON dosya temelli temizlik
            try:
                deleted_size = 0
                deleted_count = 0
                
                for cache_file in self.cache_dir.glob("*.synced.json"):
                    file_time = cache_file.stat().st_mtime
                    if file_time < cutoff_time:
                        file_size = cache_file.stat().st_size
                        cache_file.unlink()
                        deleted_size += file_size
                        deleted_count += 1
                
                if deleted_count > 0:
                    self.logger.info(f"Cleaned up {deleted_count} old synced log files ({deleted_size/1024:.2f} KB)")
                    with self.sync_lock:
                        self.stats["current_cache_size_bytes"] -= deleted_size
            except Exception as e:
                self.logger.error(f"Failed to clean up old cache files: {str(e)}")
                
    def _enforce_cache_size_limit(self):
        """Önbellek boyutunu kontrol eder ve maksimum boyutu aşmışsa en eski kayıtları siler."""
        if self.stats["current_cache_size_bytes"] <= self.max_cache_size_bytes:
            return  # Boyut limiti aşılmamış
        
        # Ne kadar yer açılması gerektiğini hesapla
        bytes_to_free = self.stats["current_cache_size_bytes"] - (self.max_cache_size_bytes * 0.8)  # %80'e düşür
        
        if self.use_sqlite:
            try:
                conn = sqlite3.connect(str(self.db_path))
                cursor = conn.cursor()
                
                # En eski kayıtlardan başlayarak senkronize edilmiş kayıtları sil
                cursor.execute('''
                SELECT id, size_bytes FROM log_cache 
                WHERE synced = 1 
                ORDER BY timestamp ASC
                ''')
                
                records = cursor.fetchall()
                deleted_size = 0
                deleted_ids = []
                
                for record_id, size in records:
                    deleted_ids.append(record_id)
                    deleted_size += size
                    if deleted_size >= bytes_to_free:
                        break
                
                if deleted_ids:
                    # DELETE FROM ile liste kullanma
                    placeholders = ",".join("?" for _ in deleted_ids)
                    cursor.execute(f"DELETE FROM log_cache WHERE id IN ({placeholders})", deleted_ids)
                    
                    conn.commit()
                    conn.close()
                    
                    self.logger.info(f"Cleaned up {len(deleted_ids)} log entries to reduce cache size ({deleted_size/1024/1024:.2f} MB)")
                    with self.sync_lock:
                        self.stats["current_cache_size_bytes"] -= deleted_size
            except Exception as e:
                self.logger.error(f"Failed to enforce cache size limit: {str(e)}")
        else:
            # JSON dosya temelli boyut kontrolü
            try:
                # Synced dosyalarını bulup sıralama
                cache_files = []
                for cache_file in self.cache_dir.glob("*.synced.json"):
                    cache_files.append((cache_file, cache_file.stat().st_mtime, cache_file.stat().st_size))
                
                # En eski dosyalardan başlayarak sil
                cache_files.sort(key=lambda x: x[1])  # mtime'a göre sırala
                
                deleted_size = 0
                deleted_count = 0
                
                for cache_file, _, file_size in cache_files:
                    cache_file.unlink()
                    deleted_size += file_size
                    deleted_count += 1
                    
                    if deleted_size >= bytes_to_free:
                        break
                
                if deleted_count > 0:
                    self.logger.info(f"Cleaned up {deleted_count} log files to reduce cache size ({deleted_size/1024/1024:.2f} MB)")
                    with self.sync_lock:
                        self.stats["current_cache_size_bytes"] -= deleted_size
            except Exception as e:
                self.logger.error(f"Failed to enforce cache size limit: {str(e)}")
    
    def cache_log(self, log_data: Dict[str, Any]) -> bool:
        """
        Log verisini yerel önbelleğe kaydeder.
        
        Args:
            log_data: JSON serileştirilebilir log verisi
            
        Returns:
            bool: Başarılı ise True, değilse False
        """
        log_id = str(uuid.uuid4())
        timestamp = time.time()
        log_level = log_data.get("level", "INFO")
        log_json = json.dumps(log_data)
        size_bytes = len(log_json.encode('utf-8'))
        
        try:
            if self.use_sqlite:
                conn = sqlite3.connect(str(self.db_path))
                cursor = conn.cursor()
                
                cursor.execute('''
                INSERT INTO log_cache (id, timestamp, log_level, log_data, size_bytes, synced)
                VALUES (?, ?, ?, ?, ?, 0)
                ''', (log_id, timestamp, log_level, log_json, size_bytes))
                
                conn.commit()
                conn.close()
            else:
                # JSON dosyasına kaydet
                cache_file = self.cache_dir / f"{log_id}.pending.json"
                with open(cache_file, 'w', encoding='utf-8') as f:
                    json.dump({
                        "id": log_id,
                        "timestamp": timestamp,
                        "log_level": log_level,
                        "retry_count": 0,
                        "log_data": log_data,
                        "size_bytes": size_bytes,
                        "synced": 0
                    }, f)
            
            # İstatistikleri güncelle
            with self.sync_lock:
                self.stats["cached_logs"] += 1
                self.stats["current_cache_size_bytes"] += size_bytes
            
            return True
        
        except Exception as e:
            self.logger.error(f"Failed to cache log: {str(e)}")
            return False
    
    def set_online_status(self, is_online: bool):
        """
        Ağ bağlantı durumunu günceller.
        
        Args:
            is_online: Bağlantı durumu - True: online, False: offline
        """
        was_offline = not self.is_online
        self.is_online = is_online
        
        # Offline'dan online'a geçişte senkronizasyonu başlat
        if was_offline and is_online:
            self.logger.info("Connection restored, starting synchronization")
            self.sync_logs()
    
    def sync_logs(self, max_batch_size: int = 100) -> Tuple[int, int]:
        """
        Önbelleğe alınmış logları senkronize eder.
        
        Args:
            max_batch_size: Bir seferde işlenecek maksimum log sayısı
            
        Returns:
            Tuple[int, int]: (Senkronize edilen log sayısı, Başarısız olan log sayısı)
        """
        if not self.is_online:
            self.logger.debug("Skipping log sync - system is offline")
            return 0, 0
        
        with self.sync_lock:
            self.logger.debug("Starting log synchronization")
            
            sync_count = 0
            fail_count = 0
            
            if self.use_sqlite:
                try:
                    conn = sqlite3.connect(str(self.db_path))
                    cursor = conn.cursor()
                    
                    # Senkronize edilmemiş kayıtları getir (kritiklik sırasına göre)
                    cursor.execute('''
                    SELECT id, log_data, retry_count 
                    FROM log_cache 
                    WHERE synced = 0 
                    ORDER BY 
                        CASE 
                            WHEN log_level = 'CRITICAL' THEN 1
                            WHEN log_level = 'ERROR' THEN 2
                            WHEN log_level = 'WARNING' THEN 3
                            WHEN log_level = 'INFO' THEN 4
                            ELSE 5
                        END,
                        timestamp ASC
                    LIMIT ?
                    ''', (max_batch_size,))
                    
                    records = cursor.fetchall()
                    
                    for record_id, log_data_str, retry_count in records:
                        log_data = json.loads(log_data_str)
                        success = self._send_log_to_server(log_data)
                        
                        if success:
                            # Başarıyla senkronize edildi olarak işaretle
                            cursor.execute('UPDATE log_cache SET synced = 1 WHERE id = ?', (record_id,))
                            sync_count += 1
                        else:
                            # Retry count'u artır
                            cursor.execute('UPDATE log_cache SET retry_count = ? WHERE id = ?', 
                                          (retry_count + 1, record_id))
                            fail_count += 1
                            
                            # Çok fazla başarısız deneme olduysa, bağlantı durumunu kontrol et
                            if retry_count >= 5:
                                self.logger.warning(f"Log sync failed 5+ times for id={record_id}, may be offline")
                                break
                    
                    conn.commit()
                    conn.close()
                except Exception as e:
                    self.logger.error(f"Failed to sync logs from SQLite: {str(e)}")
                    fail_count += len(records) if 'records' in locals() else 0
            else:
                # JSON dosya temelli senkronizasyon
                try:
                    processed = 0
                    
                    # Önce dosyaları kritiklik sırasına göre sıralama için hepsini topla
                    priority_order = {"CRITICAL": 1, "ERROR": 2, "WARNING": 3, "INFO": 4, "DEBUG": 5}
                    pending_files = []
                    
                    for cache_file in self.cache_dir.glob("*.pending.json"):
                        try:
                            with open(cache_file, 'r', encoding='utf-8') as f:
                                cache_data = json.load(f)
                                log_level = cache_data.get("log_level", "INFO")
                                priority = priority_order.get(log_level, 99)
                                timestamp = cache_data.get("timestamp", 0)
                                pending_files.append((cache_file, priority, timestamp, cache_data))
                        except Exception:
                            continue
                    
                    # Kritiklik ve zaman sırasına göre sırala
                    pending_files.sort(key=lambda x: (x[1], x[2]))
                    
                    for cache_file, _, _, cache_data in pending_files:
                        if processed >= max_batch_size:
                            break
                            
                        retry_count = cache_data.get("retry_count", 0)
                        log_data = cache_data.get("log_data", {})
                        
                        success = self._send_log_to_server(log_data)
                        
                        if success:
                            # Dosya adını değiştirerek senkronize edildi olarak işaretle
                            synced_file = cache_file.with_name(cache_file.name.replace(".pending.", ".synced."))
                            cache_file.rename(synced_file)
                            sync_count += 1
                        else:
                            # Retry count'u artır
                            cache_data["retry_count"] = retry_count + 1
                            with open(cache_file, 'w', encoding='utf-8') as f:
                                json.dump(cache_data, f)
                            fail_count += 1
                            
                            # Çok fazla başarısız deneme olduysa, bağlantı durumunu kontrol et
                            if retry_count >= 5:
                                self.logger.warning(f"Log sync failed 5+ times for file={cache_file.name}, may be offline")
                                break
                        
                        processed += 1
                except Exception as e:
                    self.logger.error(f"Failed to sync logs from JSON files: {str(e)}")
            
            # İstatistikleri güncelle
            self.stats["synced_logs"] += sync_count
            self.stats["failed_logs"] += fail_count
            if sync_count > 0 or fail_count > 0:
                self.stats["last_sync_time"] = datetime.now().isoformat()
                self.logger.info(f"Log sync completed: {sync_count} synced, {fail_count} failed")
            
            return sync_count, fail_count
    
    def _send_log_to_server(self, log_data: Dict[str, Any]) -> bool:
        """
        Log verisini sunucuya göndermeyi dener.
        
        NOT: Bu fonksiyon uygulamadaki APIHandler'ın bir örneğine erişim gerektirir.
        Gerçekte burayı APIHandler'a erişerek gerçekleştirmelisiniz.
        
        Args:
            log_data: Sunucuya gönderilecek log verisi
            
        Returns:
            bool: Başarılı ise True, değilse False
        """
        # TODO: Gerçek APIHandler'a bağla
        # Bu kısım, Loggier sınıfı tarafından cache_handler'a aktarılan api_handler
        # örneği üzerinden gerçekleştirilmeli.
        
        # Şimdilik sadece simülasyon yapıyoruz:
        self.logger.debug(f"Simulating sending log to server: {log_data.get('message', '')[:30]}...")
        return True  # Başarılı olduğunu varsayıyoruz
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Önbellek istatistiklerini döndürür.
        
        Returns:
            Dict[str, Any]: İstatistik bilgileri
        """
        with self.sync_lock:
            stats_copy = self.stats.copy()
            
            # SQLite için bekleyen log sayısını hesapla
            if self.use_sqlite:
                try:
                    conn = sqlite3.connect(str(self.db_path))
                    cursor = conn.cursor()
                    
                    cursor.execute('SELECT COUNT(*) FROM log_cache WHERE synced = 0')
                    pending_count = cursor.fetchone()[0]
                    
                    cursor.execute('SELECT COUNT(*) FROM log_cache WHERE synced = 1')
                    synced_count = cursor.fetchone()[0]
                    
                    conn.close()
                    
                    stats_copy["pending_logs"] = pending_count
                    stats_copy["stored_logs"] = pending_count + synced_count
                except Exception as e:
                    self.logger.error(f"Failed to get cache stats: {str(e)}")
                    stats_copy["pending_logs"] = "unknown"
                    stats_copy["stored_logs"] = "unknown"
            else:
                # JSON dosya sayımı
                try:
                    pending_count = len(list(self.cache_dir.glob("*.pending.json")))
                    synced_count = len(list(self.cache_dir.glob("*.synced.json")))
                    
                    stats_copy["pending_logs"] = pending_count
                    stats_copy["stored_logs"] = pending_count + synced_count
                except Exception as e:
                    self.logger.error(f"Failed to count cache files: {str(e)}")
                    stats_copy["pending_logs"] = "unknown"
                    stats_copy["stored_logs"] = "unknown"
            
            # Boyut bilgisini insan okunabilir formata dönüştür
            current_size_mb = stats_copy["current_cache_size_bytes"] / 1024 / 1024
            max_size_mb = self.max_cache_size_bytes / 1024 / 1024
            stats_copy["cache_size"] = f"{current_size_mb:.2f}MB / {max_size_mb:.0f}MB"
            
            return stats_copy
    
    def shutdown(self):
        """Handler'ı kapatır ve senkronizasyon thread'ini durdurur."""
        self.logger.info("Shutting down cache handler")
        self.stop_thread = True
        
        # Thread'in sonlanmasını bekle
        if hasattr(self, 'maintenance_thread') and self.maintenance_thread.is_alive():
            self.maintenance_thread.join(timeout=2.0)
        
        # Son bir senkronizasyon daha dene
        if self.is_online:
            self.sync_logs()
            
    def clear_cache(self, force: bool = False) -> int:
        """
        Önbelleği temizler. Varsayılan olarak sadece senkronize edilmiş logları siler.
        
        Args:
            force: True ise senkronize edilmemiş logları da siler
            
        Returns:
            int: Silinen log sayısı
        """
        deleted_count = 0
        
        with self.sync_lock:
            if self.use_sqlite:
                try:
                    conn = sqlite3.connect(str(self.db_path))
                    cursor = conn.cursor()
                    
                    if force:
                        # Tüm kayıtları sil
                        cursor.execute('SELECT COUNT(*), SUM(size_bytes) FROM log_cache')
                        count, size = cursor.fetchone()
                        size = size or 0  # None olabilir
                        
                        cursor.execute('DELETE FROM log_cache')
                        deleted_count = count
                        
                        self.stats["current_cache_size_bytes"] = 0
                    else:
                        # Sadece senkronize edilmiş kayıtları sil
                        cursor.execute('SELECT COUNT(*), SUM(size_bytes) FROM log_cache WHERE synced = 1')
                        count, size = cursor.fetchone()
                        size = size or 0  # None olabilir
                        
                        cursor.execute('DELETE FROM log_cache WHERE synced = 1')
                        deleted_count = count
                        
                        self.stats["current_cache_size_bytes"] -= size
                    
                    conn.commit()
                    conn.close()
                except Exception as e:
                    self.logger.error(f"Failed to clear cache: {str(e)}")
            else:
                # JSON dosya temelli temizlik
                try:
                    total_size = 0
                    
                    if force:
                        # Tüm dosyaları sil
                        for cache_file in self.cache_dir.glob("*.json"):
                            total_size += cache_file.stat().st_size
                            cache_file.unlink()
                            deleted_count += 1
                        
                        self.stats["current_cache_size_bytes"] = 0
                    else:
                        # Sadece senkronize edilmiş dosyaları sil
                        for cache_file in self.cache_dir.glob("*.synced.json"):
                            total_size += cache_file.stat().st_size
                            cache_file.unlink()
                            deleted_count += 1
                        
                        self.stats["current_cache_size_bytes"] -= total_size
                except Exception as e:
                    self.logger.error(f"Failed to clear cache files: {str(e)}")
            
            self.logger.info(f"Cleared {deleted_count} log entries from cache")
            return deleted_count
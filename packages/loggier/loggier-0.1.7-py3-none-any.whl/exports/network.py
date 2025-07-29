# utils/network.py

import logging
import socket
import threading
import time
from typing import List, Callable, Optional, Any
from datetime import datetime

class NetworkMonitor:
    """
    İnternet bağlantısını periyodik olarak kontrol eden ve durum değişikliklerinde
    callback fonksiyonlarını tetikleyen sınıf.
    """
    
    def __init__(
        self,
        check_interval: int = 60,
        api_handler: Optional[Any] = None,
        initial_status: bool = True,
        test_hosts: Optional[List[str]] = None,
        log_level: int = logging.INFO
    ):
        """
        NetworkMonitor sınıfını başlatır.
        
        Args:
            check_interval: Bağlantı kontrol aralığı (saniye)
            api_handler: API bağlantı testleri için kullanılacak APIHandler örneği
            initial_status: Başlangıç bağlantı durumu
            test_hosts: İnternet erişimini test etmek için kullanılacak host listesi
            log_level: Logging seviyesi
        """
        self.logger = logging.getLogger("loggier.network")
        self.logger.setLevel(log_level)
        
        self.check_interval = check_interval
        self.api_handler = api_handler
        self.is_running = False
        self.status_callbacks = []
        self._online = initial_status
        self.last_check_time = datetime.now().isoformat()
        
        # Test edilecek adresler
        self.test_hosts = test_hosts or [
            "8.8.8.8",  # Google DNS
            "1.1.1.1",  # Cloudflare DNS
            "208.67.222.222"  # OpenDNS
        ]
        
        # İzleme thread'ini başlat
        self._start_monitoring()
    
    def _start_monitoring(self):
        """Ağ izleme thread'ini başlatır."""
        if self.is_running:
            return
            
        self.is_running = True
        self.stop_thread = False
        
        self.monitor_thread = threading.Thread(
            target=self._monitor_worker,
            name="LoggierNetworkMonitor",
            daemon=True
        )
        self.monitor_thread.start()
        self.logger.debug("Network monitoring thread started")
    
    def _monitor_worker(self):
        """Periyodik ağ durumu kontrolleri için çalışan thread."""
        while not self.stop_thread:
            try:
                # Ağ durumunu kontrol et
                current_status = self._check_connectivity()
                self.last_check_time = datetime.now().isoformat()
                
                # Durum değişti mi?
                if current_status != self._online:
                    self.logger.info(f"Network status changed: {'Online' if current_status else 'Offline'}")
                    self._online = current_status
                    
                    # Callback'leri tetikle
                    self._notify_status_change(current_status)
            except Exception as e:
                self.logger.error(f"Error in network monitor: {str(e)}")
            
            # Bir sonraki kontrol için bekle
            time.sleep(self.check_interval)
    
    def _check_connectivity(self) -> bool:
        """
        İnternet bağlantısını kontrol eder.
        
        Returns:
            bool: Bağlantı varsa True, yoksa False
        """
        # Önce API handler ile kontrol et (eğer belirtilmişse)
        if self.api_handler:
            try:
                health_check = self.api_handler.check_connectivity()
                if health_check:
                    return True
            except Exception:
                # API kontrol hatası, diğer metodları dene
                pass
        
        # Socket testi - DNS sunucularına bağlantı dene
        for host in self.test_hosts:
            try:
                # 53 = DNS portu, TCP bağlantı kurabilirse internet vardır
                socket.create_connection((host, 53), timeout=3.0)
                return True
            except OSError:
                continue
        
        # HTTP isteği ile kontrol et
        try:
            import urllib.request
            urllib.request.urlopen('http://www.google.com', timeout=3)
            return True
        except Exception:
            pass
        
        # Tüm kontroller başarısız olduysa offline kabul et
        return False
    
    def add_status_callback(self, callback: Callable[[bool], None]) -> None:
        """
        Ağ durum değişikliğini izlemek için callback fonksiyonu ekler.
        
        Args:
            callback: Durum değiştiğinde çağrılacak fonksiyon.
                     Fonksiyon bir bool parametresi alır (True=Online, False=Offline)
        """
        if callback not in self.status_callbacks:
            self.status_callbacks.append(callback)
    
    def remove_status_callback(self, callback: Callable[[bool], None]) -> None:
        """Durum değişikliği callback'ini kaldırır."""
        if callback in self.status_callbacks:
            self.status_callbacks.remove(callback)
    
    def _notify_status_change(self, status: bool) -> None:
        """Tüm kayıtlı callback'lere durum değişikliğini bildirir."""
        for callback in self.status_callbacks:
            try:
                callback(status)
            except Exception as e:
                self.logger.error(f"Error in network status callback: {str(e)}")
    
    def is_online(self) -> bool:
        """
        Mevcut ağ durumunu döndürür.
        
        Returns:
            bool: Internet bağlantısı varsa True, yoksa False
        """
        return self._online
    
    def check_now(self) -> bool:
        """
        Ağ durumunu hemen kontrol eder ve sonucu döndürür.
        
        Returns:
            bool: Internet bağlantısı varsa True, yoksa False
        """
        try:
            current_status = self._check_connectivity()
            self.last_check_time = datetime.now().isoformat()
            
            # Durum değiştiyse callback'leri tetikle
            if current_status != self._online:
                self.logger.info(f"Network status changed: {'Online' if current_status else 'Offline'}")
                self._online = current_status
                self._notify_status_change(current_status)
            
            return current_status
        except Exception as e:
            self.logger.error(f"Error checking network connectivity: {str(e)}")
            return self._online  # Hata durumunda mevcut durumu koruyoruz
    
    def stop(self) -> None:
        """İzleme thread'ini durdurur."""
        self.logger.debug("Stopping network monitor")
        self.stop_thread = True
        
        # Thread'in sonlanmasını bekle
        if hasattr(self, 'monitor_thread') and self.monitor_thread.is_alive():
            self.monitor_thread.join(timeout=2.0)
            
        self.is_running = False
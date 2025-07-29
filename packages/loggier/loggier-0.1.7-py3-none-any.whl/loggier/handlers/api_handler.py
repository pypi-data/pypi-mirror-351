# handlers/api_handler.py

import json
import logging
import time
from typing import Dict, List, Any, Optional, Union, Tuple
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

class APIHandler:
    """
    API ile iletişim kuran ve log verilerini gönderen handler.
    """
    
    def __init__(
        self,
        api_key: str,
        api_url: str = "https://api.loggier.app/api",
        project_name: Optional[str] = None,
        max_retries: int = 3,
        timeout: int = 5,
        log_level: int = logging.INFO
    ):
        """
        APIHandler sınıfını yapılandırır.
        
        Args:
            api_key: Loggier API anahtarı
            api_url: API temel URL'i
            project_name: Proje adı (opsiyonel)
            max_retries: Başarısız istekler için yeniden deneme sayısı
            timeout: HTTP istekleri için zaman aşımı (saniye)
            log_level: Logging seviyesi
        """
        self.logger = logging.getLogger("loggier.api")
        self.logger.setLevel(log_level)
        
        self.api_key = api_key
        self.api_url = api_url.rstrip('/')
        self.project_name = project_name
        self.timeout = timeout
        
        # HTTP session oluşturma ve retry stratejisi tanımlama
        self.session = requests.Session()
        
        # Retry stratejisi tanımlama
        retry_strategy = Retry(
            total=max_retries,
            backoff_factor=0.5,  # 0.5, 1, 2, 4... şeklinde bekleyerek yeniden dener
            status_forcelist=[408, 429, 500, 502, 503, 504],  # Bu HTTP kodlarında yeniden dene
            allowed_methods=["GET", "POST"]  # Sadece GET ve POST isteklerini yeniden dene
        )
        
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
        
        # API URL'lerini oluşturma
        self.ingest_url = f"{self.api_url}/api/ingest/{self.api_key}"
        self.batch_url = f"{self.api_url}/api/ingest/{self.api_key}/batch"
        self.health_url = f"{self.api_url}/health"
        
        # İstatistikler
        self.stats = {
            "logs_sent": 0,
            "logs_failed": 0,
            "last_response_time": None,
            "avg_response_time": 0,
            "total_request_time": 0
        }
        
        self.logger.debug(f"API Handler initialized for URL: {api_url}")
    
    def send_log(self, log_data: Dict[str, Any]) -> bool:
        """
        Tek bir log kaydını API'ye gönderir.
        
        Args:
            log_data: Gönderilecek log verisi
            
        Returns:
            bool: Başarılı ise True, değilse False
        
        Raises:
            requests.RequestException: API isteği başarısız olursa
        """
        start_time = time.time()
        
        try:
            headers = {
                "Content-Type": "application/json",
                "X-Loggier-Key": self.api_key
            }
            self.logger.info(log_data)
            response = self.session.post(
                self.ingest_url,
                json=log_data,
                headers=headers,
                timeout=self.timeout
            )
            
            response_time = time.time() - start_time
            
            # İstatistikleri güncelle
            self._update_stats(True, response_time)
            
            # Yanıtı kontrol et
            response.raise_for_status()
            
            return True
            
        except requests.RequestException as e:
            response_time = time.time() - start_time
            self._update_stats(False, response_time)
            
            self.logger.warning(f"Failed to send log: {str(e)}")
            raise
    
    def send_logs_batch(self, logs: List[Dict[str, Any]]) -> bool:
        """
        Birden fazla log kaydını toplu olarak API'ye gönderir.
        
        Args:
            logs: Gönderilecek log verisi listesi
            
        Returns:
            bool: Başarılı ise True, değilse False
        
        Raises:
            requests.RequestException: API isteği başarısız olursa
        """
        if not logs:
            return True
            
        start_time = time.time()
        
        try:
            headers = {
                "Content-Type": "application/json",
                "X-Loggier-Key": self.api_key
            }
            
            response = self.session.post(
                self.batch_url,
                json=logs,
                headers=headers,
                timeout=self.timeout
            )
            
            response_time = time.time() - start_time
            
            # İstatistikleri güncelle
            self._update_stats(True, response_time, len(logs))
            
            # Yanıtı kontrol et
            response.raise_for_status()
            
            return True
            
        except requests.RequestException as e:
            response_time = time.time() - start_time
            self._update_stats(False, response_time, len(logs))
            
            self.logger.warning(f"Failed to send log batch: {str(e)}")
            raise
    
    def check_connectivity(self) -> bool:
        """
        API sunucusuna bağlantıyı kontrol eder.
        
        Returns:
            bool: Bağlantı başarılı ise True, değilse False
        """
        try:
            response = self.session.get(
                self.health_url,
                timeout=self.timeout / 2  # Daha kısa timeout ile hızlı kontrol
            )
            
            return response.status_code == 200
        except requests.RequestException:
            return False
    
    def get_project_details(self) -> Optional[Dict[str, Any]]:
        """
        API anahtarına bağlı projenin detaylarını getirir.
        
        Returns:
            Optional[Dict[str, Any]]: Proje detayları veya None
        """
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}"
            }
            
            response = self.session.get(
                f"{self.api_url}/projects/current",
                headers=headers,
                timeout=self.timeout
            )
            
            response.raise_for_status()
            return response.json()
            
        except requests.RequestException as e:
            self.logger.warning(f"Failed to get project details: {str(e)}")
            return None
    
    def _update_stats(self, success: bool, response_time: float, logs_count: int = 1):
        """İstek sonucuna göre istatistikleri günceller."""
        if success:
            self.stats["logs_sent"] += logs_count
        else:
            self.stats["logs_failed"] += logs_count
            
        self.stats["last_response_time"] = response_time
        
        # Ortalama yanıt süresini güncelle
        total_logs = self.stats["logs_sent"] + self.stats["logs_failed"]
        self.stats["total_request_time"] += response_time
        
        if total_logs > 0:
            self.stats["avg_response_time"] = self.stats["total_request_time"] / total_logs
    
    def get_stats(self) -> Dict[str, Any]:
        """
        API Handler istatistiklerini döndürür.
        
        Returns:
            Dict[str, Any]: İstatistik bilgileri
        """
        return self.stats.copy()
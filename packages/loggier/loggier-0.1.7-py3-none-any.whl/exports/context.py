import uuid
import threading
from typing import Any, Dict, Optional

class Context:
    """
    Log bağlam bilgilerini yönetmek için sınıf
    Thread-safe bağlam yönetimi sağlar
    """
    
    def __init__(self, initial_context: Optional[Dict[str, Any]] = None):
        """
        Context yöneticisini başlat
        
        Args:
            initial_context (Dict[str, Any], optional): Başlangıç bağlam değerleri
        """
        self._data = initial_context or {}
        self._thread_data = threading.local()
        self._thread_data.context_stack = []
    
    def push(self, **kwargs) -> str:
        """
        Bağlam yığınına yeni değerler ekle
        
        Args:
            **kwargs: Eklenecek anahtar-değer çiftleri
        
        Returns:
            str: İşlem token'ı (pop için kullanılır)
        """
        if not hasattr(self._thread_data, "context_stack"):
            self._thread_data.context_stack = []
        
        token = str(uuid.uuid4())
        self._thread_data.context_stack.append((token, kwargs))
        return token
    
    def pop(self, token: str) -> None:
        """
        Belirtilen token ile eklenmiş bağlam değerlerini kaldır
        
        Args:
            token (str): push() ile döndürülen token
        """
        if not hasattr(self._thread_data, "context_stack"):
            return
        
        # Token'ı bul ve kaldır
        new_stack = []
        for t, ctx in self._thread_data.context_stack:
            if t != token:
                new_stack.append((t, ctx))
        
        self._thread_data.context_stack = new_stack
    
    def get_context(self) -> Dict[str, Any]:
        """
        Mevcut bağlam değerlerini al (global ve thread-local)
        
        Returns:
            Dict[str, Any]: Birleştirilmiş bağlam verileri
        """
        # Global bağlam ile başla
        result = self._data.copy()
        
        # Thread-local bağlam verilerini ekle
        if hasattr(self._thread_data, "context_stack"):
            for _, ctx in self._thread_data.context_stack:
                result.update(ctx)
        
        return result
    
    def clear(self) -> None:
        """Tüm thread-local bağlam verilerini temizle"""
        if hasattr(self._thread_data, "context_stack"):
            self._thread_data.context_stack = []
    
    def set_global(self, key: str, value: Any) -> None:
        """
        Global bağlam değeri ayarla
        
        Args:
            key (str): Anahtar
            value (Any): Değer
        """
        self._data[key] = value
    
    def update_global(self, data=None, **kwargs) -> None:
        """
        Global bağlam değerlerini güncelle
        
        Args:
            data (Dict[str, Any], optional): Dictionary olarak eklenecek bağlam verileri
            **kwargs: Anahtar-değer çiftleri olarak eklenecek bağlam verileri
        """
        if data and isinstance(data, dict):
            self._data.update(data)
            
        self._data.update(kwargs)
    
    def get_global(self, key: str, default: Any = None) -> Any:
        """
        Global bağlam değerini al
        
        Args:
            key (str): Anahtar
            default (Any, optional): Bulunamazsa dönecek değer
        
        Returns:
            Any: Bağlam değeri veya default
        """
        return self._data.get(key, default)
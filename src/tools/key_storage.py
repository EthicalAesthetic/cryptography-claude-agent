"""
Shared key storage for POC
In production, this would be HashiCorp Vault
"""
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


class KeyStorage:
    """
    Singleton key storage for POC.
    In production, this would be replaced with Vault client.
    """
    _instance = None
    _storage: Dict[str, Any] = {}
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(KeyStorage, cls).__new__(cls)
        return cls._instance
    
    def store_key(self, key_id: str, private_key: Any) -> None:
        """Store a private key"""
        self._storage[key_id] = private_key
        logger.debug(f"Stored key: {key_id}")
    
    def get_key(self, key_id: str) -> Optional[Any]:
        """Retrieve a private key"""
        key = self._storage.get(key_id)
        if key:
            logger.debug(f"Retrieved key: {key_id}")
        else:
            logger.warning(f"Key not found: {key_id}")
        return key
    
    def list_keys(self) -> list:
        """List all stored key IDs"""
        return list(self._storage.keys())
    
    def delete_key(self, key_id: str) -> bool:
        """Delete a key"""
        if key_id in self._storage:
            del self._storage[key_id]
            logger.info(f"Deleted key: {key_id}")
            return True
        return False


# Global instance
key_storage = KeyStorage()
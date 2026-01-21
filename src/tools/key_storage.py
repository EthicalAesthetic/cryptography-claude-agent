"""
Shared key storage singleton for POC
In production, this would be HashiCorp Vault
"""
import logging
from typing import Dict, Any, Optional
from threading import Lock

logger = logging.getLogger(__name__)


class KeyStorage:
    """
    Thread-safe singleton key storage for POC.
    In production, replace with Vault client.
    """
    _instance = None
    _lock = Lock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super(KeyStorage, cls).__new__(cls)
                    cls._instance._storage = {}
                    cls._instance._initialized = True
        return cls._instance
    
    def store_key(self, key_id: str, private_key: Any) -> None:
        """Store a private key"""
        self._storage[key_id] = private_key
        logger.info(f"✓ Stored key in shared storage: {key_id}")
        logger.info(f"  Total keys in storage: {len(self._storage)}")
    
    def get_key(self, key_id: str) -> Optional[Any]:
        """Retrieve a private key"""
        key = self._storage.get(key_id)
        if key:
            logger.info(f"✓ Retrieved key from shared storage: {key_id}")
        else:
            logger.error(f"✗ Key NOT found in storage: {key_id}")
            logger.error(f"  Available keys: {list(self._storage.keys())}")
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
    
    def clear(self):
        """Clear all keys (for testing)"""
        count = len(self._storage)
        self._storage.clear()
        logger.info(f"Cleared {count} keys from storage")


# Global singleton instance - THIS IS THE FIX!
key_storage = KeyStorage()

def get_key_storage() -> KeyStorage:
    """Get the global key storage instance"""
    return key_storage
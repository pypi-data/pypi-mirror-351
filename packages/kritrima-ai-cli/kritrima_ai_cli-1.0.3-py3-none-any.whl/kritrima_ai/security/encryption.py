"""
Encryption and secure storage for Kritrima AI CLI.

This module provides secure storage capabilities for sensitive data
such as API keys, session information, and user credentials.
"""

import base64
import getpass
import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import keyring
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

from kritrima_ai.config.app_config import AppConfig
from kritrima_ai.utils.logger import get_logger

logger = get_logger(__name__)


class EncryptionError(Exception):
    """Raised when encryption/decryption operations fail."""


class DataEncryption:
    """
    Provides data encryption and decryption capabilities.

    Uses Fernet (symmetric encryption) with PBKDF2 key derivation
    for secure data protection.
    """

    def __init__(self, password: Optional[str] = None) -> None:
        """
        Initialize data encryption.

        Args:
            password: Password for key derivation (prompted if not provided)
        """
        self._password = password
        self._key: Optional[bytes] = None
        self._fernet: Optional[Fernet] = None

        logger.info("Data encryption initialized")

    def _get_password(self) -> str:
        """Get password for encryption."""
        if self._password:
            return self._password

        # Try to get from environment
        env_password = os.getenv("KRITRIMA_ENCRYPTION_PASSWORD")
        if env_password:
            return env_password

        # Prompt user
        return getpass.getpass("Enter encryption password: ")

    def _derive_key(self, password: str, salt: bytes) -> bytes:
        """Derive encryption key from password."""
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        return base64.urlsafe_b64encode(kdf.derive(password.encode()))

    def _get_fernet(self, salt: Optional[bytes] = None) -> Fernet:
        """Get Fernet instance for encryption/decryption."""
        if self._fernet and salt is None:
            return self._fernet

        password = self._get_password()

        if salt is None:
            salt = os.urandom(16)

        key = self._derive_key(password, salt)
        return Fernet(key)

    def encrypt(self, data: Union[str, bytes]) -> Dict[str, str]:
        """
        Encrypt data.

        Args:
            data: Data to encrypt

        Returns:
            Dictionary with encrypted data and metadata
        """
        try:
            if isinstance(data, str):
                data = data.encode("utf-8")

            # Generate salt
            salt = os.urandom(16)

            # Get Fernet instance
            fernet = self._get_fernet(salt)

            # Encrypt data
            encrypted_data = fernet.encrypt(data)

            return {
                "encrypted_data": base64.b64encode(encrypted_data).decode("utf-8"),
                "salt": base64.b64encode(salt).decode("utf-8"),
                "algorithm": "fernet",
                "version": "1.0",
            }

        except Exception as e:
            logger.error(f"Encryption failed: {e}")
            raise EncryptionError(f"Encryption failed: {e}")

    def decrypt(self, encrypted_package: Dict[str, str]) -> bytes:
        """
        Decrypt data.

        Args:
            encrypted_package: Dictionary with encrypted data and metadata

        Returns:
            Decrypted data as bytes
        """
        try:
            # Extract components
            encrypted_data = base64.b64decode(encrypted_package["encrypted_data"])
            salt = base64.b64decode(encrypted_package["salt"])

            # Get Fernet instance
            fernet = self._get_fernet(salt)

            # Decrypt data
            decrypted_data = fernet.decrypt(encrypted_data)

            return decrypted_data

        except Exception as e:
            logger.error(f"Decryption failed: {e}")
            raise EncryptionError(f"Decryption failed: {e}")

    def encrypt_string(self, text: str) -> Dict[str, str]:
        """Encrypt a string and return the encrypted package."""
        return self.encrypt(text)

    def decrypt_string(self, encrypted_package: Dict[str, str]) -> str:
        """Decrypt a string from an encrypted package."""
        decrypted_bytes = self.decrypt(encrypted_package)
        return decrypted_bytes.decode("utf-8")


class SecureStorage:
    """
    Provides secure storage for sensitive application data.

    Uses system keyring for API keys and encrypted files for
    other sensitive data like session information.
    """

    def __init__(self, config: AppConfig) -> None:
        """
        Initialize secure storage.

        Args:
            config: Application configuration
        """
        self.config = config
        self.app_name = "kritrima-ai"
        self.storage_dir = Path.home() / ".kritrima-ai" / "secure"
        self.storage_dir.mkdir(parents=True, exist_ok=True)

        # Initialize encryption
        self.encryption = DataEncryption()

        logger.info("Secure storage initialized")

    def store_api_key(self, provider: str, api_key: str) -> None:
        """
        Store API key securely using system keyring.

        Args:
            provider: Provider name (e.g., "openai", "anthropic")
            api_key: API key to store
        """
        try:
            keyring.set_password(self.app_name, f"api_key_{provider}", api_key)
            logger.info(f"API key stored for provider: {provider}")
        except Exception as e:
            logger.error(f"Failed to store API key for {provider}: {e}")
            raise EncryptionError(f"Failed to store API key: {e}")

    def get_api_key(self, provider: str) -> Optional[str]:
        """
        Retrieve API key from system keyring.

        Args:
            provider: Provider name

        Returns:
            API key if found, None otherwise
        """
        try:
            api_key = keyring.get_password(self.app_name, f"api_key_{provider}")
            if api_key:
                logger.debug(f"Retrieved API key for provider: {provider}")
            return api_key
        except Exception as e:
            logger.error(f"Failed to retrieve API key for {provider}: {e}")
            return None

    def delete_api_key(self, provider: str) -> bool:
        """
        Delete API key from system keyring.

        Args:
            provider: Provider name

        Returns:
            True if deleted successfully
        """
        try:
            keyring.delete_password(self.app_name, f"api_key_{provider}")
            logger.info(f"API key deleted for provider: {provider}")
            return True
        except Exception as e:
            logger.error(f"Failed to delete API key for {provider}: {e}")
            return False

    def store_encrypted_data(self, key: str, data: Dict[str, Any]) -> None:
        """
        Store encrypted data to file.

        Args:
            key: Storage key/filename
            data: Data to store
        """
        try:
            # Serialize data
            json_data = json.dumps(data, indent=2)

            # Encrypt data
            encrypted_package = self.encryption.encrypt_string(json_data)

            # Store to file
            file_path = self.storage_dir / f"{key}.enc"
            with open(file_path, "w") as f:
                json.dump(encrypted_package, f, indent=2)

            logger.info(f"Encrypted data stored: {key}")

        except Exception as e:
            logger.error(f"Failed to store encrypted data for {key}: {e}")
            raise EncryptionError(f"Failed to store encrypted data: {e}")

    def get_encrypted_data(self, key: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve and decrypt data from file.

        Args:
            key: Storage key/filename

        Returns:
            Decrypted data if found, None otherwise
        """
        try:
            file_path = self.storage_dir / f"{key}.enc"

            if not file_path.exists():
                return None

            # Load encrypted package
            with open(file_path, "r") as f:
                encrypted_package = json.load(f)

            # Decrypt data
            decrypted_json = self.encryption.decrypt_string(encrypted_package)

            # Parse JSON
            data = json.loads(decrypted_json)

            logger.debug(f"Retrieved encrypted data: {key}")
            return data

        except Exception as e:
            logger.error(f"Failed to retrieve encrypted data for {key}: {e}")
            return None

    def delete_encrypted_data(self, key: str) -> bool:
        """
        Delete encrypted data file.

        Args:
            key: Storage key/filename

        Returns:
            True if deleted successfully
        """
        try:
            file_path = self.storage_dir / f"{key}.enc"

            if file_path.exists():
                file_path.unlink()
                logger.info(f"Encrypted data deleted: {key}")
                return True

            return False

        except Exception as e:
            logger.error(f"Failed to delete encrypted data for {key}: {e}")
            return False

    def list_stored_keys(self) -> List[str]:
        """
        List all stored encrypted data keys.

        Returns:
            List of storage keys
        """
        try:
            keys = []
            for file_path in self.storage_dir.glob("*.enc"):
                key = file_path.stem
                keys.append(key)

            return sorted(keys)

        except Exception as e:
            logger.error(f"Failed to list stored keys: {e}")
            return []

    def store_session_data(self, session_id: str, session_data: Dict[str, Any]) -> None:
        """
        Store session data securely.

        Args:
            session_id: Session identifier
            session_data: Session data to store
        """
        key = f"session_{session_id}"
        self.store_encrypted_data(key, session_data)

    def get_session_data(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve session data.

        Args:
            session_id: Session identifier

        Returns:
            Session data if found
        """
        key = f"session_{session_id}"
        return self.get_encrypted_data(key)

    def delete_session_data(self, session_id: str) -> bool:
        """
        Delete session data.

        Args:
            session_id: Session identifier

        Returns:
            True if deleted successfully
        """
        key = f"session_{session_id}"
        return self.delete_encrypted_data(key)

    def store_user_preferences(self, preferences: Dict[str, Any]) -> None:
        """
        Store user preferences securely.

        Args:
            preferences: User preferences to store
        """
        self.store_encrypted_data("user_preferences", preferences)

    def get_user_preferences(self) -> Dict[str, Any]:
        """
        Retrieve user preferences.

        Returns:
            User preferences or empty dict if not found
        """
        preferences = self.get_encrypted_data("user_preferences")
        return preferences or {}

    def backup_storage(self, backup_path: Path) -> None:
        """
        Create a backup of all stored data.

        Args:
            backup_path: Path for backup file
        """
        try:
            backup_data = {
                "timestamp": datetime.now().isoformat(),
                "app_name": self.app_name,
                "encrypted_files": {},
            }

            # Backup encrypted files
            for key in self.list_stored_keys():
                file_path = self.storage_dir / f"{key}.enc"
                with open(file_path, "r") as f:
                    backup_data["encrypted_files"][key] = json.load(f)

            # Save backup
            with open(backup_path, "w") as f:
                json.dump(backup_data, f, indent=2)

            logger.info(f"Storage backup created: {backup_path}")

        except Exception as e:
            logger.error(f"Failed to create storage backup: {e}")
            raise EncryptionError(f"Failed to create backup: {e}")

    def restore_storage(self, backup_path: Path) -> None:
        """
        Restore storage from backup.

        Args:
            backup_path: Path to backup file
        """
        try:
            # Load backup
            with open(backup_path, "r") as f:
                backup_data = json.load(f)

            # Restore encrypted files
            for key, encrypted_package in backup_data["encrypted_files"].items():
                file_path = self.storage_dir / f"{key}.enc"
                with open(file_path, "w") as f:
                    json.dump(encrypted_package, f, indent=2)

            logger.info(f"Storage restored from backup: {backup_path}")

        except Exception as e:
            logger.error(f"Failed to restore storage from backup: {e}")
            raise EncryptionError(f"Failed to restore from backup: {e}")

    def clear_all_data(self) -> None:
        """
        Clear all stored data (use with caution).
        """
        try:
            # Clear encrypted files
            for file_path in self.storage_dir.glob("*.enc"):
                file_path.unlink()

            # Clear API keys from keyring
            # Note: This is a simplified approach - in practice, you'd need to
            # track which keys were stored to delete them properly
            logger.warning(
                "Cleared all encrypted files. API keys in keyring may remain."
            )

            logger.info("All stored data cleared")

        except Exception as e:
            logger.error(f"Failed to clear all data: {e}")
            raise EncryptionError(f"Failed to clear data: {e}")

    def get_storage_stats(self) -> Dict[str, Any]:
        """
        Get storage statistics.

        Returns:
            Storage statistics
        """
        try:
            keys = self.list_stored_keys()
            total_size = 0

            for key in keys:
                file_path = self.storage_dir / f"{key}.enc"
                if file_path.exists():
                    total_size += file_path.stat().st_size

            return {
                "total_keys": len(keys),
                "total_size_bytes": total_size,
                "storage_directory": str(self.storage_dir),
                "keys": keys,
            }

        except Exception as e:
            logger.error(f"Failed to get storage stats: {e}")
            return {"error": str(e)}

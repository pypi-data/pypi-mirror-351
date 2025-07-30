"""
EcoCycle - Cloud Backup Module

This module provides cloud backup and sync functionality for the EcoCycle application.
It handles backing up and restoring user data to/from cloud storage.
"""

import os
import json
import logging
import datetime
import hashlib
import base64
import requests
from typing import Dict, Any, List, Optional, Tuple, Union

# Setup logger
logger = logging.getLogger(__name__)

# Cloud backup configuration
DEFAULT_CLOUD_CONFIG = {
    'enabled': False,
    'provider': 'local',  # 'local', 'dropbox', 'google_drive'
    'auto_backup': False,
    'backup_frequency': 'daily',  # 'hourly', 'daily', 'weekly', 'monthly'
    'last_backup': None,
    'encryption': False,
    'encryption_key': None,
    'sync_enabled': False,
    'sync_frequency': 'daily',  # 'hourly', 'daily', 'weekly', 'monthly'
    'last_sync': None
}

# Path to cloud backup configuration file
CONFIG_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'cloud')
CONFIG_FILE = os.path.join(CONFIG_DIR, 'cloud_config.json')

# Path to local backups
BACKUP_DIR = os.path.join(CONFIG_DIR, 'backups')


class CloudBackupManager:
    """Manages cloud backup and sync functionality."""

    def __init__(self):
        """Initialize the cloud backup manager."""
        self.config = DEFAULT_CLOUD_CONFIG.copy()
        self._load_config()
        self._ensure_directories()

    def _ensure_directories(self) -> None:
        """Ensure required directories exist."""
        os.makedirs(CONFIG_DIR, exist_ok=True)
        os.makedirs(BACKUP_DIR, exist_ok=True)

    def _load_config(self) -> None:
        """Load cloud backup configuration."""
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    # Update config with loaded values
                    self.config.update(config)
            except Exception as e:
                logger.error(f"Error loading cloud backup configuration: {e}")

    def _save_config(self) -> bool:
        """
        Save cloud backup configuration.

        Returns:
            bool: True if configuration was saved successfully, False otherwise.
        """
        try:
            self._ensure_directories()
            with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            logger.error(f"Error saving cloud backup configuration: {e}")
            return False

    def enable_cloud_backup(self, enabled: bool = True) -> bool:
        """
        Enable or disable cloud backup.

        Args:
            enabled (bool): Whether to enable cloud backup.

        Returns:
            bool: True if setting was updated successfully, False otherwise.
        """
        self.config['enabled'] = enabled
        return self._save_config()

    def set_provider(self, provider: str) -> bool:
        """
        Set the cloud provider.

        Args:
            provider (str): The cloud provider ('local', 'dropbox', 'google_drive').

        Returns:
            bool: True if provider was set successfully, False otherwise.
        """
        if provider not in ['local', 'dropbox', 'google_drive']:
            logger.error(f"Invalid cloud provider: {provider}")
            return False
        self.config['provider'] = provider
        return self._save_config()

    def enable_auto_backup(self, enabled: bool = True) -> bool:
        """
        Enable or disable automatic backups.

        Args:
            enabled (bool): Whether to enable automatic backups.

        Returns:
            bool: True if setting was updated successfully, False otherwise.
        """
        self.config['auto_backup'] = enabled
        return self._save_config()

    def set_backup_frequency(self, frequency: str) -> bool:
        """
        Set the backup frequency.

        Args:
            frequency (str): The backup frequency ('hourly', 'daily', 'weekly', 'monthly').

        Returns:
            bool: True if frequency was set successfully, False otherwise.
        """
        if frequency not in ['hourly', 'daily', 'weekly', 'monthly']:
            logger.error(f"Invalid backup frequency: {frequency}")
            return False
        self.config['backup_frequency'] = frequency
        return self._save_config()

    def enable_encryption(self, enabled: bool = True, key: Optional[str] = None) -> bool:
        """
        Enable or disable backup encryption.

        Args:
            enabled (bool): Whether to enable encryption.
            key (Optional[str]): The encryption key.

        Returns:
            bool: True if setting was updated successfully, False otherwise.
        """
        self.config['encryption'] = enabled
        if enabled and key:
            # Store a hash of the key, not the key itself
            self.config['encryption_key'] = self._hash_key(key)
        elif not enabled:
            self.config['encryption_key'] = None
        return self._save_config()

    def _hash_key(self, key: str) -> str:
        """
        Hash an encryption key.

        Args:
            key (str): The encryption key.

        Returns:
            str: The hashed key.
        """
        return hashlib.sha256(key.encode()).hexdigest()

    def enable_sync(self, enabled: bool = True) -> bool:
        """
        Enable or disable data sync.

        Args:
            enabled (bool): Whether to enable sync.

        Returns:
            bool: True if setting was updated successfully, False otherwise.
        """
        self.config['sync_enabled'] = enabled
        return self._save_config()

    def set_sync_frequency(self, frequency: str) -> bool:
        """
        Set the sync frequency.

        Args:
            frequency (str): The sync frequency ('hourly', 'daily', 'weekly', 'monthly').

        Returns:
            bool: True if frequency was set successfully, False otherwise.
        """
        if frequency not in ['hourly', 'daily', 'weekly', 'monthly']:
            logger.error(f"Invalid sync frequency: {frequency}")
            return False
        self.config['sync_frequency'] = frequency
        return self._save_config()

    def create_backup(self, user_data: Dict[str, Any], encryption_key: Optional[str] = None) -> Optional[str]:
        """
        Create a backup of user data.

        Args:
            user_data (Dict[str, Any]): The user data to backup.
            encryption_key (Optional[str]): The encryption key for encrypted backups.

        Returns:
            Optional[str]: The backup file path if successful, None otherwise.
        """
        try:
            # Create backup filename with timestamp
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            username = user_data.get('username', 'user')
            filename = f"ecocycle_{username}_backup_{timestamp}.json"
            filepath = os.path.join(BACKUP_DIR, filename)

            # Remove sensitive information
            backup_data = user_data.copy()
            if 'password_hash' in backup_data:
                del backup_data['password_hash']
            if 'salt' in backup_data:
                del backup_data['salt']

            # Encrypt data if encryption is enabled
            if self.config['encryption']:
                if not encryption_key and not self.config['encryption_key']:
                    logger.error("Encryption key required for encrypted backup")
                    return None
                
                # Use provided key or stored key hash
                key_hash = self._hash_key(encryption_key) if encryption_key else self.config['encryption_key']
                
                # Simple encryption for demonstration (not secure for production)
                backup_json = json.dumps(backup_data)
                encrypted_data = self._encrypt_data(backup_json, key_hash)
                
                # Write encrypted data
                with open(filepath, 'wb') as f:
                    f.write(encrypted_data)
            else:
                # Write unencrypted data
                with open(filepath, 'w', encoding='utf-8') as f:
                    json.dump(backup_data, f, indent=2, ensure_ascii=False)

            # Update last backup timestamp
            self.config['last_backup'] = datetime.datetime.now().isoformat()
            self._save_config()

            # Upload to cloud if not local
            if self.config['provider'] != 'local':
                self._upload_to_cloud(filepath)

            return filepath
        except Exception as e:
            logger.error(f"Error creating backup: {e}")
            return None

    def restore_backup(self, backup_path: str, encryption_key: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Restore a backup.

        Args:
            backup_path (str): The backup file path.
            encryption_key (Optional[str]): The encryption key for encrypted backups.

        Returns:
            Optional[Dict[str, Any]]: The restored user data if successful, None otherwise.
        """
        try:
            # Check if file exists
            if not os.path.exists(backup_path):
                logger.error(f"Backup file not found: {backup_path}")
                return None

            # Determine if backup is encrypted
            is_encrypted = self._is_backup_encrypted(backup_path)

            if is_encrypted:
                if not encryption_key:
                    logger.error("Encryption key required for encrypted backup")
                    return None
                
                # Read encrypted data
                with open(backup_path, 'rb') as f:
                    encrypted_data = f.read()
                
                # Decrypt data
                key_hash = self._hash_key(encryption_key)
                decrypted_json = self._decrypt_data(encrypted_data, key_hash)
                
                # Parse JSON
                user_data = json.loads(decrypted_json)
            else:
                # Read unencrypted data
                with open(backup_path, 'r', encoding='utf-8') as f:
                    user_data = json.load(f)

            return user_data
        except Exception as e:
            logger.error(f"Error restoring backup: {e}")
            return None

    def _is_backup_encrypted(self, backup_path: str) -> bool:
        """
        Check if a backup file is encrypted.

        Args:
            backup_path (str): The backup file path.

        Returns:
            bool: True if backup is encrypted, False otherwise.
        """
        try:
            # Try to read as JSON
            with open(backup_path, 'r', encoding='utf-8') as f:
                json.load(f)
            return False
        except:
            # If JSON parsing fails, assume it's encrypted
            return True

    def _encrypt_data(self, data: str, key: str) -> bytes:
        """
        Encrypt data.

        Args:
            data (str): The data to encrypt.
            key (str): The encryption key.

        Returns:
            bytes: The encrypted data.
        """
        # Simple XOR encryption for demonstration (not secure for production)
        key_bytes = key.encode()
        data_bytes = data.encode()
        encrypted = bytearray()
        
        for i in range(len(data_bytes)):
            encrypted.append(data_bytes[i] ^ key_bytes[i % len(key_bytes)])
        
        return base64.b64encode(encrypted)

    def _decrypt_data(self, encrypted_data: bytes, key: str) -> str:
        """
        Decrypt data.

        Args:
            encrypted_data (bytes): The encrypted data.
            key (str): The encryption key.

        Returns:
            str: The decrypted data.
        """
        # Simple XOR decryption for demonstration (not secure for production)
        key_bytes = key.encode()
        data_bytes = base64.b64decode(encrypted_data)
        decrypted = bytearray()
        
        for i in range(len(data_bytes)):
            decrypted.append(data_bytes[i] ^ key_bytes[i % len(key_bytes)])
        
        return decrypted.decode()

    def _upload_to_cloud(self, file_path: str) -> bool:
        """
        Upload a file to cloud storage.

        Args:
            file_path (str): The file path to upload.

        Returns:
            bool: True if upload was successful, False otherwise.
        """
        # Implementation depends on the cloud provider
        provider = self.config['provider']
        
        if provider == 'dropbox':
            return self._upload_to_dropbox(file_path)
        elif provider == 'google_drive':
            return self._upload_to_google_drive(file_path)
        else:
            # Local provider doesn't need upload
            return True

    def _upload_to_dropbox(self, file_path: str) -> bool:
        """
        Upload a file to Dropbox.

        Args:
            file_path (str): The file path to upload.

        Returns:
            bool: True if upload was successful, False otherwise.
        """
        # Placeholder for Dropbox API integration
        logger.info(f"Uploading to Dropbox: {file_path}")
        return True

    def _upload_to_google_drive(self, file_path: str) -> bool:
        """
        Upload a file to Google Drive.

        Args:
            file_path (str): The file path to upload.

        Returns:
            bool: True if upload was successful, False otherwise.
        """
        # Placeholder for Google Drive API integration
        logger.info(f"Uploading to Google Drive: {file_path}")
        return True

    def get_available_backups(self) -> List[Dict[str, Any]]:
        """
        Get a list of available backups.

        Returns:
            List[Dict[str, Any]]: List of backup information.
        """
        backups = []
        
        try:
            for filename in os.listdir(BACKUP_DIR):
                if filename.endswith('.json'):
                    file_path = os.path.join(BACKUP_DIR, filename)
                    file_stat = os.stat(file_path)
                    
                    # Parse filename for metadata
                    parts = filename.split('_')
                    username = parts[1] if len(parts) > 1 else 'unknown'
                    
                    # Parse timestamp from filename
                    timestamp_str = parts[3].split('.')[0] if len(parts) > 3 else None
                    timestamp = None
                    if timestamp_str:
                        try:
                            timestamp = datetime.datetime.strptime(timestamp_str, "%Y%m%d%H%M%S")
                        except:
                            pass
                    
                    backups.append({
                        'filename': filename,
                        'path': file_path,
                        'size': file_stat.st_size,
                        'created': datetime.datetime.fromtimestamp(file_stat.st_ctime).isoformat(),
                        'username': username,
                        'timestamp': timestamp.isoformat() if timestamp else None,
                        'encrypted': self._is_backup_encrypted(file_path)
                    })
        except Exception as e:
            logger.error(f"Error getting available backups: {e}")
        
        # Sort by creation time (newest first)
        backups.sort(key=lambda x: x['created'], reverse=True)
        return backups


# Global cloud backup manager instance
_cloud_backup_manager = None


def get_cloud_backup_manager() -> CloudBackupManager:
    """
    Get the global cloud backup manager instance.

    Returns:
        CloudBackupManager: The global cloud backup manager instance.
    """
    global _cloud_backup_manager
    if _cloud_backup_manager is None:
        _cloud_backup_manager = CloudBackupManager()
    return _cloud_backup_manager

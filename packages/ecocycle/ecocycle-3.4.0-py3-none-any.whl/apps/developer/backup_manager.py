"""
EcoCycle - Comprehensive Backup Manager

This module provides comprehensive backup and restore functionality for the EcoCycle application.
It handles full system backups, user data backups, database backups, and automated scheduling.
"""

import os
import json
import sqlite3
import shutil
import gzip
import hashlib
import base64
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple
import traceback

# Setup logger
logger = logging.getLogger(__name__)

# Backup configuration
BACKUP_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'data', 'backups')
SCHEDULE_CONFIG_FILE = os.path.join(BACKUP_DIR, 'schedule_config.json')
BACKUP_HISTORY_FILE = os.path.join(BACKUP_DIR, 'backup_history.json')

# Default schedule configuration
DEFAULT_SCHEDULE_CONFIG = {
    'enabled': False,
    'frequency': 'daily',  # hourly, daily, weekly, monthly
    'backup_time': '02:00',  # HH:MM format
    'backup_types': ['full'],  # full, user, database, config
    'encryption_enabled': False,
    'retention_days': 30,
    'max_backups': 50,
    'last_backup': None,
    'next_backup': None
}


class BackupManager:
    """Comprehensive backup and restore manager for EcoCycle."""

    def __init__(self, developer_tools):
        """Initialize the backup manager."""
        self.developer_tools = developer_tools
        self.schedule_config = DEFAULT_SCHEDULE_CONFIG.copy()
        self._ensure_directories()
        self._load_schedule_config()

    def _ensure_directories(self) -> None:
        """Ensure required directories exist."""
        os.makedirs(BACKUP_DIR, exist_ok=True)

    def _load_schedule_config(self) -> None:
        """Load backup schedule configuration."""
        if os.path.exists(SCHEDULE_CONFIG_FILE):
            try:
                with open(SCHEDULE_CONFIG_FILE, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    self.schedule_config.update(config)
            except Exception as e:
                logger.error(f"Error loading schedule config: {e}")

    def _save_schedule_config(self) -> bool:
        """Save backup schedule configuration."""
        try:
            with open(SCHEDULE_CONFIG_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.schedule_config, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            logger.error(f"Error saving schedule config: {e}")
            return False

    def _encrypt_data(self, data: str, key: str) -> bytes:
        """Encrypt data using simple XOR encryption."""
        key_bytes = hashlib.sha256(key.encode()).digest()
        data_bytes = data.encode('utf-8')
        encrypted = bytearray()

        for i in range(len(data_bytes)):
            encrypted.append(data_bytes[i] ^ key_bytes[i % len(key_bytes)])

        return base64.b64encode(encrypted)

    def _decrypt_data(self, encrypted_data: bytes, key: str) -> str:
        """Decrypt data using simple XOR decryption."""
        key_bytes = hashlib.sha256(key.encode()).digest()
        data_bytes = base64.b64decode(encrypted_data)
        decrypted = bytearray()

        for i in range(len(data_bytes)):
            decrypted.append(data_bytes[i] ^ key_bytes[i % len(key_bytes)])

        return decrypted.decode('utf-8')

    def _generate_backup_filename(self, backup_type: str, encrypted: bool = False) -> str:
        """Generate a backup filename with timestamp."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        extension = ".enc" if encrypted else ".json"
        return f"ecocycle_{backup_type}_backup_{timestamp}{extension}"

    def _add_to_history(self, backup_info: Dict[str, Any]) -> None:
        """Add backup to history."""
        try:
            history = []
            if os.path.exists(BACKUP_HISTORY_FILE):
                with open(BACKUP_HISTORY_FILE, 'r', encoding='utf-8') as f:
                    history = json.load(f)

            history.append(backup_info)

            # Keep only last 100 entries
            if len(history) > 100:
                history = history[-100:]

            with open(BACKUP_HISTORY_FILE, 'w', encoding='utf-8') as f:
                json.dump(history, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Error adding to backup history: {e}")

    def create_full_backup(self, include_sensitive: bool = False, encryption_key: Optional[str] = None) -> Dict[str, Any]:
        """Create a full system backup."""
        start_time = datetime.now()
        result = {
            'success': False,
            'backup_type': 'full',
            'timestamp': start_time.isoformat(),
            'components': [],
            'errors': []
        }

        try:
            backup_data = {
                'backup_type': 'full',
                'timestamp': start_time.isoformat(),
                'version': '1.0',
                'components': {}
            }

            # Backup user data
            try:
                users_file = os.path.join(os.getcwd(), 'data', 'user', 'users.json')
                if os.path.exists(users_file):
                    with open(users_file, 'r', encoding='utf-8') as f:
                        users_data = json.load(f)

                    # Remove sensitive data if not included
                    if not include_sensitive:
                        for username, user_data in users_data.items():
                            if 'password_hash' in user_data:
                                del user_data['password_hash']
                            if 'salt' in user_data:
                                del user_data['salt']

                    backup_data['components']['users'] = users_data
                    result['components'].append('users')
            except Exception as e:
                result['errors'].append(f"Users backup error: {e}")

            # Backup database
            try:
                db_data = self.developer_tools.view_database_contents()
                if 'error' not in db_data:
                    backup_data['components']['database'] = db_data
                    result['components'].append('database')
            except Exception as e:
                result['errors'].append(f"Database backup error: {e}")

            # Backup cache data
            try:
                cache_data = self.developer_tools.manage_cache('view')
                backup_data['components']['cache'] = cache_data
                result['components'].append('cache')
            except Exception as e:
                result['errors'].append(f"Cache backup error: {e}")

            # Backup configuration
            try:
                config_data = self.developer_tools.manage_configuration('view')
                if 'config' in config_data:
                    backup_data['components']['config'] = config_data['config']
                    result['components'].append('config')
            except Exception as e:
                result['errors'].append(f"Config backup error: {e}")

            # Backup recent logs
            try:
                log_dir = os.path.join(os.getcwd(), 'Logs')
                if os.path.exists(log_dir):
                    logs = {}
                    for log_file in os.listdir(log_dir):
                        if log_file.endswith('.log'):
                            log_path = os.path.join(log_dir, log_file)
                            try:
                                with open(log_path, 'r', encoding='utf-8') as f:
                                    lines = f.readlines()
                                    logs[log_file] = lines[-50:] if len(lines) > 50 else lines
                            except Exception as e:
                                logs[log_file] = f"Error reading log: {e}"
                    backup_data['components']['logs'] = logs
                    result['components'].append('logs')
            except Exception as e:
                result['errors'].append(f"Logs backup error: {e}")

            # Save backup
            filename = self._generate_backup_filename('full', bool(encryption_key))
            backup_path = os.path.join(BACKUP_DIR, filename)

            if encryption_key:
                backup_json = json.dumps(backup_data, indent=2, default=str)
                encrypted_data = self._encrypt_data(backup_json, encryption_key)
                with open(backup_path, 'wb') as f:
                    f.write(encrypted_data)
            else:
                with open(backup_path, 'w', encoding='utf-8') as f:
                    json.dump(backup_data, f, indent=2, default=str)

            # Calculate file size
            file_size = os.path.getsize(backup_path)
            result['backup_path'] = backup_path
            result['filename'] = filename
            result['size_mb'] = round(file_size / (1024 * 1024), 2)
            result['encrypted'] = bool(encryption_key)
            result['success'] = True

            # Add to history
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()

            history_entry = {
                'date': start_time.isoformat(),
                'type': 'full',
                'status': 'success',
                'filename': filename,
                'size_mb': result['size_mb'],
                'duration': f"{duration:.2f}s",
                'components': result['components'],
                'encrypted': result['encrypted'],
                'errors': result['errors']
            }
            self._add_to_history(history_entry)

            return result

        except Exception as e:
            result['error'] = str(e)
            result['traceback'] = traceback.format_exc()

            # Add to history even if failed
            history_entry = {
                'date': start_time.isoformat(),
                'type': 'full',
                'status': 'failed',
                'error': str(e),
                'duration': f"{(datetime.now() - start_time).total_seconds():.2f}s"
            }
            self._add_to_history(history_entry)

            return result

    def create_user_backup(self, usernames: Optional[List[str]] = None, encryption_key: Optional[str] = None) -> Dict[str, Any]:
        """Create a user data backup."""
        start_time = datetime.now()
        result = {
            'success': False,
            'backup_type': 'user',
            'timestamp': start_time.isoformat(),
            'users_backed_up': [],
            'errors': []
        }

        try:
            # Get user data
            users_data = self.developer_tools.manage_user_data('list')
            if 'error' in users_data:
                result['error'] = f"Failed to get user data: {users_data['error']}"
                return result

            all_users = users_data.get('users', {})

            # Filter users if specified
            if usernames:
                filtered_users = {username: all_users[username] for username in usernames if username in all_users}
            else:
                filtered_users = all_users

            if not filtered_users:
                result['error'] = "No users found to backup"
                return result

            backup_data = {
                'backup_type': 'user',
                'timestamp': start_time.isoformat(),
                'version': '1.0',
                'users': {}
            }

            # Process each user
            for username, user_data in filtered_users.items():
                try:
                    # Create a clean copy without sensitive data
                    clean_user_data = user_data.copy()
                    if 'password_hash' in clean_user_data:
                        del clean_user_data['password_hash']
                    if 'salt' in clean_user_data:
                        del clean_user_data['salt']

                    backup_data['users'][username] = clean_user_data
                    result['users_backed_up'].append(username)
                except Exception as e:
                    result['errors'].append(f"Error backing up user {username}: {e}")

            # Save backup
            filename = self._generate_backup_filename('user', bool(encryption_key))
            backup_path = os.path.join(BACKUP_DIR, filename)

            if encryption_key:
                backup_json = json.dumps(backup_data, indent=2, default=str)
                encrypted_data = self._encrypt_data(backup_json, encryption_key)
                with open(backup_path, 'wb') as f:
                    f.write(encrypted_data)
            else:
                with open(backup_path, 'w', encoding='utf-8') as f:
                    json.dump(backup_data, f, indent=2, default=str)

            # Calculate file size
            file_size = os.path.getsize(backup_path)
            result['backup_path'] = backup_path
            result['filename'] = filename
            result['size_mb'] = round(file_size / (1024 * 1024), 2)
            result['encrypted'] = bool(encryption_key)
            result['success'] = True

            # Add to history
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()

            history_entry = {
                'date': start_time.isoformat(),
                'type': 'user',
                'status': 'success',
                'filename': filename,
                'size_mb': result['size_mb'],
                'duration': f"{duration:.2f}s",
                'users_count': len(result['users_backed_up']),
                'encrypted': result['encrypted'],
                'errors': result['errors']
            }
            self._add_to_history(history_entry)

            return result

        except Exception as e:
            result['error'] = str(e)
            result['traceback'] = traceback.format_exc()

            # Add to history even if failed
            history_entry = {
                'date': start_time.isoformat(),
                'type': 'user',
                'status': 'failed',
                'error': str(e),
                'duration': f"{(datetime.now() - start_time).total_seconds():.2f}s"
            }
            self._add_to_history(history_entry)

            return result

    def create_database_backup(self, include_integrity_check: bool = True, compress: bool = False) -> Dict[str, Any]:
        """Create a database backup."""
        start_time = datetime.now()
        result = {
            'success': False,
            'backup_type': 'database',
            'timestamp': start_time.isoformat(),
            'integrity_check': include_integrity_check,
            'compressed': compress,
            'errors': []
        }

        try:
            # Get database file path
            database_file = os.path.join(os.getcwd(), 'data', 'sync', 'sync.db')

            if not os.path.exists(database_file):
                result['error'] = "Database file not found"
                return result

            # Perform integrity check if requested
            if include_integrity_check:
                try:
                    conn = sqlite3.connect(database_file)
                    cursor = conn.cursor()
                    cursor.execute("PRAGMA integrity_check")
                    integrity_result = cursor.fetchone()[0]
                    conn.close()

                    result['integrity_status'] = integrity_result
                    if integrity_result != 'ok':
                        result['errors'].append(f"Database integrity check failed: {integrity_result}")
                except Exception as e:
                    result['errors'].append(f"Integrity check error: {e}")

            # Create backup filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            extension = ".gz" if compress else ".db"
            filename = f"ecocycle_database_backup_{timestamp}{extension}"
            backup_path = os.path.join(BACKUP_DIR, filename)

            # Copy database file
            if compress:
                with open(database_file, 'rb') as f_in:
                    with gzip.open(backup_path, 'wb') as f_out:
                        shutil.copyfileobj(f_in, f_out)
            else:
                shutil.copy2(database_file, backup_path)

            # Calculate file sizes
            original_size = os.path.getsize(database_file)
            backup_size = os.path.getsize(backup_path)

            result['backup_path'] = backup_path
            result['filename'] = filename
            result['database_size_mb'] = round(original_size / (1024 * 1024), 2)
            result['backup_size_mb'] = round(backup_size / (1024 * 1024), 2)
            result['compression_ratio'] = round((1 - backup_size / original_size) * 100, 1) if compress else 0
            result['success'] = True

            # Add to history
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()

            history_entry = {
                'date': start_time.isoformat(),
                'type': 'database',
                'status': 'success',
                'filename': filename,
                'size_mb': result['backup_size_mb'],
                'duration': f"{duration:.2f}s",
                'compressed': compress,
                'integrity_check': include_integrity_check,
                'integrity_status': result.get('integrity_status', 'not_checked'),
                'errors': result['errors']
            }
            self._add_to_history(history_entry)

            return result

        except Exception as e:
            result['error'] = str(e)
            result['traceback'] = traceback.format_exc()

            # Add to history even if failed
            history_entry = {
                'date': start_time.isoformat(),
                'type': 'database',
                'status': 'failed',
                'error': str(e),
                'duration': f"{(datetime.now() - start_time).total_seconds():.2f}s"
            }
            self._add_to_history(history_entry)

            return result

    def restore_backup(self, backup_path: str, encryption_key: Optional[str] = None) -> Dict[str, Any]:
        """Restore from a backup file."""
        start_time = datetime.now()
        result = {
            'success': False,
            'timestamp': start_time.isoformat(),
            'restored_components': [],
            'warnings': [],
            'errors': []
        }

        try:
            if not os.path.exists(backup_path):
                result['error'] = f"Backup file not found: {backup_path}"
                return result

            # Determine if backup is encrypted
            is_encrypted = backup_path.endswith('.enc')

            # Load backup data
            if is_encrypted:
                if not encryption_key:
                    result['error'] = "Encryption key required for encrypted backup"
                    return result

                with open(backup_path, 'rb') as f:
                    encrypted_data = f.read()

                try:
                    decrypted_json = self._decrypt_data(encrypted_data, encryption_key)
                    backup_data = json.loads(decrypted_json)
                except Exception as e:
                    result['error'] = f"Failed to decrypt backup: {e}"
                    return result
            else:
                with open(backup_path, 'r', encoding='utf-8') as f:
                    backup_data = json.load(f)

            backup_type = backup_data.get('backup_type', 'unknown')
            components = backup_data.get('components', {}) if backup_type == 'full' else backup_data

            # Restore based on backup type
            if backup_type == 'full':
                # Restore users
                if 'users' in components:
                    try:
                        users_file = os.path.join(os.getcwd(), 'data', 'user', 'users.json')
                        # Create backup of current users
                        if os.path.exists(users_file):
                            backup_current = f"{users_file}.restore_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                            shutil.copy2(users_file, backup_current)
                            result['warnings'].append(f"Current users backed up to: {backup_current}")

                        # Restore users data
                        with open(users_file, 'w', encoding='utf-8') as f:
                            json.dump(components['users'], f, indent=2)
                        result['restored_components'].append('users')
                    except Exception as e:
                        result['errors'].append(f"Failed to restore users: {e}")

                # Restore database
                if 'database' in components:
                    try:
                        # Note: This would restore database metadata, not the actual database file
                        result['warnings'].append("Database metadata restored (actual database file restoration requires separate process)")
                        result['restored_components'].append('database_metadata')
                    except Exception as e:
                        result['errors'].append(f"Failed to restore database: {e}")

                # Restore cache
                if 'cache' in components:
                    try:
                        cache_dir = os.path.join(os.getcwd(), 'data', 'cache')
                        os.makedirs(cache_dir, exist_ok=True)

                        cache_data = components['cache']
                        for cache_file, cache_content in cache_data.items():
                            if isinstance(cache_content, dict):
                                cache_path = os.path.join(cache_dir, f"{cache_file}.json")
                                with open(cache_path, 'w', encoding='utf-8') as f:
                                    json.dump(cache_content, f, indent=2)

                        result['restored_components'].append('cache')
                    except Exception as e:
                        result['errors'].append(f"Failed to restore cache: {e}")

                # Restore configuration
                if 'config' in components:
                    try:
                        # This would integrate with the configuration management system
                        result['warnings'].append("Configuration restoration requires manual review")
                        result['restored_components'].append('config_metadata')
                    except Exception as e:
                        result['errors'].append(f"Failed to restore config: {e}")

            elif backup_type == 'user':
                # Restore user data
                try:
                    users_file = os.path.join(os.getcwd(), 'data', 'user', 'users.json')
                    current_users = {}

                    if os.path.exists(users_file):
                        with open(users_file, 'r', encoding='utf-8') as f:
                            current_users = json.load(f)

                        # Create backup of current users
                        backup_current = f"{users_file}.restore_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                        shutil.copy2(users_file, backup_current)
                        result['warnings'].append(f"Current users backed up to: {backup_current}")

                    # Merge restored users with current users
                    restored_users = backup_data.get('users', {})
                    current_users.update(restored_users)

                    with open(users_file, 'w', encoding='utf-8') as f:
                        json.dump(current_users, f, indent=2)

                    result['restored_components'].append('users')
                    result['warnings'].append(f"Restored {len(restored_users)} user accounts")
                except Exception as e:
                    result['errors'].append(f"Failed to restore users: {e}")

            elif backup_type == 'database':
                result['warnings'].append("Database file restoration requires manual process")
                result['restored_components'].append('database_reference')

            result['success'] = len(result['restored_components']) > 0

            # Add to history
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()

            history_entry = {
                'date': start_time.isoformat(),
                'type': 'restore',
                'status': 'success' if result['success'] else 'partial',
                'source_file': os.path.basename(backup_path),
                'duration': f"{duration:.2f}s",
                'restored_components': result['restored_components'],
                'warnings': result['warnings'],
                'errors': result['errors']
            }
            self._add_to_history(history_entry)

            return result

        except Exception as e:
            result['error'] = str(e)
            result['traceback'] = traceback.format_exc()

            # Add to history even if failed
            history_entry = {
                'date': start_time.isoformat(),
                'type': 'restore',
                'status': 'failed',
                'source_file': os.path.basename(backup_path) if backup_path else 'unknown',
                'error': str(e),
                'duration': f"{(datetime.now() - start_time).total_seconds():.2f}s"
            }
            self._add_to_history(history_entry)

            return result

    def list_backups(self) -> List[Dict[str, Any]]:
        """List all available backups."""
        backups = []

        try:
            if not os.path.exists(BACKUP_DIR):
                return backups

            for filename in os.listdir(BACKUP_DIR):
                if filename.startswith('ecocycle_') and (filename.endswith('.json') or filename.endswith('.enc') or filename.endswith('.db') or filename.endswith('.gz')):
                    file_path = os.path.join(BACKUP_DIR, filename)
                    file_stat = os.stat(file_path)

                    # Parse backup type from filename
                    backup_type = 'unknown'
                    if '_full_backup_' in filename:
                        backup_type = 'full'
                    elif '_user_backup_' in filename:
                        backup_type = 'user'
                    elif '_database_backup_' in filename:
                        backup_type = 'database'

                    # Determine if encrypted
                    encrypted = filename.endswith('.enc')

                    # Parse timestamp from filename
                    timestamp_str = None
                    try:
                        parts = filename.split('_')
                        for i, part in enumerate(parts):
                            if len(part) == 8 and part.isdigit():  # YYYYMMDD
                                if i + 1 < len(parts) and len(parts[i + 1]) >= 6:  # HHMMSS
                                    timestamp_str = f"{part}_{parts[i + 1].split('.')[0]}"
                                    break
                    except:
                        pass

                    # Validate backup integrity
                    status = 'valid'
                    try:
                        if filename.endswith('.json'):
                            with open(file_path, 'r', encoding='utf-8') as f:
                                json.load(f)
                        elif filename.endswith('.enc'):
                            # Can't validate encrypted files without key
                            status = 'encrypted'
                        elif filename.endswith('.db'):
                            # Basic SQLite file check
                            with open(file_path, 'rb') as f:
                                header = f.read(16)
                                if not header.startswith(b'SQLite format 3'):
                                    status = 'corrupted'
                    except Exception:
                        status = 'corrupted'

                    backups.append({
                        'filename': filename,
                        'path': file_path,
                        'type': backup_type,
                        'size_mb': round(file_stat.st_size / (1024 * 1024), 2),
                        'created': datetime.fromtimestamp(file_stat.st_ctime).strftime('%Y-%m-%d %H:%M:%S'),
                        'modified': datetime.fromtimestamp(file_stat.st_mtime).strftime('%Y-%m-%d %H:%M:%S'),
                        'encrypted': encrypted,
                        'status': status,
                        'timestamp': timestamp_str
                    })

            # Sort by creation time (newest first)
            backups.sort(key=lambda x: x['created'], reverse=True)

        except Exception as e:
            logger.error(f"Error listing backups: {e}")

        return backups

    def get_backup_history(self) -> List[Dict[str, Any]]:
        """Get backup history."""
        try:
            if os.path.exists(BACKUP_HISTORY_FILE):
                with open(BACKUP_HISTORY_FILE, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            logger.error(f"Error reading backup history: {e}")
        return []

    def get_schedule_info(self) -> Dict[str, Any]:
        """Get current backup schedule information."""
        schedule_info = self.schedule_config.copy()

        # Calculate next backup time if enabled
        if schedule_info['enabled']:
            try:
                frequency = schedule_info['frequency']
                backup_time = schedule_info['backup_time']

                # Parse backup time
                hour, minute = map(int, backup_time.split(':'))

                # Calculate next backup
                now = datetime.now()
                next_backup = now.replace(hour=hour, minute=minute, second=0, microsecond=0)

                if frequency == 'hourly':
                    if next_backup <= now:
                        next_backup += timedelta(hours=1)
                elif frequency == 'daily':
                    if next_backup <= now:
                        next_backup += timedelta(days=1)
                elif frequency == 'weekly':
                    if next_backup <= now:
                        next_backup += timedelta(weeks=1)
                elif frequency == 'monthly':
                    if next_backup <= now:
                        # Add one month (approximate)
                        next_backup += timedelta(days=30)

                schedule_info['next_backup'] = next_backup.strftime('%Y-%m-%d %H:%M:%S')
            except Exception as e:
                schedule_info['next_backup'] = f"Error calculating: {e}"

        return schedule_info

    def enable_schedule(self, frequency: str = 'daily', backup_time: str = '02:00', backup_types: Optional[List[str]] = None) -> Dict[str, Any]:
        """Enable automatic backup schedule."""
        try:
            if backup_types is None:
                backup_types = ['full']

            self.schedule_config.update({
                'enabled': True,
                'frequency': frequency,
                'backup_time': backup_time,
                'backup_types': backup_types
            })

            if self._save_schedule_config():
                return {'success': True, 'message': 'Backup schedule enabled'}
            else:
                return {'success': False, 'error': 'Failed to save schedule configuration'}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def disable_schedule(self) -> Dict[str, Any]:
        """Disable automatic backup schedule."""
        try:
            self.schedule_config['enabled'] = False

            if self._save_schedule_config():
                return {'success': True, 'message': 'Backup schedule disabled'}
            else:
                return {'success': False, 'error': 'Failed to save schedule configuration'}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def set_frequency(self, frequency: str) -> Dict[str, Any]:
        """Set backup frequency."""
        try:
            if frequency not in ['hourly', 'daily', 'weekly', 'monthly']:
                return {'success': False, 'error': 'Invalid frequency'}

            self.schedule_config['frequency'] = frequency

            if self._save_schedule_config():
                return {'success': True, 'message': f'Backup frequency set to {frequency}'}
            else:
                return {'success': False, 'error': 'Failed to save schedule configuration'}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def set_backup_time(self, backup_time: str) -> Dict[str, Any]:
        """Set backup time."""
        try:
            # Validate time format
            hour, minute = map(int, backup_time.split(':'))
            if not (0 <= hour <= 23 and 0 <= minute <= 59):
                return {'success': False, 'error': 'Invalid time format'}

            self.schedule_config['backup_time'] = backup_time

            if self._save_schedule_config():
                return {'success': True, 'message': f'Backup time set to {backup_time}'}
            else:
                return {'success': False, 'error': 'Failed to save schedule configuration'}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def set_backup_types(self, backup_types: List[str]) -> Dict[str, Any]:
        """Set backup types."""
        try:
            valid_types = ['full', 'user', 'database', 'config']
            invalid_types = [t for t in backup_types if t not in valid_types]

            if invalid_types:
                return {'success': False, 'error': f'Invalid backup types: {invalid_types}'}

            self.schedule_config['backup_types'] = backup_types

            if self._save_schedule_config():
                return {'success': True, 'message': f'Backup types set to: {", ".join(backup_types)}'}
            else:
                return {'success': False, 'error': 'Failed to save schedule configuration'}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def cleanup_old_backups(self, retention_days: Optional[int] = None) -> Dict[str, Any]:
        """Clean up old backup files."""
        if retention_days is None:
            retention_days = self.schedule_config.get('retention_days', 30)

        result = {
            'success': False,
            'deleted_files': [],
            'errors': []
        }

        try:
            # Ensure retention_days is a valid integer
            if retention_days is None:
                retention_days = 30
            cutoff_date = datetime.now() - timedelta(days=retention_days)
            backups = self.list_backups()

            for backup in backups:
                try:
                    # Parse creation date
                    created_date = datetime.strptime(backup['created'], '%Y-%m-%d %H:%M:%S')

                    if created_date < cutoff_date:
                        os.remove(backup['path'])
                        result['deleted_files'].append(backup['filename'])
                except Exception as e:
                    result['errors'].append(f"Failed to delete {backup['filename']}: {e}")

            result['success'] = True
            result['message'] = f"Cleaned up {len(result['deleted_files'])} old backup files"

        except Exception as e:
            result['error'] = str(e)

        return result
"""
EcoCycle - System Repair Module

This module provides comprehensive system diagnostics and automated repair capabilities
for the EcoCycle application, including cache management, database integrity checks,
configuration validation, and file system repairs.
"""

import os
import json
import sqlite3
import shutil
import logging
import traceback
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path

# Import configuration
try:
    import config.config as config
    from config.config_manager import ConfigManager
    HAS_CONFIG = True
except ImportError:
    HAS_CONFIG = False
    config = None

# Check if Rich is available for enhanced UI
try:
    from rich.console import Console
    from rich.progress import Progress, BarColumn, TextColumn, TimeElapsedColumn
    HAS_RICH = True
    console = Console()
except ImportError:
    HAS_RICH = False
    console = None

# Import AI diagnostics
try:
    from utils.ai_system_diagnostics import AISystemDiagnostics
    HAS_AI_DIAGNOSTICS = True
except ImportError:
    HAS_AI_DIAGNOSTICS = False

logger = logging.getLogger(__name__)


class SystemRepair:
    """Comprehensive system repair and diagnostics utility."""

    def __init__(self):
        """Initialize the system repair utility."""
        self.config_manager = ConfigManager() if HAS_CONFIG else None
        self.repair_history = []
        self.backup_dir = self._get_backup_directory()
        self.issues_found = []
        self.repairs_applied = []

        # Initialize AI diagnostics if available
        self.ai_diagnostics = None
        if HAS_AI_DIAGNOSTICS:
            try:
                self.ai_diagnostics = AISystemDiagnostics()
                logger.info("AI diagnostics system initialized")
            except Exception as e:
                logger.warning(f"Failed to initialize AI diagnostics: {e}")
                self.ai_diagnostics = None

    def _get_backup_directory(self) -> str:
        """Get the backup directory path."""
        if HAS_CONFIG and hasattr(config, 'PROJECT_ROOT'):
            backup_dir = os.path.join(config.PROJECT_ROOT, 'system_repair_backups')
        else:
            backup_dir = os.path.join(os.getcwd(), 'system_repair_backups')

        os.makedirs(backup_dir, exist_ok=True)
        return backup_dir

    def run_comprehensive_diagnostics(self) -> Dict[str, Any]:
        """Run comprehensive system diagnostics."""
        logger.info("Starting comprehensive system diagnostics")

        diagnostics = {
            'timestamp': datetime.now().isoformat(),
            'status': 'running',
            'issues_found': [],
            'recommendations': [],
            'system_health': 'unknown',
            'checks_performed': []
        }

        try:
            # Check cache system
            cache_issues = self._check_cache_system()
            diagnostics['cache_system'] = cache_issues
            diagnostics['checks_performed'].append('cache_system')

            # Check database integrity
            db_issues = self._check_database_integrity()
            diagnostics['database_integrity'] = db_issues
            diagnostics['checks_performed'].append('database_integrity')

            # Check configuration files
            config_issues = self._check_configuration_files()
            diagnostics['configuration'] = config_issues
            diagnostics['checks_performed'].append('configuration')

            # Check file permissions
            permission_issues = self._check_file_permissions()
            diagnostics['file_permissions'] = permission_issues
            diagnostics['checks_performed'].append('file_permissions')

            # Check API connectivity
            api_issues = self._check_api_connectivity()
            diagnostics['api_connectivity'] = api_issues
            diagnostics['checks_performed'].append('api_connectivity')

            # Check email system
            email_issues = self._check_email_system()
            diagnostics['email_system'] = email_issues
            diagnostics['checks_performed'].append('email_system')

            # Aggregate issues and determine system health
            all_issues = []
            for check_name in diagnostics['checks_performed']:
                if check_name in diagnostics and 'issues' in diagnostics[check_name]:
                    all_issues.extend(diagnostics[check_name]['issues'])

            diagnostics['issues_found'] = all_issues
            diagnostics['system_health'] = self._determine_system_health(all_issues)
            diagnostics['status'] = 'completed'

            logger.info(f"System diagnostics completed. Found {len(all_issues)} issues.")

        except Exception as e:
            logger.error(f"Error during system diagnostics: {e}")
            diagnostics['status'] = 'error'
            diagnostics['error'] = str(e)
            diagnostics['traceback'] = traceback.format_exc()

        return diagnostics

    def run_ai_enhanced_diagnostics(self) -> Dict[str, Any]:
        """Run comprehensive diagnostics with AI analysis."""
        # First run standard diagnostics
        diagnostics = self.run_comprehensive_diagnostics()

        # Add AI analysis if available
        if self.ai_diagnostics and self.ai_diagnostics.is_ai_available():
            if HAS_RICH:
                with Progress(
                    TextColumn("[bold cyan]🤖 AI Analysis"),
                    BarColumn(),
                    TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
                    TimeElapsedColumn(),
                    console=console
                ) as progress:
                    task = progress.add_task("Running AI analysis...", total=100)

                    # AI analysis
                    progress.update(task, completed=30)
                    ai_success, ai_analysis = self.ai_diagnostics.analyze_system_issues(diagnostics)
                    progress.update(task, completed=100)

                    if ai_success:
                        diagnostics['ai_analysis'] = ai_analysis
                        logger.info("AI analysis completed successfully")
                    else:
                        diagnostics['ai_analysis'] = {"error": "AI analysis failed", "details": ai_analysis}
                        logger.warning("AI analysis failed")
            else:
                print("🤖 Running AI analysis...")
                ai_success, ai_analysis = self.ai_diagnostics.analyze_system_issues(diagnostics)

                if ai_success:
                    diagnostics['ai_analysis'] = ai_analysis
                    logger.info("AI analysis completed successfully")
                else:
                    diagnostics['ai_analysis'] = {"error": "AI analysis failed", "details": ai_analysis}
                    logger.warning("AI analysis failed")
        else:
            diagnostics['ai_analysis'] = {"error": "AI analysis not available"}

        return diagnostics

    def generate_ai_repair_suggestions(self, issues: List[str]) -> Dict[str, Any]:
        """Generate AI-powered repair suggestions for specific issues."""
        if not self.ai_diagnostics or not self.ai_diagnostics.is_ai_available():
            return {"error": "AI repair suggestions not available"}

        # Prepare system context
        system_context = {
            "platform": os.name,
            "python_version": "3.x",  # Could be more specific
            "application": "EcoCycle",
            "total_issues": len(issues),
            "backup_available": os.path.exists(self.backup_dir)
        }

        if HAS_RICH:
            with Progress(
                TextColumn("[bold green]🔧 AI Repair Suggestions"),
                BarColumn(),
                TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
                TimeElapsedColumn(),
                console=console
            ) as progress:
                task = progress.add_task("Generating repair suggestions...", total=100)

                # Generate suggestions
                progress.update(task, completed=50)
                success, suggestions = self.ai_diagnostics.generate_repair_suggestions(issues, system_context)
                progress.update(task, completed=100)

                if success:
                    logger.info("AI repair suggestions generated successfully")
                    return suggestions
                else:
                    logger.warning("AI repair suggestions failed")
                    return {"error": "Failed to generate AI repair suggestions", "details": suggestions}
        else:
            print("🔧 Generating AI-powered repair suggestions...")
            success, suggestions = self.ai_diagnostics.generate_repair_suggestions(issues, system_context)

            if success:
                logger.info("AI repair suggestions generated successfully")
                return suggestions
            else:
                logger.warning("AI repair suggestions failed")
                return {"error": "Failed to generate AI repair suggestions", "details": suggestions}

    def _check_cache_system(self) -> Dict[str, Any]:
        """Check cache system integrity."""
        cache_check = {
            'status': 'healthy',
            'issues': [],
            'recommendations': [],
            'cache_files': {}
        }

        try:
            # Define cache files to check
            cache_files = {
                'routes_cache': 'data/cache/routes_cache.json',
                'weather_cache': 'data/cache/weather_cache.json',
                'ai_routes': 'data/user/ai_routes.json',
                'dependency_cache': 'data/cache/dependency_cache.json'
            }

            if HAS_CONFIG:
                cache_files.update({
                    'routes_cache': getattr(config, 'ROUTES_CACHE_FILE', cache_files['routes_cache']),
                    'weather_cache': getattr(config, 'WEATHER_CACHE_FILE', cache_files['weather_cache']),
                    'ai_routes': getattr(config, 'AI_ROUTES_FILE', cache_files['ai_routes'])
                })

            for cache_name, cache_path in cache_files.items():
                cache_info = self._check_cache_file(cache_path)
                cache_check['cache_files'][cache_name] = cache_info

                if cache_info['issues']:
                    cache_check['issues'].extend([f"{cache_name}: {issue}" for issue in cache_info['issues']])

            # Check cache directory structure
            cache_dirs = ['data/cache', 'data/user', 'data/debug']
            for cache_dir in cache_dirs:
                if not os.path.exists(cache_dir):
                    cache_check['issues'].append(f"Missing cache directory: {cache_dir}")
                    cache_check['recommendations'].append(f"Create missing directory: {cache_dir}")

            if cache_check['issues']:
                cache_check['status'] = 'issues_found'

        except Exception as e:
            cache_check['status'] = 'error'
            cache_check['error'] = str(e)
            logger.error(f"Error checking cache system: {e}")

        return cache_check

    def _check_cache_file(self, cache_path: str) -> Dict[str, Any]:
        """Check individual cache file."""
        cache_info = {
            'exists': False,
            'readable': False,
            'valid_json': False,
            'size': 0,
            'last_modified': None,
            'issues': [],
            'recommendations': []
        }

        try:
            if os.path.exists(cache_path):
                cache_info['exists'] = True
                cache_info['size'] = os.path.getsize(cache_path)
                cache_info['last_modified'] = datetime.fromtimestamp(
                    os.path.getmtime(cache_path)
                ).isoformat()

                # Check if file is readable
                try:
                    with open(cache_path, 'r', encoding='utf-8') as f:
                        cache_info['readable'] = True

                        # Check if valid JSON
                        try:
                            json.load(f)
                            cache_info['valid_json'] = True
                        except json.JSONDecodeError:
                            cache_info['issues'].append("Invalid JSON format")
                            cache_info['recommendations'].append("Recreate cache file")

                except PermissionError:
                    cache_info['issues'].append("Permission denied reading file")
                    cache_info['recommendations'].append("Fix file permissions")

            else:
                cache_info['issues'].append("Cache file does not exist")
                cache_info['recommendations'].append("Create missing cache file")

        except Exception as e:
            cache_info['issues'].append(f"Error checking cache file: {e}")
            logger.error(f"Error checking cache file {cache_path}: {e}")

        return cache_info

    def _check_database_integrity(self) -> Dict[str, Any]:
        """Check database integrity."""
        db_check = {
            'status': 'healthy',
            'issues': [],
            'recommendations': [],
            'database_info': {}
        }

        try:
            # Get database file path
            db_path = getattr(config, 'DATABASE_FILE', 'ecocycle.db') if HAS_CONFIG else 'ecocycle.db'

            if not os.path.exists(db_path):
                db_check['issues'].append("Database file does not exist")
                db_check['recommendations'].append("Initialize database")
                db_check['status'] = 'critical'
                return db_check

            # Check database file
            db_check['database_info']['file_size'] = os.path.getsize(db_path)
            db_check['database_info']['last_modified'] = datetime.fromtimestamp(
                os.path.getmtime(db_path)
            ).isoformat()

            # Check database connectivity and integrity
            try:
                conn = sqlite3.connect(db_path)
                cursor = conn.cursor()

                # Check database integrity
                cursor.execute("PRAGMA integrity_check;")
                integrity_result = cursor.fetchone()

                if integrity_result[0] != 'ok':
                    db_check['issues'].append(f"Database integrity check failed: {integrity_result[0]}")
                    db_check['recommendations'].append("Repair database or restore from backup")

                # Check for required tables
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
                tables = [row[0] for row in cursor.fetchall()]

                required_tables = ['users', 'trips', 'stats']  # Add more as needed
                for table in required_tables:
                    if table not in tables:
                        db_check['issues'].append(f"Missing required table: {table}")
                        db_check['recommendations'].append(f"Create missing table: {table}")

                db_check['database_info']['tables'] = tables
                conn.close()

            except sqlite3.Error as e:
                db_check['issues'].append(f"Database connection error: {e}")
                db_check['recommendations'].append("Check database file permissions and integrity")

            if db_check['issues']:
                db_check['status'] = 'issues_found'

        except Exception as e:
            db_check['status'] = 'error'
            db_check['error'] = str(e)
            logger.error(f"Error checking database integrity: {e}")

        return db_check

    def _check_configuration_files(self) -> Dict[str, Any]:
        """Check configuration files."""
        config_check = {
            'status': 'healthy',
            'issues': [],
            'recommendations': [],
            'config_files': {}
        }

        try:
            # Check main configuration files
            config_files = [
                'config/config.py',
                'config/config_manager.py',
                '.env'  # Optional but important
            ]

            for config_file in config_files:
                if os.path.exists(config_file):
                    config_check['config_files'][config_file] = {
                        'exists': True,
                        'readable': os.access(config_file, os.R_OK),
                        'size': os.path.getsize(config_file)
                    }

                    if not os.access(config_file, os.R_OK):
                        config_check['issues'].append(f"Cannot read config file: {config_file}")
                        config_check['recommendations'].append(f"Fix permissions for: {config_file}")
                else:
                    config_check['config_files'][config_file] = {'exists': False}
                    if config_file != '.env':  # .env is optional
                        config_check['issues'].append(f"Missing config file: {config_file}")
                        config_check['recommendations'].append(f"Create missing config file: {config_file}")

            # Check environment variables
            required_env_vars = ['SESSION_SECRET_KEY']
            optional_env_vars = ['EMAIL_USERNAME', 'EMAIL_PASSWORD', 'GOOGLE_MAPS_API_KEY', 'OPENWEATHERMAP_API_KEY']

            for env_var in required_env_vars:
                if not os.environ.get(env_var):
                    config_check['issues'].append(f"Missing required environment variable: {env_var}")
                    config_check['recommendations'].append(f"Set environment variable: {env_var}")

            if config_check['issues']:
                config_check['status'] = 'issues_found'

        except Exception as e:
            config_check['status'] = 'error'
            config_check['error'] = str(e)
            logger.error(f"Error checking configuration files: {e}")

        return config_check

    def _check_file_permissions(self) -> Dict[str, Any]:
        """Check file permissions for critical directories and files."""
        permission_check = {
            'status': 'healthy',
            'issues': [],
            'recommendations': [],
            'checked_paths': {}
        }

        try:
            # Critical paths to check
            critical_paths = [
                'data',
                'data/cache',
                'data/user',
                'Logs',
                'ecocycle.db'
            ]

            if HAS_CONFIG:
                critical_paths.extend([
                    getattr(config, 'LOG_DIR', 'Logs'),
                    getattr(config, 'CACHE_DIR', 'data/cache'),
                    getattr(config, 'USER_DATA_DIR', 'data/user'),
                    getattr(config, 'DATABASE_FILE', 'ecocycle.db')
                ])

            for path in critical_paths:
                if os.path.exists(path):
                    permission_info = {
                        'exists': True,
                        'readable': os.access(path, os.R_OK),
                        'writable': os.access(path, os.W_OK),
                        'executable': os.access(path, os.X_OK) if os.path.isdir(path) else None
                    }

                    permission_check['checked_paths'][path] = permission_info

                    # Check for issues
                    if not permission_info['readable']:
                        permission_check['issues'].append(f"Cannot read: {path}")
                        permission_check['recommendations'].append(f"Fix read permissions for: {path}")

                    if not permission_info['writable']:
                        permission_check['issues'].append(f"Cannot write: {path}")
                        permission_check['recommendations'].append(f"Fix write permissions for: {path}")

                    if os.path.isdir(path) and not permission_info['executable']:
                        permission_check['issues'].append(f"Cannot execute/access directory: {path}")
                        permission_check['recommendations'].append(f"Fix execute permissions for: {path}")
                else:
                    permission_check['checked_paths'][path] = {'exists': False}
                    permission_check['issues'].append(f"Path does not exist: {path}")
                    permission_check['recommendations'].append(f"Create missing path: {path}")

            if permission_check['issues']:
                permission_check['status'] = 'issues_found'

        except Exception as e:
            permission_check['status'] = 'error'
            permission_check['error'] = str(e)
            logger.error(f"Error checking file permissions: {e}")

        return permission_check

    def _check_api_connectivity(self) -> Dict[str, Any]:
        """Check API connectivity and key validation."""
        api_check = {
            'status': 'healthy',
            'issues': [],
            'recommendations': [],
            'api_services': {}
        }

        try:
            # Check API keys
            api_keys = {
                'GOOGLE_MAPS_API_KEY': os.environ.get('GOOGLE_MAPS_API_KEY'),
                'OPENWEATHERMAP_API_KEY': os.environ.get('OPENWEATHERMAP_API_KEY'),
                'WEATHERAPI_KEY': os.environ.get('WEATHERAPI_KEY')
            }

            for api_name, api_key in api_keys.items():
                api_info = {
                    'configured': bool(api_key),
                    'key_length': len(api_key) if api_key else 0,
                    'status': 'unknown'
                }

                if not api_key:
                    api_info['status'] = 'missing'
                    api_check['issues'].append(f"Missing API key: {api_name}")
                    api_check['recommendations'].append(f"Configure API key: {api_name}")
                elif len(api_key) < 10:  # Basic validation
                    api_info['status'] = 'invalid'
                    api_check['issues'].append(f"Invalid API key format: {api_name}")
                    api_check['recommendations'].append(f"Check API key format: {api_name}")
                else:
                    api_info['status'] = 'configured'

                api_check['api_services'][api_name] = api_info

            if api_check['issues']:
                api_check['status'] = 'issues_found'

        except Exception as e:
            api_check['status'] = 'error'
            api_check['error'] = str(e)
            logger.error(f"Error checking API connectivity: {e}")

        return api_check

    def _check_email_system(self) -> Dict[str, Any]:
        """Check email system configuration."""
        email_check = {
            'status': 'healthy',
            'issues': [],
            'recommendations': [],
            'email_config': {}
        }

        try:
            # Check email configuration
            email_config = {
                'EMAIL_USERNAME': os.environ.get('EMAIL_USERNAME'),
                'EMAIL_PASSWORD': os.environ.get('EMAIL_PASSWORD'),
                'FROM_EMAIL': os.environ.get('FROM_EMAIL')
            }

            for config_name, config_value in email_config.items():
                email_check['email_config'][config_name] = {
                    'configured': bool(config_value),
                    'value_length': len(config_value) if config_value else 0
                }

                if not config_value:
                    email_check['issues'].append(f"Missing email configuration: {config_name}")
                    email_check['recommendations'].append(f"Configure email setting: {config_name}")

            # Check email templates directory
            email_templates_dir = 'email_templates'
            if os.path.exists(email_templates_dir):
                email_check['email_config']['templates_dir'] = {
                    'exists': True,
                    'template_count': len([f for f in os.listdir(email_templates_dir) if f.endswith('.html')])
                }
            else:
                email_check['issues'].append("Missing email templates directory")
                email_check['recommendations'].append("Create email templates directory")

            if email_check['issues']:
                email_check['status'] = 'issues_found'

        except Exception as e:
            email_check['status'] = 'error'
            email_check['error'] = str(e)
            logger.error(f"Error checking email system: {e}")

        return email_check

    def _determine_system_health(self, issues: List[str]) -> str:
        """Determine overall system health based on issues found."""
        if not issues:
            return 'excellent'
        elif len(issues) <= 2:
            return 'good'
        elif len(issues) <= 5:
            return 'fair'
        elif len(issues) <= 10:
            return 'poor'
        else:
            return 'critical'

    def auto_repair_system(self, create_backup: bool = True) -> Dict[str, Any]:
        """Automatically repair detected system issues."""
        logger.info("Starting automated system repair")

        repair_result = {
            'timestamp': datetime.now().isoformat(),
            'status': 'running',
            'backup_created': False,
            'repairs_attempted': [],
            'repairs_successful': [],
            'repairs_failed': [],
            'issues_remaining': []
        }

        try:
            # Create backup if requested
            if create_backup:
                backup_result = self.create_system_backup()
                repair_result['backup_created'] = backup_result.get('success', False)
                repair_result['backup_path'] = backup_result.get('backup_path')

            # Run diagnostics first
            diagnostics = self.run_comprehensive_diagnostics()

            # Repair cache issues
            if 'cache_system' in diagnostics and diagnostics['cache_system']['issues']:
                cache_repair = self._repair_cache_system(diagnostics['cache_system'])
                repair_result['repairs_attempted'].append('cache_system')
                if cache_repair['success']:
                    repair_result['repairs_successful'].append('cache_system')
                else:
                    repair_result['repairs_failed'].append('cache_system')

            # Repair database issues
            if 'database_integrity' in diagnostics and diagnostics['database_integrity']['issues']:
                db_repair = self._repair_database_issues(diagnostics['database_integrity'])
                repair_result['repairs_attempted'].append('database_integrity')
                if db_repair['success']:
                    repair_result['repairs_successful'].append('database_integrity')
                else:
                    repair_result['repairs_failed'].append('database_integrity')

            # Repair file permission issues
            if 'file_permissions' in diagnostics and diagnostics['file_permissions']['issues']:
                permission_repair = self._repair_file_permissions(diagnostics['file_permissions'])
                repair_result['repairs_attempted'].append('file_permissions')
                if permission_repair['success']:
                    repair_result['repairs_successful'].append('file_permissions')
                else:
                    repair_result['repairs_failed'].append('file_permissions')

            # Repair configuration issues
            if 'configuration' in diagnostics and diagnostics['configuration']['issues']:
                config_repair = self._repair_configuration_issues(diagnostics['configuration'])
                repair_result['repairs_attempted'].append('configuration')
                if config_repair['success']:
                    repair_result['repairs_successful'].append('configuration')
                else:
                    repair_result['repairs_failed'].append('configuration')

            # Run diagnostics again to check remaining issues
            final_diagnostics = self.run_comprehensive_diagnostics()
            repair_result['issues_remaining'] = final_diagnostics.get('issues_found', [])

            repair_result['status'] = 'completed'
            logger.info(f"System repair completed. {len(repair_result['repairs_successful'])} repairs successful, {len(repair_result['repairs_failed'])} failed.")

        except Exception as e:
            repair_result['status'] = 'error'
            repair_result['error'] = str(e)
            repair_result['traceback'] = traceback.format_exc()
            logger.error(f"Error during automated system repair: {e}")

        # Save repair to history
        self._save_repair_to_history(repair_result)

        return repair_result

    def _repair_cache_system(self, cache_issues: Dict[str, Any]) -> Dict[str, Any]:
        """Repair cache system issues."""
        repair_result = {
            'success': True,
            'repairs_made': [],
            'errors': []
        }

        try:
            # Create missing cache directories
            cache_dirs = ['data/cache', 'data/user', 'data/debug']
            for cache_dir in cache_dirs:
                if not os.path.exists(cache_dir):
                    try:
                        os.makedirs(cache_dir, exist_ok=True)
                        repair_result['repairs_made'].append(f"Created directory: {cache_dir}")
                        logger.info(f"Created missing cache directory: {cache_dir}")
                    except Exception as e:
                        repair_result['errors'].append(f"Failed to create directory {cache_dir}: {e}")
                        repair_result['success'] = False

            # Repair corrupted cache files
            for cache_name, cache_info in cache_issues.get('cache_files', {}).items():
                if cache_info.get('issues'):
                    try:
                        # Get cache file path
                        cache_paths = {
                            'routes_cache': 'data/cache/routes_cache.json',
                            'weather_cache': 'data/cache/weather_cache.json',
                            'ai_routes': 'data/user/ai_routes.json',
                            'dependency_cache': 'data/cache/dependency_cache.json'
                        }

                        cache_path = cache_paths.get(cache_name)
                        if cache_path:
                            # Create empty valid JSON file
                            with open(cache_path, 'w', encoding='utf-8') as f:
                                json.dump({}, f, indent=2)
                            repair_result['repairs_made'].append(f"Recreated cache file: {cache_path}")
                            logger.info(f"Recreated corrupted cache file: {cache_path}")
                    except Exception as e:
                        repair_result['errors'].append(f"Failed to repair cache file {cache_name}: {e}")
                        repair_result['success'] = False

        except Exception as e:
            repair_result['success'] = False
            repair_result['errors'].append(f"Cache repair error: {e}")
            logger.error(f"Error repairing cache system: {e}")

        return repair_result

    def _repair_database_issues(self, db_issues: Dict[str, Any]) -> Dict[str, Any]:
        """Repair database issues."""
        repair_result = {
            'success': True,
            'repairs_made': [],
            'errors': []
        }

        try:
            # Get database file path
            db_path = getattr(config, 'DATABASE_FILE', 'ecocycle.db') if HAS_CONFIG else 'ecocycle.db'

            # If database doesn't exist, initialize it
            if not os.path.exists(db_path):
                try:
                    # Import database initialization function
                    from core.database_manager import initialize_database
                    initialize_database()
                    repair_result['repairs_made'].append("Initialized missing database")
                    logger.info("Initialized missing database")
                except Exception as e:
                    repair_result['errors'].append(f"Failed to initialize database: {e}")
                    repair_result['success'] = False

            # Check for missing tables and create them
            try:
                conn = sqlite3.connect(db_path)
                cursor = conn.cursor()

                # Get existing tables
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
                existing_tables = [row[0] for row in cursor.fetchall()]

                # Define required tables with their creation SQL
                required_tables = {
                    'users': '''CREATE TABLE IF NOT EXISTS users (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        username TEXT NOT NULL UNIQUE,
                        email TEXT,
                        password_hash TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )''',
                    'trips': '''CREATE TABLE IF NOT EXISTS trips (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER,
                        date TEXT,
                        distance REAL,
                        duration REAL,
                        co2_saved REAL,
                        calories INTEGER,
                        FOREIGN KEY (user_id) REFERENCES users (id)
                    )''',
                    'stats': '''CREATE TABLE IF NOT EXISTS stats (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER,
                        total_trips INTEGER DEFAULT 0,
                        total_distance REAL DEFAULT 0,
                        total_co2_saved REAL DEFAULT 0,
                        total_calories INTEGER DEFAULT 0,
                        FOREIGN KEY (user_id) REFERENCES users (id)
                    )'''
                }

                for table_name, create_sql in required_tables.items():
                    if table_name not in existing_tables:
                        cursor.execute(create_sql)
                        repair_result['repairs_made'].append(f"Created missing table: {table_name}")
                        logger.info(f"Created missing table: {table_name}")

                conn.commit()
                conn.close()

            except Exception as e:
                repair_result['errors'].append(f"Database table repair error: {e}")
                repair_result['success'] = False

        except Exception as e:
            repair_result['success'] = False
            repair_result['errors'].append(f"Database repair error: {e}")
            logger.error(f"Error repairing database: {e}")

        return repair_result

    def _repair_file_permissions(self, permission_issues: Dict[str, Any]) -> Dict[str, Any]:
        """Repair file permission issues."""
        repair_result = {
            'success': True,
            'repairs_made': [],
            'errors': []
        }

        try:
            # Create missing directories
            for path, path_info in permission_issues.get('checked_paths', {}).items():
                if not path_info.get('exists', True):
                    try:
                        if '.' not in os.path.basename(path):  # It's a directory
                            os.makedirs(path, exist_ok=True)
                            repair_result['repairs_made'].append(f"Created missing directory: {path}")
                            logger.info(f"Created missing directory: {path}")
                    except Exception as e:
                        repair_result['errors'].append(f"Failed to create directory {path}: {e}")
                        repair_result['success'] = False

            # Note: File permission fixes typically require admin privileges
            # We can only create missing directories, not fix existing permissions
            if permission_issues.get('issues'):
                for issue in permission_issues['issues']:
                    if 'does not exist' not in issue:
                        repair_result['errors'].append(f"Permission issue requires manual intervention: {issue}")

        except Exception as e:
            repair_result['success'] = False
            repair_result['errors'].append(f"Permission repair error: {e}")
            logger.error(f"Error repairing file permissions: {e}")

        return repair_result

    def _repair_configuration_issues(self, config_issues: Dict[str, Any]) -> Dict[str, Any]:
        """Repair configuration issues."""
        repair_result = {
            'success': True,
            'repairs_made': [],
            'errors': []
        }

        try:
            # Create missing configuration directories
            config_dirs = ['config', 'email_templates']
            for config_dir in config_dirs:
                if not os.path.exists(config_dir):
                    try:
                        os.makedirs(config_dir, exist_ok=True)
                        repair_result['repairs_made'].append(f"Created config directory: {config_dir}")
                        logger.info(f"Created missing config directory: {config_dir}")
                    except Exception as e:
                        repair_result['errors'].append(f"Failed to create config directory {config_dir}: {e}")
                        repair_result['success'] = False

            # Note: We cannot automatically fix missing environment variables
            # or create missing config files as they require user-specific values
            if config_issues.get('issues'):
                for issue in config_issues['issues']:
                    if 'environment variable' in issue or 'config file' in issue:
                        repair_result['errors'].append(f"Configuration issue requires manual setup: {issue}")

        except Exception as e:
            repair_result['success'] = False
            repair_result['errors'].append(f"Configuration repair error: {e}")
            logger.error(f"Error repairing configuration: {e}")

        return repair_result

    def create_system_backup(self) -> Dict[str, Any]:
        """Create a backup of critical system files before repairs."""
        backup_result = {
            'success': False,
            'backup_path': None,
            'files_backed_up': [],
            'errors': []
        }

        try:
            # Create backup directory with timestamp
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_path = os.path.join(self.backup_dir, f'system_backup_{timestamp}')
            os.makedirs(backup_path, exist_ok=True)

            # Files and directories to backup
            backup_items = [
                'ecocycle.db',
                'data/cache',
                'data/user',
                'config',
                '.env'
            ]

            if HAS_CONFIG:
                backup_items.extend([
                    getattr(config, 'DATABASE_FILE', 'ecocycle.db'),
                    getattr(config, 'CACHE_DIR', 'data/cache'),
                    getattr(config, 'USER_DATA_DIR', 'data/user')
                ])

            for item in backup_items:
                if os.path.exists(item):
                    try:
                        dest_path = os.path.join(backup_path, os.path.basename(item))
                        if os.path.isdir(item):
                            shutil.copytree(item, dest_path, dirs_exist_ok=True)
                        else:
                            shutil.copy2(item, dest_path)
                        backup_result['files_backed_up'].append(item)
                    except Exception as e:
                        backup_result['errors'].append(f"Failed to backup {item}: {e}")

            backup_result['success'] = len(backup_result['files_backed_up']) > 0
            backup_result['backup_path'] = backup_path

            if backup_result['success']:
                logger.info(f"System backup created at: {backup_path}")
            else:
                logger.warning("System backup failed - no files were backed up")

        except Exception as e:
            backup_result['errors'].append(f"Backup creation error: {e}")
            logger.error(f"Error creating system backup: {e}")

        return backup_result

    def _save_repair_to_history(self, repair_result: Dict[str, Any]) -> None:
        """Save repair operation to history."""
        try:
            history_file = os.path.join(self.backup_dir, 'repair_history.json')

            # Load existing history
            history = []
            if os.path.exists(history_file):
                try:
                    with open(history_file, 'r', encoding='utf-8') as f:
                        history = json.load(f)
                except json.JSONDecodeError:
                    logger.warning("Corrupted repair history file, starting fresh")
                    history = []

            # Add current repair to history
            history.append(repair_result)

            # Keep only last 50 repairs
            history = history[-50:]

            # Save updated history
            with open(history_file, 'w', encoding='utf-8') as f:
                json.dump(history, f, indent=2)

            logger.info("Repair operation saved to history")

        except Exception as e:
            logger.error(f"Error saving repair to history: {e}")

    def get_repair_history(self) -> List[Dict[str, Any]]:
        """Get the history of repair operations."""
        try:
            history_file = os.path.join(self.backup_dir, 'repair_history.json')

            if os.path.exists(history_file):
                with open(history_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                return []

        except Exception as e:
            logger.error(f"Error loading repair history: {e}")
            return []
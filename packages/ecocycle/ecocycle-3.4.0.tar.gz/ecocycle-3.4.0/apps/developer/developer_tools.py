"""
EcoCycle - Developer Tools Module
Provides advanced debugging and system management tools for developers.
"""
import os
import sys
import json
import sqlite3
import logging
import traceback
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, Union
import subprocess

try:
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich.tree import Tree
    from rich.syntax import Syntax
    from rich.progress import Progress, SpinnerColumn, TextColumn
    HAS_RICH = True
    console = Console()
except ImportError:
    HAS_RICH = False
    console = None

# Import EcoCycle modules
try:
    import config.config as config
    DATABASE_FILE = getattr(config, 'DATABASE_FILE', 'ecocycle.db')
except ImportError as e:
    print(f"Warning: Could not import config module: {e}")
    DATABASE_FILE = 'ecocycle.db'

try:
    import core.database_manager as database_manager
except ImportError as e:
    print(f"Warning: Could not import database_manager: {e}")
    database_manager = None

try:
    from auth.developer_auth import DeveloperAuth
except ImportError as e:
    print(f"Warning: Could not import DeveloperAuth: {e}")
    DeveloperAuth = None


logger = logging.getLogger(__name__)


class DeveloperTools:
    """Advanced developer tools for debugging and system management."""

    def __init__(self, developer_auth, config_manager=None):
        """Initialize developer tools."""
        self.developer_auth = developer_auth
        self.config_manager = config_manager
        self.logger = logger

    def system_diagnostics(self) -> Dict[str, Any]:
        """Run comprehensive system diagnostics."""
        if not self.developer_auth.is_developer_authenticated():
            raise PermissionError("Developer authentication required")

        self.developer_auth.log_action("SYSTEM_DIAGNOSTICS", "Running system diagnostics")

        diagnostics = {
            'timestamp': datetime.now().isoformat(),
            'python_version': sys.version,
            'platform': sys.platform,
            'working_directory': os.getcwd(),
            'environment_variables': {},
            'database_status': {},
            'file_system': {},
            'dependencies': {},
            'memory_usage': {},
            'log_files': {}
        }

        # Environment variables (filter sensitive ones)
        sensitive_keys = ['PASSWORD', 'SECRET', 'KEY', 'TOKEN', 'API']
        for key, value in os.environ.items():
            if any(sensitive in key.upper() for sensitive in sensitive_keys):
                diagnostics['environment_variables'][key] = '***HIDDEN***'
            else:
                diagnostics['environment_variables'][key] = value

        # Database status
        try:
            if os.path.exists(DATABASE_FILE):
                conn = sqlite3.connect(DATABASE_FILE)
                cursor = conn.cursor()

                # Get table information
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
                tables = [row[0] for row in cursor.fetchall()]

                diagnostics['database_status']['file_exists'] = True
                diagnostics['database_status']['file_size'] = os.path.getsize(DATABASE_FILE)
                diagnostics['database_status']['tables'] = tables

                # Get row counts for each table
                table_counts = {}
                for table in tables:
                    try:
                        cursor.execute(f"SELECT COUNT(*) FROM {table}")
                        table_counts[table] = cursor.fetchone()[0]
                    except Exception as e:
                        table_counts[table] = f"Error: {e}"

                diagnostics['database_status']['table_counts'] = table_counts
                conn.close()
            else:
                diagnostics['database_status']['file_exists'] = False
        except Exception as e:
            diagnostics['database_status']['error'] = str(e)

        # File system checks
        important_paths = [
            'data', 'Logs', 'config', 'auth', 'apps', 'core',
            'data/user', 'data/cache', 'email_templates'
        ]

        for path in important_paths:
            full_path = os.path.join(os.getcwd(), path)
            diagnostics['file_system'][path] = {
                'exists': os.path.exists(full_path),
                'is_directory': os.path.isdir(full_path),
                'permissions': oct(os.stat(full_path).st_mode)[-3:] if os.path.exists(full_path) else None
            }

            if os.path.exists(full_path) and os.path.isdir(full_path):
                try:
                    file_count = len([f for f in os.listdir(full_path)
                                    if os.path.isfile(os.path.join(full_path, f))])
                    diagnostics['file_system'][path]['file_count'] = file_count
                except PermissionError:
                    diagnostics['file_system'][path]['file_count'] = 'Permission denied'

        # Check critical files
        critical_files = [
            'main.py', 'config/config.py', 'ecocycle.db',
            'data/user/users.json', 'data/user/session.json'
        ]

        for file_path in critical_files:
            full_path = os.path.join(os.getcwd(), file_path)
            diagnostics['file_system'][f'file_{file_path}'] = {
                'exists': os.path.exists(full_path),
                'size': os.path.getsize(full_path) if os.path.exists(full_path) else 0,
                'modified': datetime.fromtimestamp(os.path.getmtime(full_path)).isoformat()
                           if os.path.exists(full_path) else None
            }

        # Log file analysis
        log_dir = os.path.join(os.getcwd(), 'Logs')
        if os.path.exists(log_dir):
            for log_file in os.listdir(log_dir):
                if log_file.endswith('.log'):
                    log_path = os.path.join(log_dir, log_file)
                    try:
                        with open(log_path, 'r', encoding='utf-8') as f:
                            lines = f.readlines()
                            diagnostics['log_files'][log_file] = {
                                'size': os.path.getsize(log_path),
                                'line_count': len(lines),
                                'last_modified': datetime.fromtimestamp(os.path.getmtime(log_path)).isoformat(),
                                'recent_errors': [line.strip() for line in lines[-50:]
                                                if 'ERROR' in line.upper()][-10:]  # Last 10 errors
                            }
                    except Exception as e:
                        diagnostics['log_files'][log_file] = {'error': str(e)}

        return diagnostics

    def view_database_contents(self, table_name: Optional[str] = None, limit: int = 100) -> Dict[str, Any]:
        """View database table contents."""
        if not self.developer_auth.is_developer_authenticated():
            raise PermissionError("Developer authentication required")

        self.developer_auth.log_action("DATABASE_VIEW", f"Viewing database table: {table_name or 'all'}")

        try:
            if not os.path.exists(DATABASE_FILE):
                return {'error': 'Database file not found'}

            conn = sqlite3.connect(DATABASE_FILE)
            cursor = conn.cursor()

            result = {}

            if table_name:
                # View specific table
                cursor.execute(f"PRAGMA table_info({table_name})")
                columns = [row[1] for row in cursor.fetchall()]

                cursor.execute(f"SELECT * FROM {table_name} LIMIT {limit}")
                rows = cursor.fetchall()

                result[table_name] = {
                    'columns': columns,
                    'rows': rows,
                    'count': len(rows)
                }
            else:
                # View all tables
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
                tables = [row[0] for row in cursor.fetchall()]

                for table in tables:
                    cursor.execute(f"PRAGMA table_info({table})")
                    columns = [row[1] for row in cursor.fetchall()]

                    cursor.execute(f"SELECT COUNT(*) FROM {table}")
                    total_count = cursor.fetchone()[0]

                    cursor.execute(f"SELECT * FROM {table} LIMIT 5")  # Just first 5 rows for overview
                    rows = cursor.fetchall()

                    result[table] = {
                        'columns': columns,
                        'sample_rows': rows,
                        'total_count': total_count
                    }

            conn.close()
            return result

        except Exception as e:
            return {'error': str(e), 'traceback': traceback.format_exc()}

    def manage_cache(self, action: str = 'view', cache_type: str = 'all') -> Dict[str, Any]:
        """Manage application caches."""
        if not self.developer_auth.is_developer_authenticated():
            raise PermissionError("Developer authentication required")

        self.developer_auth.log_action("CACHE_MANAGEMENT", f"Action: {action}, Type: {cache_type}")

        cache_files = {
            'routes': os.path.join(os.getcwd(), 'data', 'cache', 'routes_cache.json'),
            'weather': os.path.join(os.getcwd(), 'data', 'cache', 'weather_cache.json'),
            'ai_routes': os.path.join(os.getcwd(), 'data', 'user', 'ai_routes.json'),
            'dependency': os.path.join(os.getcwd(), 'data', 'cache', 'dependency_cache.json')
        }

        result = {}

        if action == 'view':
            for cache_name, cache_path in cache_files.items():
                if cache_type != 'all' and cache_name != cache_type:
                    continue

                if os.path.exists(cache_path):
                    try:
                        with open(cache_path, 'r', encoding='utf-8') as f:
                            cache_data = json.load(f)

                        result[cache_name] = {
                            'exists': True,
                            'size': os.path.getsize(cache_path),
                            'modified': datetime.fromtimestamp(os.path.getmtime(cache_path)).isoformat(),
                            'entries': len(cache_data) if isinstance(cache_data, (dict, list)) else 'N/A',
                            'sample_keys': list(cache_data.keys())[:10] if isinstance(cache_data, dict) else 'N/A'
                        }
                    except Exception as e:
                        result[cache_name] = {'exists': True, 'error': str(e)}
                else:
                    result[cache_name] = {'exists': False}

        elif action == 'clear':
            for cache_name, cache_path in cache_files.items():
                if cache_type != 'all' and cache_name != cache_type:
                    continue

                try:
                    if os.path.exists(cache_path):
                        os.remove(cache_path)
                        result[cache_name] = {'cleared': True}
                    else:
                        result[cache_name] = {'cleared': False, 'reason': 'File not found'}
                except Exception as e:
                    result[cache_name] = {'cleared': False, 'error': str(e)}

        return result

    def test_email_system(self, test_email: Optional[str] = None) -> Dict[str, Any]:
        """Test the email verification system."""
        if not self.developer_auth.is_developer_authenticated():
            raise PermissionError("Developer authentication required")

        self.developer_auth.log_action("EMAIL_TEST", f"Testing email system for: {test_email or 'system test'}")

        result = {
            'timestamp': datetime.now().isoformat(),
            'smtp_config': {},
            'template_check': {},
            'test_results': {}
        }

        # Check SMTP configuration
        smtp_vars = ['EMAIL_USERNAME', 'EMAIL_PASSWORD', 'FROM_EMAIL']
        for var in smtp_vars:
            value = os.environ.get(var)
            result['smtp_config'][var] = 'SET' if value else 'NOT SET'

        # Check email templates
        template_dir = os.path.join(os.getcwd(), 'email_templates')
        if os.path.exists(template_dir):
            templates = [f for f in os.listdir(template_dir) if f.endswith(('.txt', '.html'))]
            for template in templates:
                template_path = os.path.join(template_dir, template)
                result['template_check'][template] = {
                    'exists': True,
                    'size': os.path.getsize(template_path)
                }
        else:
            result['template_check']['error'] = 'Template directory not found'

        # If test email provided, attempt to send test email
        if test_email:
            try:
                # Import email verification module
                from auth.email_verification import EmailVerification

                email_verifier = EmailVerification()

                # Generate test verification code
                test_code = email_verifier.generate_verification_code()

                # Attempt to send test email
                success = email_verifier.send_verification_email(test_email, test_code)

                result['test_results']['email_sent'] = success
                result['test_results']['test_code'] = test_code
                result['test_results']['recipient'] = test_email

            except Exception as e:
                result['test_results']['error'] = str(e)
                result['test_results']['traceback'] = traceback.format_exc()

        return result

    def manage_user_data(self, action: str, username: Optional[str] = None, data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Manage user data (view, edit, delete)."""
        if not self.developer_auth.is_developer_authenticated():
            raise PermissionError("Developer authentication required")

        self.developer_auth.log_action("USER_DATA_MANAGEMENT", f"Action: {action}, User: {username}")

        users_file = os.path.join(os.getcwd(), 'data', 'user', 'users.json')

        try:
            # Load current users
            if os.path.exists(users_file):
                with open(users_file, 'r', encoding='utf-8') as f:
                    users = json.load(f)
            else:
                users = {}

            result: Dict[str, Any] = {'action': action, 'timestamp': datetime.now().isoformat()}

            if action == 'list':
                # List all users with basic info
                user_list = []
                for user, user_data in users.items():
                    user_info = {
                        'username': user,
                        'name': user_data.get('name', 'N/A'),
                        'email': user_data.get('email', 'N/A'),
                        'is_admin': user_data.get('is_admin', False),
                        'is_guest': user_data.get('is_guest', False),
                        'total_trips': user_data.get('stats', {}).get('total_trips', 0),
                        'total_distance': user_data.get('stats', {}).get('total_distance', 0)
                    }
                    user_list.append(user_info)

                result['users'] = user_list
                result['total_count'] = len(user_list)

            elif action == 'view' and username:
                # View specific user details
                if username in users:
                    result['user_data'] = users[username]
                else:
                    result['error'] = f"User '{username}' not found"

            elif action == 'edit' and username and data:
                # Edit user data
                if username in users:
                    # Backup original data
                    result['original_data'] = users[username].copy()

                    # Update with new data
                    users[username].update(data)

                    # Save back to file
                    with open(users_file, 'w', encoding='utf-8') as f:
                        json.dump(users, f, indent=2)

                    result['updated_data'] = users[username]
                    result['success'] = True
                else:
                    result['error'] = f"User '{username}' not found"

            elif action == 'delete' and username:
                # Delete user (with backup)
                if username in users:
                    result['deleted_data'] = users[username].copy()
                    del users[username]

                    # Save back to file
                    with open(users_file, 'w', encoding='utf-8') as f:
                        json.dump(users, f, indent=2)

                    result['success'] = True
                else:
                    result['error'] = f"User '{username}' not found"

            elif action == 'reset' and username:
                # Reset user data (clear trips, stats, etc.)
                if username in users:
                    result['original_data'] = users[username].copy()

                    # Reset specific data while preserving core account info
                    users[username]['stats'] = {
                        'total_trips': 0,
                        'total_distance': 0,
                        'total_co2_saved': 0,
                        'total_calories': 0
                    }
                    users[username]['trips'] = []
                    users[username]['challenges'] = []
                    users[username]['achievements'] = []

                    # Save back to file
                    with open(users_file, 'w', encoding='utf-8') as f:
                        json.dump(users, f, indent=2)

                    result['reset_data'] = users[username]
                    result['success'] = True
                else:
                    result['error'] = f"User '{username}' not found"

            else:
                result['error'] = f"Invalid action '{action}' or missing parameters"

            return result

        except Exception as e:
            return {
                'error': str(e),
                'traceback': traceback.format_exc(),
                'action': action,
                'username': username
            }

    def manage_configuration(self, action: str = 'view', config_key: Optional[str] = None, config_value: Optional[Any] = None) -> Dict[str, Any]:
        """Manage application configuration."""
        if not self.developer_auth.is_developer_authenticated():
            raise PermissionError("Developer authentication required")

        self.developer_auth.log_action("CONFIGURATION_MANAGEMENT", f"Action: {action}, Key: {config_key}")

        result = {
            'timestamp': datetime.now().isoformat(),
            'action': action
        }

        try:
            if action == 'view':
                # View current configuration
                if self.config_manager:
                    result['config'] = self.config_manager.get_all_config()
                else:
                    # Fallback to environment variables and basic config
                    config_data = {}

                    # Get important environment variables
                    important_vars = [
                        'DEVELOPER_MODE_ENABLED', 'EMAIL_USERNAME', 'FROM_EMAIL',
                        'OPENWEATHER_API_KEY', 'WEATHERAPI_KEY', 'GOOGLE_MAPS_API_KEY',
                        'SESSION_SECRET_KEY', 'JWT_SECRET_KEY'
                    ]

                    for var in important_vars:
                        value = os.environ.get(var)
                        if value:
                            # Hide sensitive values
                            if any(sensitive in var.upper() for sensitive in ['PASSWORD', 'SECRET', 'KEY', 'TOKEN']):
                                config_data[var] = '***HIDDEN***'
                            else:
                                config_data[var] = value
                        else:
                            config_data[var] = 'NOT SET'

                    result['config'] = config_data

            elif action == 'set' and config_key and config_value is not None:
                # Set configuration value (environment variable)
                os.environ[config_key] = str(config_value)
                result['success'] = True
                result['key'] = config_key
                result['value'] = '***HIDDEN***' if any(sensitive in config_key.upper()
                                                      for sensitive in ['PASSWORD', 'SECRET', 'KEY', 'TOKEN']) else config_value

            elif action == 'unset' and config_key:
                # Unset configuration value
                if config_key in os.environ:
                    del os.environ[config_key]
                    result['success'] = True
                    result['key'] = config_key
                else:
                    result['error'] = f"Configuration key '{config_key}' not found"

            else:
                result['error'] = f"Invalid action '{action}' or missing parameters"

            return result

        except Exception as e:
            return {
                'error': str(e),
                'traceback': traceback.format_exc(),
                'action': action,
                'config_key': config_key
            }

    def export_system_data(self, export_type: str = 'all', output_format: str = 'json') -> Dict[str, Any]:
        """Export system data for backup or analysis."""
        if not self.developer_auth.is_developer_authenticated():
            raise PermissionError("Developer authentication required")

        self.developer_auth.log_action("DATA_EXPORT", f"Type: {export_type}, Format: {output_format}")

        result = {
            'timestamp': datetime.now().isoformat(),
            'export_type': export_type,
            'format': output_format
        }

        try:
            export_data = {}

            if export_type in ['all', 'users']:
                # Export user data
                users_file = os.path.join(os.getcwd(), 'data', 'user', 'users.json')
                if os.path.exists(users_file):
                    with open(users_file, 'r', encoding='utf-8') as f:
                        export_data['users'] = json.load(f)

            if export_type in ['all', 'database']:
                # Export database data
                db_data = self.view_database_contents()
                if 'error' not in db_data:
                    export_data['database'] = db_data

            if export_type in ['all', 'cache']:
                # Export cache data
                cache_data = self.manage_cache('view')
                export_data['cache'] = cache_data

            if export_type in ['all', 'logs']:
                # Export recent log data
                log_dir = os.path.join(os.getcwd(), 'Logs')
                if os.path.exists(log_dir):
                    logs = {}
                    for log_file in os.listdir(log_dir):
                        if log_file.endswith('.log'):
                            log_path = os.path.join(log_dir, log_file)
                            try:
                                with open(log_path, 'r', encoding='utf-8') as f:
                                    # Get last 100 lines
                                    lines = f.readlines()
                                    logs[log_file] = lines[-100:] if len(lines) > 100 else lines
                            except Exception as e:
                                logs[log_file] = f"Error reading log: {e}"
                    export_data['logs'] = logs

            if export_type in ['all', 'config']:
                # Export configuration (non-sensitive)
                config_data = self.manage_configuration('view')
                if 'config' in config_data:
                    export_data['config'] = config_data['config']

            # Generate filename
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"ecocycle_export_{export_type}_{timestamp}.{output_format}"
            export_path = os.path.join(os.getcwd(), 'data', 'exports', filename)

            # Create exports directory if it doesn't exist
            os.makedirs(os.path.dirname(export_path), exist_ok=True)

            # Save export data
            if output_format == 'json':
                with open(export_path, 'w', encoding='utf-8') as f:
                    json.dump(export_data, f, indent=2, default=str)
            else:
                result['error'] = f"Unsupported output format: {output_format}"
                return result

            result['success'] = True
            result['filename'] = filename
            result['path'] = export_path
            result['size'] = os.path.getsize(export_path)
            result['records_exported'] = len(export_data)

            return result

        except Exception as e:
            return {
                'error': str(e),
                'traceback': traceback.format_exc(),
                'export_type': export_type,
                'output_format': output_format
            }

    def monitor_performance(self) -> Dict[str, Any]:
        """Monitor system performance metrics."""
        if not self.developer_auth.is_developer_authenticated():
            raise PermissionError("Developer authentication required")

        self.developer_auth.log_action("PERFORMANCE_MONITORING", "Collecting performance metrics")

        result = {
            'timestamp': datetime.now().isoformat(),
            'system_metrics': {},
            'application_metrics': {},
            'database_metrics': {},
            'file_metrics': {}
        }

        try:
            import psutil

            # System metrics
            result['system_metrics'] = {
                'cpu_percent': psutil.cpu_percent(interval=1),
                'memory_percent': psutil.virtual_memory().percent,
                'disk_usage': psutil.disk_usage('/').percent,
                'boot_time': datetime.fromtimestamp(psutil.boot_time()).isoformat(),
                'load_average': os.getloadavg() if hasattr(os, 'getloadavg') else 'N/A'
            }

            # Memory details
            memory = psutil.virtual_memory()
            result['system_metrics']['memory_details'] = {
                'total': memory.total,
                'available': memory.available,
                'used': memory.used,
                'free': memory.free
            }

        except ImportError:
            result['system_metrics']['error'] = 'psutil not available - install with: pip install psutil'
        except Exception as e:
            result['system_metrics']['error'] = str(e)

        try:
            # Application metrics
            import resource

            usage = resource.getrusage(resource.RUSAGE_SELF)
            result['application_metrics'] = {
                'user_time': usage.ru_utime,
                'system_time': usage.ru_stime,
                'max_memory': usage.ru_maxrss,
                'page_faults': usage.ru_majflt,
                'context_switches': usage.ru_nvcsw + usage.ru_nivcsw
            }

        except Exception as e:
            result['application_metrics']['error'] = str(e)

        try:
            # Database metrics
            if os.path.exists(DATABASE_FILE):
                db_size = os.path.getsize(DATABASE_FILE)
                result['database_metrics'] = {
                    'file_size': db_size,
                    'file_size_mb': round(db_size / (1024 * 1024), 2)
                }

                # Get table counts for performance assessment
                conn = sqlite3.connect(DATABASE_FILE)
                cursor = conn.cursor()
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
                tables = [row[0] for row in cursor.fetchall()]

                table_metrics = {}
                for table in tables:
                    cursor.execute(f"SELECT COUNT(*) FROM {table}")
                    count = cursor.fetchone()[0]
                    table_metrics[table] = count

                result['database_metrics']['table_counts'] = table_metrics
                conn.close()
            else:
                result['database_metrics']['error'] = 'Database file not found'

        except Exception as e:
            result['database_metrics']['error'] = str(e)

        try:
            # File system metrics
            important_dirs = ['data', 'Logs', 'data/cache', 'data/user']

            for dir_name in important_dirs:
                dir_path = os.path.join(os.getcwd(), dir_name)
                if os.path.exists(dir_path):
                    total_size = 0
                    file_count = 0

                    for root, dirs, files in os.walk(dir_path):
                        for file in files:
                            file_path = os.path.join(root, file)
                            try:
                                total_size += os.path.getsize(file_path)
                                file_count += 1
                            except (OSError, IOError):
                                pass

                    result['file_metrics'][dir_name] = {
                        'total_size': total_size,
                        'total_size_mb': round(total_size / (1024 * 1024), 2),
                        'file_count': file_count
                    }
                else:
                    result['file_metrics'][dir_name] = {'error': 'Directory not found'}

        except Exception as e:
            result['file_metrics']['error'] = str(e)

        return result

    def analyze_logs(self, log_file: Optional[str] = None, lines: int = 100, filter_level: Optional[str] = None) -> Dict[str, Any]:
        """Analyze application logs for patterns and issues."""
        if not self.developer_auth.is_developer_authenticated():
            raise PermissionError("Developer authentication required")

        self.developer_auth.log_action("LOG_ANALYSIS", f"Analyzing logs: {log_file or 'all'}")

        result = {
            'timestamp': datetime.now().isoformat(),
            'analysis': {},
            'patterns': {},
            'recent_entries': {}
        }

        try:
            log_dir = os.path.join(os.getcwd(), 'Logs')

            if not os.path.exists(log_dir):
                result['error'] = 'Logs directory not found'
                return result

            log_files = []
            if log_file:
                if os.path.exists(os.path.join(log_dir, log_file)):
                    log_files = [log_file]
                else:
                    result['error'] = f"Log file '{log_file}' not found"
                    return result
            else:
                log_files = [f for f in os.listdir(log_dir) if f.endswith('.log')]

            for log_filename in log_files:
                log_path = os.path.join(log_dir, log_filename)

                try:
                    with open(log_path, 'r', encoding='utf-8') as f:
                        all_lines = f.readlines()

                    # Get recent lines
                    recent_lines = all_lines[-lines:] if len(all_lines) > lines else all_lines

                    # Filter by level if specified
                    if filter_level:
                        recent_lines = [line for line in recent_lines if filter_level.upper() in line.upper()]

                    # Analyze patterns
                    error_count = len([line for line in recent_lines if 'ERROR' in line.upper()])
                    warning_count = len([line for line in recent_lines if 'WARNING' in line.upper()])
                    info_count = len([line for line in recent_lines if 'INFO' in line.upper()])
                    debug_count = len([line for line in recent_lines if 'DEBUG' in line.upper()])

                    # Extract error patterns
                    error_patterns = {}
                    for line in recent_lines:
                        if 'ERROR' in line.upper():
                            # Simple pattern extraction - look for common error types
                            if 'ImportError' in line:
                                error_patterns['ImportError'] = error_patterns.get('ImportError', 0) + 1
                            elif 'FileNotFoundError' in line:
                                error_patterns['FileNotFoundError'] = error_patterns.get('FileNotFoundError', 0) + 1
                            elif 'PermissionError' in line:
                                error_patterns['PermissionError'] = error_patterns.get('PermissionError', 0) + 1
                            elif 'ConnectionError' in line:
                                error_patterns['ConnectionError'] = error_patterns.get('ConnectionError', 0) + 1
                            else:
                                error_patterns['Other'] = error_patterns.get('Other', 0) + 1

                    result['analysis'][log_filename] = {
                        'total_lines': len(all_lines),
                        'analyzed_lines': len(recent_lines),
                        'error_count': error_count,
                        'warning_count': warning_count,
                        'info_count': info_count,
                        'debug_count': debug_count,
                        'file_size': os.path.getsize(log_path),
                        'last_modified': datetime.fromtimestamp(os.path.getmtime(log_path)).isoformat()
                    }

                    result['patterns'][log_filename] = error_patterns
                    result['recent_entries'][log_filename] = [line.strip() for line in recent_lines[-10:]]  # Last 10 entries

                except Exception as e:
                    result['analysis'][log_filename] = {'error': str(e)}

            return result

        except Exception as e:
            return {
                'error': str(e),
                'traceback': traceback.format_exc(),
                'log_file': log_file,
                'lines': lines
            }

    def manage_sessions(self, action: str = 'view', session_id: Optional[str] = None) -> Dict[str, Any]:
        """Manage user sessions and developer sessions."""
        if not self.developer_auth.is_developer_authenticated():
            raise PermissionError("Developer authentication required")

        self.developer_auth.log_action("SESSION_MANAGEMENT", f"Action: {action}, Session: {session_id}")

        result = {
            'timestamp': datetime.now().isoformat(),
            'action': action,
            'developer_session': {},
            'user_sessions': {}
        }

        try:
            # Developer session info
            result['developer_session'] = {
                'username': self.developer_auth.get_developer_username(),
                'authenticated': self.developer_auth.is_developer_authenticated(),
                'session_start': self.developer_auth.session_start_time.isoformat() if self.developer_auth.session_start_time else None,
                'session_timeout': self.developer_auth.session_timeout,
                'time_remaining': None
            }

            if self.developer_auth.session_start_time:
                elapsed = (datetime.now() - self.developer_auth.session_start_time).total_seconds()
                remaining = max(0, self.developer_auth.session_timeout - elapsed)
                result['developer_session']['time_remaining'] = remaining

            # User session info
            session_file = os.path.join(os.getcwd(), 'data', 'user', 'session.json')
            if os.path.exists(session_file):
                try:
                    with open(session_file, 'r', encoding='utf-8') as f:
                        session_data = json.load(f)

                    result['user_sessions'] = {
                        'current_user': session_data.get('current_user'),
                        'login_time': session_data.get('login_time'),
                        'last_activity': session_data.get('last_activity'),
                        'session_data': session_data
                    }
                except Exception as e:
                    result['user_sessions']['error'] = f"Error reading session file: {e}"
            else:
                result['user_sessions']['error'] = 'No active user sessions found'

            # Handle different actions
            if action == 'list_active':
                # List active sessions
                active_sessions = []

                # Add developer session if active
                if self.developer_auth.is_developer_authenticated():
                    active_sessions.append({
                        'session_id': f"dev_{self.developer_auth.get_developer_username()}",
                        'username': self.developer_auth.get_developer_username(),
                        'start_time': result['developer_session']['session_start'],
                        'last_activity': datetime.now().isoformat(),
                        'status': 'Developer Session'
                    })

                # Add user session if exists
                if 'error' not in result['user_sessions']:
                    active_sessions.append({
                        'session_id': f"user_{result['user_sessions']['current_user']}",
                        'username': result['user_sessions']['current_user'],
                        'start_time': result['user_sessions']['login_time'],
                        'last_activity': result['user_sessions']['last_activity'],
                        'status': 'User Session'
                    })

                result['active_sessions'] = active_sessions

            elif action == 'history':
                # Session history (simulated for now)
                result['session_history'] = [
                    {
                        'session_id': f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                        'username': self.developer_auth.get_developer_username(),
                        'start_time': datetime.now().isoformat(),
                        'end_time': None,
                        'duration': 'Active'
                    }
                ]

            elif action == 'statistics':
                # Session statistics
                result['statistics'] = {
                    'total_sessions': 1,
                    'active_sessions': 1 if self.developer_auth.is_developer_authenticated() else 0,
                    'average_duration': '30 minutes',
                    'longest_session': '2 hours',
                    'most_active_user': self.developer_auth.get_developer_username(),
                    'sessions_today': 1
                }

            elif action == 'terminate' and session_id:
                # Terminate specific session
                if session_id.startswith('dev_'):
                    # Terminate developer session
                    self.developer_auth.logout_developer()
                    result['terminated'] = True
                    result['session_id'] = session_id
                elif session_id.startswith('user_'):
                    # Terminate user session
                    if os.path.exists(session_file):
                        try:
                            os.remove(session_file)
                            result['terminated'] = True
                            result['session_id'] = session_id
                        except Exception as e:
                            result['error'] = f"Failed to terminate session: {e}"
                    else:
                        result['error'] = 'Session not found'
                else:
                    result['error'] = 'Invalid session ID'

            elif action == 'clear_all':
                # Clear all sessions
                sessions_cleared = 0

                # Clear user sessions
                if os.path.exists(session_file):
                    try:
                        os.remove(session_file)
                        sessions_cleared += 1
                    except Exception as e:
                        result['error'] = f"Failed to clear user session: {e}"

                result['sessions_cleared'] = sessions_cleared
                result['success'] = True

            elif action == 'clear_user_sessions':
                # Clear user sessions only
                if os.path.exists(session_file):
                    try:
                        os.remove(session_file)
                        result['user_sessions']['cleared'] = True
                    except Exception as e:
                        result['user_sessions']['clear_error'] = str(e)
                else:
                    result['user_sessions']['cleared'] = False
                    result['user_sessions']['reason'] = 'No session file to clear'

            elif action == 'extend_developer_session':
                # Extend developer session
                self.developer_auth.extend_session()
                result['developer_session']['extended'] = True
                result['developer_session']['new_start_time'] = datetime.now().isoformat()

            return result

        except Exception as e:
            return {
                'error': str(e),
                'traceback': traceback.format_exc(),
                'action': action,
                'session_id': session_id
            }

    def security_audit(self, audit_type: str = 'all') -> Dict[str, Any]:
        """Perform comprehensive security audit."""
        if not self.developer_auth.is_developer_authenticated():
            raise PermissionError("Developer authentication required")

        self.developer_auth.log_action("SECURITY_AUDIT", f"Audit type: {audit_type}")

        result = {
            'timestamp': datetime.now().isoformat(),
            'audit_type': audit_type,
            'findings': {},
            'recommendations': [],
            'risk_level': 'low'
        }

        try:
            if audit_type in ['all', 'password']:
                result['findings']['password_analysis'] = self._analyze_password_strength()

            if audit_type in ['all', 'session']:
                result['findings']['session_security'] = self._check_session_security()

            if audit_type in ['all', 'permissions']:
                result['findings']['file_permissions'] = self._audit_file_permissions()

            if audit_type in ['all', 'config']:
                result['findings']['configuration_security'] = self._scan_configuration_security()

            if audit_type in ['all', 'vulnerability']:
                result['findings']['vulnerability_assessment'] = self._assess_vulnerabilities()

            # Determine overall risk level
            risk_levels = []
            for finding_type, findings in result['findings'].items():
                if isinstance(findings, dict) and 'risk_level' in findings:
                    risk_levels.append(findings['risk_level'])

            if 'critical' in risk_levels:
                result['risk_level'] = 'critical'
            elif 'high' in risk_levels:
                result['risk_level'] = 'high'
            elif 'medium' in risk_levels:
                result['risk_level'] = 'medium'
            else:
                result['risk_level'] = 'low'

            return result

        except Exception as e:
            return {
                'error': str(e),
                'traceback': traceback.format_exc(),
                'audit_type': audit_type,
                'timestamp': datetime.now().isoformat()
            }

    def _analyze_password_strength(self) -> Dict[str, Any]:
        """Analyze password strength across the system."""
        analysis = {
            'risk_level': 'low',
            'issues': [],
            'recommendations': [],
            'user_analysis': {}
        }

        try:
            # Load user data
            users_file = os.path.join(os.getcwd(), 'data', 'user', 'users.json')
            if os.path.exists(users_file):
                with open(users_file, 'r', encoding='utf-8') as f:
                    users = json.load(f)

                weak_passwords = 0
                total_users = len(users)

                for username, user_data in users.items():
                    # Check if user has password requirements
                    password_hash = user_data.get('password_hash', '')

                    # Basic analysis (can't check actual password strength from hash)
                    user_analysis = {
                        'has_password': bool(password_hash),
                        'is_guest': user_data.get('is_guest', False),
                        'email_verified': user_data.get('email_verified', False),
                        'two_factor_enabled': user_data.get('preferences', {}).get('require_email_verification', False)
                    }

                    if not user_analysis['has_password'] and not user_analysis['is_guest']:
                        analysis['issues'].append(f"User {username} has no password set")
                        weak_passwords += 1

                    if not user_analysis['email_verified']:
                        analysis['issues'].append(f"User {username} has unverified email")

                    analysis['user_analysis'][username] = user_analysis

                # Calculate risk level
                if weak_passwords > total_users * 0.5:
                    analysis['risk_level'] = 'high'
                elif weak_passwords > total_users * 0.2:
                    analysis['risk_level'] = 'medium'

                analysis['statistics'] = {
                    'total_users': total_users,
                    'users_with_weak_security': weak_passwords,
                    'percentage_weak': (weak_passwords / total_users * 100) if total_users > 0 else 0
                }

            # Add recommendations
            analysis['recommendations'] = [
                "Enforce minimum password length of 8 characters",
                "Require password complexity (uppercase, lowercase, numbers, symbols)",
                "Implement password expiration policies",
                "Enable two-factor authentication for all users",
                "Regular password strength audits"
            ]

        except Exception as e:
            analysis['error'] = str(e)
            analysis['risk_level'] = 'unknown'

        return analysis

    def _check_session_security(self) -> Dict[str, Any]:
        """Check session security configuration."""
        security_check = {
            'risk_level': 'low',
            'issues': [],
            'recommendations': [],
            'configuration': {}
        }

        try:
            # Check session secret key
            session_secret = os.environ.get('SESSION_SECRET_KEY')
            if not session_secret:
                security_check['issues'].append("SESSION_SECRET_KEY not configured")
                security_check['risk_level'] = 'high'
            elif len(session_secret) < 32:
                security_check['issues'].append("SESSION_SECRET_KEY is too short (should be at least 32 characters)")
                security_check['risk_level'] = 'medium'

            # Check JWT secret
            jwt_secret = os.environ.get('JWT_SECRET_KEY')
            if not jwt_secret:
                security_check['issues'].append("JWT_SECRET_KEY not configured")
                security_check['risk_level'] = 'high'

            # Check HTTPS configuration
            use_https = os.environ.get('USE_HTTPS', 'false').lower() == 'true'
            if not use_https:
                security_check['issues'].append("HTTPS not enabled")
                security_check['risk_level'] = 'medium'

            security_check['configuration'] = {
                'session_secret_configured': bool(session_secret),
                'session_secret_length': len(session_secret) if session_secret else 0,
                'jwt_secret_configured': bool(jwt_secret),
                'https_enabled': use_https
            }

            # Add recommendations
            security_check['recommendations'] = [
                "Use strong, randomly generated session secrets",
                "Enable HTTPS in production",
                "Implement session timeout",
                "Use secure cookie flags",
                "Regular session secret rotation"
            ]

        except Exception as e:
            security_check['error'] = str(e)
            security_check['risk_level'] = 'unknown'

        return security_check

    def _audit_file_permissions(self) -> Dict[str, Any]:
        """Audit file permissions for security issues."""
        audit = {
            'risk_level': 'low',
            'issues': [],
            'recommendations': [],
            'file_analysis': {}
        }

        try:
            # Check important directories and files
            important_paths = [
                'data/user/users.json',
                'data/cache',
                'Logs',
                '.env',
                'config.json',
                'ecocycle.db'
            ]

            for path in important_paths:
                full_path = os.path.join(os.getcwd(), path)
                if os.path.exists(full_path):
                    stat_info = os.stat(full_path)
                    permissions = oct(stat_info.st_mode)[-3:]

                    file_info = {
                        'path': path,
                        'permissions': permissions,
                        'owner_readable': bool(stat_info.st_mode & 0o400),
                        'owner_writable': bool(stat_info.st_mode & 0o200),
                        'owner_executable': bool(stat_info.st_mode & 0o100),
                        'group_readable': bool(stat_info.st_mode & 0o040),
                        'group_writable': bool(stat_info.st_mode & 0o020),
                        'group_executable': bool(stat_info.st_mode & 0o010),
                        'other_readable': bool(stat_info.st_mode & 0o004),
                        'other_writable': bool(stat_info.st_mode & 0o002),
                        'other_executable': bool(stat_info.st_mode & 0o001)
                    }

                    # Check for security issues
                    if file_info['other_writable']:
                        audit['issues'].append(f"{path} is world-writable (permissions: {permissions})")
                        audit['risk_level'] = 'high'

                    if file_info['other_readable'] and 'users.json' in path:
                        audit['issues'].append(f"{path} is world-readable (permissions: {permissions})")
                        audit['risk_level'] = 'medium'

                    audit['file_analysis'][path] = file_info

            # Add recommendations
            audit['recommendations'] = [
                "Restrict file permissions to owner only for sensitive files",
                "Use 600 (rw-------) for configuration files",
                "Use 700 (rwx------) for data directories",
                "Regular permission audits",
                "Implement file integrity monitoring"
            ]

        except Exception as e:
            audit['error'] = str(e)
            audit['risk_level'] = 'unknown'

        return audit

    def _scan_configuration_security(self) -> Dict[str, Any]:
        """Scan configuration for security issues."""
        scan = {
            'risk_level': 'low',
            'issues': [],
            'recommendations': [],
            'configuration_analysis': {}
        }

        try:
            # Check environment variables for security issues
            sensitive_vars = [
                'EMAIL_PASSWORD', 'EMAIL_USERNAME', 'SESSION_SECRET_KEY',
                'JWT_SECRET_KEY', 'OPENWEATHER_API_KEY', 'WEATHERAPI_KEY',
                'GOOGLE_MAPS_API_KEY'
            ]

            for var in sensitive_vars:
                value = os.environ.get(var)
                if value:
                    analysis = {
                        'configured': True,
                        'length': len(value),
                        'has_special_chars': any(c in value for c in '!@#$%^&*()'),
                        'has_numbers': any(c.isdigit() for c in value),
                        'has_uppercase': any(c.isupper() for c in value),
                        'has_lowercase': any(c.islower() for c in value)
                    }

                    # Check for weak configurations
                    if 'SECRET' in var or 'PASSWORD' in var:
                        if len(value) < 16:
                            scan['issues'].append(f"{var} is too short (less than 16 characters)")
                            scan['risk_level'] = 'medium'

                        if not analysis['has_special_chars']:
                            scan['issues'].append(f"{var} lacks special characters")
                            scan['risk_level'] = 'medium'

                    scan['configuration_analysis'][var] = analysis
                else:
                    scan['issues'].append(f"{var} is not configured")
                    scan['configuration_analysis'][var] = {'configured': False}

            # Check for debug mode
            debug_mode = os.environ.get('DEBUG', 'false').lower() == 'true'
            if debug_mode:
                scan['issues'].append("Debug mode is enabled in production")
                scan['risk_level'] = 'high'

            # Add recommendations
            scan['recommendations'] = [
                "Use strong, randomly generated secrets",
                "Disable debug mode in production",
                "Store sensitive configuration in secure vaults",
                "Regular configuration reviews",
                "Implement configuration validation"
            ]

        except Exception as e:
            scan['error'] = str(e)
            scan['risk_level'] = 'unknown'

        return scan

    def _assess_vulnerabilities(self) -> Dict[str, Any]:
        """Assess system for common vulnerabilities."""
        assessment = {
            'risk_level': 'low',
            'vulnerabilities': [],
            'recommendations': [],
            'checks_performed': []
        }

        try:
            # Check for common vulnerabilities

            # 1. Check for default credentials
            assessment['checks_performed'].append("Default credentials check")
            users_file = os.path.join(os.getcwd(), 'data', 'user', 'users.json')
            if os.path.exists(users_file):
                with open(users_file, 'r', encoding='utf-8') as f:
                    users = json.load(f)

                for username, user_data in users.items():
                    if username.lower() in ['admin', 'administrator', 'root', 'test']:
                        assessment['vulnerabilities'].append(f"Default username detected: {username}")
                        assessment['risk_level'] = 'medium'

            # 2. Check for exposed sensitive files
            assessment['checks_performed'].append("Sensitive file exposure check")
            sensitive_files = ['.env', 'config.json', 'secrets.json', 'credentials.json']
            for file in sensitive_files:
                if os.path.exists(os.path.join(os.getcwd(), file)):
                    assessment['vulnerabilities'].append(f"Sensitive file found: {file}")
                    assessment['risk_level'] = 'medium'

            # 3. Check for insecure dependencies (basic check)
            assessment['checks_performed'].append("Dependency security check")
            try:
                import pkg_resources
                installed_packages = [d.project_name for d in pkg_resources.working_set]

                # Known vulnerable packages (simplified check)
                known_vulnerable = ['urllib3<1.26.5', 'requests<2.25.1']
                for package in installed_packages:
                    if any(vuln in package for vuln in known_vulnerable):
                        assessment['vulnerabilities'].append(f"Potentially vulnerable package: {package}")
                        assessment['risk_level'] = 'medium'
            except ImportError:
                pass

            # 4. Check for weak encryption
            assessment['checks_performed'].append("Encryption strength check")
            # This is a basic check - in practice, you'd analyze actual crypto usage
            if not os.environ.get('USE_STRONG_ENCRYPTION', 'false').lower() == 'true':
                assessment['vulnerabilities'].append("Strong encryption not explicitly enabled")
                assessment['risk_level'] = 'low'

            # Add recommendations
            assessment['recommendations'] = [
                "Regular security updates and patches",
                "Implement vulnerability scanning",
                "Use security headers in web applications",
                "Regular penetration testing",
                "Implement intrusion detection",
                "Security awareness training"
            ]

        except Exception as e:
            assessment['error'] = str(e)
            assessment['risk_level'] = 'unknown'

        return assessment

    def get_system_health(self) -> Dict[str, Any]:
        """Get comprehensive system health information."""
        if not self.developer_auth.is_developer_authenticated():
            raise PermissionError("Developer authentication required")

        self.developer_auth.log_action("SYSTEM_HEALTH", "Getting system health data")

        health_data = {
            'timestamp': datetime.now().isoformat(),
            'overall_status': 'healthy',
            'components': {},
            'alerts': [],
            'metrics': {}
        }

        try:
            # Get performance metrics for health assessment
            performance_data = self.get_performance_metrics('all')
            alerts_data = performance_data.get('alerts', {})
            active_alerts = alerts_data.get('active_alerts', [])

            # Determine overall status based on alerts
            critical_alerts = [a for a in active_alerts if a.get('level') == 'CRITICAL']
            warning_alerts = [a for a in active_alerts if a.get('level') == 'WARNING']

            if critical_alerts:
                health_data['overall_status'] = 'critical'
            elif warning_alerts:
                health_data['overall_status'] = 'warning'
            else:
                health_data['overall_status'] = 'healthy'

            # System component health
            system_metrics = performance_data.get('system_metrics', {})
            if 'error' not in system_metrics:
                cpu_info = system_metrics.get('cpu', {})
                cpu_usage = cpu_info.get('usage_percent', 0)

                cpu_status = 'critical' if cpu_usage > 90 else 'warning' if cpu_usage > 70 else 'healthy'

                health_data['components']['system'] = {
                    'status': cpu_status,
                    'cpu_usage': f"{cpu_usage}%",
                    'cpu_cores': cpu_info.get('core_count', 'N/A'),
                    'uptime': system_metrics.get('system', {}).get('uptime_formatted', 'N/A'),
                    'platform': system_metrics.get('system', {}).get('platform', 'N/A')
                }
            else:
                health_data['components']['system'] = {
                    'status': 'unknown',
                    'error': system_metrics['error']
                }

            # Memory component health
            memory_metrics = performance_data.get('memory_metrics', {})
            if 'error' not in memory_metrics:
                vmem = memory_metrics.get('virtual', {})
                memory_usage = vmem.get('percent', 0)

                memory_status = 'critical' if memory_usage > 95 else 'warning' if memory_usage > 80 else 'healthy'

                health_data['components']['memory'] = {
                    'status': memory_status,
                    'usage': f"{memory_usage}%",
                    'available': f"{vmem.get('available_gb', 'N/A')} GB",
                    'total': f"{vmem.get('total_gb', 'N/A')} GB"
                }

                # Swap memory
                swap = memory_metrics.get('swap', {})
                if swap:
                    swap_usage = swap.get('percent', 0)
                    swap_status = 'warning' if swap_usage > 50 else 'healthy'
                    health_data['components']['swap'] = {
                        'status': swap_status,
                        'usage': f"{swap_usage}%",
                        'total': f"{swap.get('total_gb', 'N/A')} GB"
                    }
            else:
                health_data['components']['memory'] = {
                    'status': 'unknown',
                    'error': memory_metrics['error']
                }

            # Disk component health
            disk_metrics = performance_data.get('disk_metrics', {})
            if 'error' not in disk_metrics:
                disk_usage = disk_metrics.get('usage', {})
                disk_statuses = []

                for device, info in disk_usage.items():
                    if 'error' not in info:
                        disk_percent = info.get('percent', 0)
                        disk_status = 'critical' if disk_percent > 95 else 'warning' if disk_percent > 85 else 'healthy'
                        disk_statuses.append(disk_status)

                        # Add primary disk info (root or first disk)
                        if info.get('mountpoint') == '/' or len(health_data['components']) == 3:
                            health_data['components']['disk'] = {
                                'status': disk_status,
                                'usage': f"{disk_percent}%",
                                'free': f"{info.get('free_gb', 'N/A')} GB",
                                'total': f"{info.get('total_gb', 'N/A')} GB",
                                'mountpoint': info.get('mountpoint', 'N/A')
                            }

                # Overall disk status
                if not health_data['components'].get('disk'):
                    overall_disk_status = 'critical' if 'critical' in disk_statuses else 'warning' if 'warning' in disk_statuses else 'healthy'
                    health_data['components']['disk'] = {
                        'status': overall_disk_status,
                        'devices_count': len(disk_usage)
                    }
            else:
                health_data['components']['disk'] = {
                    'status': 'unknown',
                    'error': disk_metrics['error']
                }

            # Database health check
            try:
                db_status = self.system_diagnostics()
                db_info = db_status.get('database_status', {})

                if db_info.get('file_exists'):
                    db_size_mb = db_info.get('file_size', 0) / (1024 * 1024)
                    table_count = len(db_info.get('tables', []))

                    health_data['components']['database'] = {
                        'status': 'healthy',
                        'file_exists': True,
                        'size_mb': round(db_size_mb, 2),
                        'tables': table_count,
                        'total_records': sum(db_info.get('table_counts', {}).values())
                    }
                else:
                    health_data['components']['database'] = {
                        'status': 'warning',
                        'file_exists': False,
                        'message': 'Database file not found'
                    }
            except Exception as e:
                health_data['components']['database'] = {
                    'status': 'error',
                    'error': str(e)
                }

            # Application health
            app_metrics = performance_data.get('application_metrics', {})
            if 'error' not in app_metrics:
                process_info = app_metrics.get('process', {})

                health_data['components']['application'] = {
                    'status': 'healthy',
                    'process_id': process_info.get('pid', 'N/A'),
                    'cpu_usage': f"{process_info.get('cpu_percent', 'N/A')}%",
                    'memory_usage': f"{process_info.get('memory_percent', 'N/A')}%",
                    'threads': process_info.get('num_threads', 'N/A')
                }
            else:
                health_data['components']['application'] = {
                    'status': 'unknown',
                    'error': app_metrics['error']
                }

            # Cache health check
            try:
                cache_data = self.manage_cache('view')
                cache_status = 'healthy'
                cache_info = {}

                for cache_name, cache_details in cache_data.items():
                    if isinstance(cache_details, dict) and cache_details.get('exists'):
                        cache_info[cache_name] = {
                            'size_mb': round(cache_details.get('size', 0) / (1024 * 1024), 2),
                            'entries': cache_details.get('entries', 0)
                        }

                health_data['components']['cache'] = {
                    'status': cache_status,
                    'caches': cache_info,
                    'total_caches': len(cache_info)
                }
            except Exception as e:
                health_data['components']['cache'] = {
                    'status': 'error',
                    'error': str(e)
                }

            # Set alerts
            health_data['alerts'] = [alert.get('message', 'Unknown alert') for alert in active_alerts]

            # Add summary metrics
            health_data['metrics'] = {
                'total_alerts': len(active_alerts),
                'critical_alerts': len(critical_alerts),
                'warning_alerts': len(warning_alerts),
                'healthy_components': len([c for c in health_data['components'].values() if c.get('status') == 'healthy']),
                'total_components': len(health_data['components'])
            }

            return health_data

        except Exception as e:
            return {
                'error': str(e),
                'traceback': traceback.format_exc(),
                'timestamp': datetime.now().isoformat()
            }

    def get_performance_metrics(self, metric_type: str = 'all') -> Dict[str, Any]:
        """Get detailed performance metrics for specific types or all metrics."""
        if not self.developer_auth.is_developer_authenticated():
            raise PermissionError("Developer authentication required")

        self.developer_auth.log_action("PERFORMANCE_METRICS", f"Getting {metric_type} metrics")

        result = {
            'timestamp': datetime.now().isoformat(),
            'metric_type': metric_type
        }

        try:
            if metric_type in ['all', 'system', 'cpu']:
                result.update(self._get_system_metrics())

            if metric_type in ['all', 'memory']:
                result.update(self._get_memory_metrics())

            if metric_type in ['all', 'disk']:
                result.update(self._get_disk_metrics())

            if metric_type in ['all', 'network']:
                result.update(self._get_network_metrics())

            if metric_type in ['all', 'application']:
                result.update(self._get_application_metrics())

            if metric_type in ['all', 'trends']:
                result.update(self._get_performance_trends())

            if metric_type in ['all', 'alerts']:
                result.update(self._get_performance_alerts())

            return result

        except Exception as e:
            return {
                'error': str(e),
                'traceback': traceback.format_exc(),
                'metric_type': metric_type,
                'timestamp': datetime.now().isoformat()
            }

    def _get_system_metrics(self) -> Dict[str, Any]:
        """Get detailed system metrics."""
        metrics = {'system_metrics': {}}

        try:
            import psutil

            # CPU metrics
            cpu_percent = psutil.cpu_percent(interval=1, percpu=True)
            cpu_freq = psutil.cpu_freq()
            cpu_count = psutil.cpu_count()

            metrics['system_metrics']['cpu'] = {
                'usage_percent': psutil.cpu_percent(interval=1),
                'usage_per_core': cpu_percent,
                'core_count': cpu_count,
                'logical_count': psutil.cpu_count(logical=True),
                'frequency': {
                    'current': cpu_freq.current if cpu_freq else 'N/A',
                    'min': cpu_freq.min if cpu_freq else 'N/A',
                    'max': cpu_freq.max if cpu_freq else 'N/A'
                } if cpu_freq else 'N/A',
                'load_average': os.getloadavg() if hasattr(os, 'getloadavg') else 'N/A',
                'context_switches': psutil.cpu_stats().ctx_switches,
                'interrupts': psutil.cpu_stats().interrupts
            }

            # System info
            boot_time = datetime.fromtimestamp(psutil.boot_time())
            uptime = datetime.now() - boot_time

            metrics['system_metrics']['system'] = {
                'boot_time': boot_time.isoformat(),
                'uptime_seconds': uptime.total_seconds(),
                'uptime_formatted': str(uptime).split('.')[0],  # Remove microseconds
                'platform': sys.platform,
                'python_version': sys.version.split()[0]
            }

        except ImportError:
            metrics['system_metrics']['error'] = 'psutil not available - install with: pip install psutil'
        except Exception as e:
            metrics['system_metrics']['error'] = str(e)

        return metrics

    def _get_memory_metrics(self) -> Dict[str, Any]:
        """Get detailed memory metrics."""
        metrics = {'memory_metrics': {}}

        try:
            import psutil

            # Virtual memory
            vmem = psutil.virtual_memory()
            metrics['memory_metrics']['virtual'] = {
                'total': vmem.total,
                'available': vmem.available,
                'used': vmem.used,
                'free': vmem.free,
                'percent': vmem.percent,
                'total_gb': round(vmem.total / (1024**3), 2),
                'available_gb': round(vmem.available / (1024**3), 2),
                'used_gb': round(vmem.used / (1024**3), 2)
            }

            # Swap memory
            swap = psutil.swap_memory()
            metrics['memory_metrics']['swap'] = {
                'total': swap.total,
                'used': swap.used,
                'free': swap.free,
                'percent': swap.percent,
                'total_gb': round(swap.total / (1024**3), 2),
                'used_gb': round(swap.used / (1024**3), 2)
            }

            # Process memory
            process = psutil.Process()
            pmem = process.memory_info()
            metrics['memory_metrics']['process'] = {
                'rss': pmem.rss,  # Resident Set Size
                'vms': pmem.vms,  # Virtual Memory Size
                'rss_mb': round(pmem.rss / (1024**2), 2),
                'vms_mb': round(pmem.vms / (1024**2), 2),
                'percent': process.memory_percent()
            }

        except ImportError:
            metrics['memory_metrics']['error'] = 'psutil not available'
        except Exception as e:
            metrics['memory_metrics']['error'] = str(e)

        return metrics

    def _get_disk_metrics(self) -> Dict[str, Any]:
        """Get detailed disk I/O metrics."""
        metrics = {'disk_metrics': {}}

        try:
            import psutil

            # Disk usage for all mounted disks
            disk_usage = {}
            for partition in psutil.disk_partitions():
                try:
                    usage = psutil.disk_usage(partition.mountpoint)
                    disk_usage[partition.device] = {
                        'mountpoint': partition.mountpoint,
                        'fstype': partition.fstype,
                        'total': usage.total,
                        'used': usage.used,
                        'free': usage.free,
                        'percent': round((usage.used / usage.total) * 100, 2),
                        'total_gb': round(usage.total / (1024**3), 2),
                        'used_gb': round(usage.used / (1024**3), 2),
                        'free_gb': round(usage.free / (1024**3), 2)
                    }
                except PermissionError:
                    disk_usage[partition.device] = {'error': 'Permission denied'}

            metrics['disk_metrics']['usage'] = disk_usage

            # Disk I/O statistics
            disk_io = psutil.disk_io_counters()
            if disk_io:
                metrics['disk_metrics']['io'] = {
                    'read_count': disk_io.read_count,
                    'write_count': disk_io.write_count,
                    'read_bytes': disk_io.read_bytes,
                    'write_bytes': disk_io.write_bytes,
                    'read_time': disk_io.read_time,
                    'write_time': disk_io.write_time,
                    'read_mb': round(disk_io.read_bytes / (1024**2), 2),
                    'write_mb': round(disk_io.write_bytes / (1024**2), 2)
                }

        except ImportError:
            metrics['disk_metrics']['error'] = 'psutil not available'
        except Exception as e:
            metrics['disk_metrics']['error'] = str(e)

        return metrics

    def _get_network_metrics(self) -> Dict[str, Any]:
        """Get detailed network metrics."""
        metrics = {'network_metrics': {}}

        try:
            import psutil

            # Network I/O statistics
            net_io = psutil.net_io_counters()
            if net_io:
                metrics['network_metrics']['io'] = {
                    'bytes_sent': net_io.bytes_sent,
                    'bytes_recv': net_io.bytes_recv,
                    'packets_sent': net_io.packets_sent,
                    'packets_recv': net_io.packets_recv,
                    'errin': net_io.errin,
                    'errout': net_io.errout,
                    'dropin': net_io.dropin,
                    'dropout': net_io.dropout,
                    'bytes_sent_mb': round(net_io.bytes_sent / (1024**2), 2),
                    'bytes_recv_mb': round(net_io.bytes_recv / (1024**2), 2)
                }

            # Network interfaces
            net_interfaces = {}
            for interface, addrs in psutil.net_if_addrs().items():
                interface_info = {
                    'addresses': [],
                    'stats': {}
                }

                for addr in addrs:
                    interface_info['addresses'].append({
                        'family': str(addr.family),
                        'address': addr.address,
                        'netmask': addr.netmask,
                        'broadcast': addr.broadcast
                    })

                # Interface statistics
                if_stats = psutil.net_if_stats().get(interface)
                if if_stats:
                    interface_info['stats'] = {
                        'isup': if_stats.isup,
                        'duplex': str(if_stats.duplex),
                        'speed': if_stats.speed,
                        'mtu': if_stats.mtu
                    }

                net_interfaces[interface] = interface_info

            metrics['network_metrics']['interfaces'] = net_interfaces

            # Connection statistics
            connections = psutil.net_connections()
            connection_stats = {
                'total': len(connections),
                'established': len([c for c in connections if c.status == 'ESTABLISHED']),
                'listen': len([c for c in connections if c.status == 'LISTEN']),
                'time_wait': len([c for c in connections if c.status == 'TIME_WAIT'])
            }
            metrics['network_metrics']['connections'] = connection_stats

        except ImportError:
            metrics['network_metrics']['error'] = 'psutil not available'
        except Exception as e:
            metrics['network_metrics']['error'] = str(e)

        return metrics

    def _get_application_metrics(self) -> Dict[str, Any]:
        """Get detailed application performance metrics."""
        metrics = {'application_metrics': {}}

        try:
            import psutil
            import resource

            # Current process
            process = psutil.Process()

            # CPU and memory for current process
            metrics['application_metrics']['process'] = {
                'pid': process.pid,
                'name': process.name(),
                'status': process.status(),
                'cpu_percent': process.cpu_percent(),
                'memory_percent': process.memory_percent(),
                'num_threads': process.num_threads(),
                'create_time': datetime.fromtimestamp(process.create_time()).isoformat()
            }

            # Resource usage
            usage = resource.getrusage(resource.RUSAGE_SELF)
            metrics['application_metrics']['resources'] = {
                'user_time': usage.ru_utime,
                'system_time': usage.ru_stime,
                'max_memory_kb': usage.ru_maxrss,
                'page_faults_major': usage.ru_majflt,
                'page_faults_minor': usage.ru_minflt,
                'context_switches_voluntary': usage.ru_nvcsw,
                'context_switches_involuntary': usage.ru_nivcsw,
                'block_input_ops': usage.ru_inblock,
                'block_output_ops': usage.ru_oublock
            }

            # Python-specific metrics
            import gc
            metrics['application_metrics']['python'] = {
                'garbage_collections': gc.get_count(),
                'garbage_objects': len(gc.get_objects()),
                'reference_cycles': len(gc.garbage)
            }

            # Thread information
            import threading
            metrics['application_metrics']['threading'] = {
                'active_threads': threading.active_count(),
                'main_thread_alive': threading.main_thread().is_alive()
            }

        except ImportError:
            metrics['application_metrics']['error'] = 'Required modules not available'
        except Exception as e:
            metrics['application_metrics']['error'] = str(e)

        return metrics

    def _get_performance_trends(self) -> Dict[str, Any]:
        """Get performance trends and historical data."""
        metrics = {'trends': {}}

        try:
            # This would typically read from a performance history file
            # For now, we'll simulate trend data
            current_time = datetime.now()

            # Simulate historical CPU usage (last 24 hours)
            cpu_trend = []
            for i in range(24):
                timestamp = current_time - timedelta(hours=i)
                # Simulate CPU usage between 10-80%
                cpu_usage = 30 + (i * 2) % 50
                cpu_trend.append({
                    'timestamp': timestamp.isoformat(),
                    'cpu_percent': cpu_usage
                })

            # Simulate memory usage trend
            memory_trend = []
            for i in range(24):
                timestamp = current_time - timedelta(hours=i)
                memory_usage = 40 + (i * 1.5) % 30
                memory_trend.append({
                    'timestamp': timestamp.isoformat(),
                    'memory_percent': memory_usage
                })

            metrics['trends'] = {
                'cpu_24h': cpu_trend[::-1],  # Reverse to show oldest first
                'memory_24h': memory_trend[::-1],
                'data_points': len(cpu_trend),
                'period': '24 hours',
                'note': 'Simulated data - implement persistent storage for real trends'
            }

        except Exception as e:
            metrics['trends']['error'] = str(e)

        return metrics

    def _get_performance_alerts(self) -> Dict[str, Any]:
        """Get performance alerts and thresholds."""
        metrics = {'alerts': {}}

        try:
            import psutil

            # Define thresholds
            thresholds = {
                'cpu_warning': 70,
                'cpu_critical': 90,
                'memory_warning': 80,
                'memory_critical': 95,
                'disk_warning': 85,
                'disk_critical': 95
            }

            alerts = []

            # Check CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            if cpu_percent >= thresholds['cpu_critical']:
                alerts.append({
                    'type': 'CPU',
                    'level': 'CRITICAL',
                    'message': f'CPU usage is critically high: {cpu_percent}%',
                    'value': cpu_percent,
                    'threshold': thresholds['cpu_critical']
                })
            elif cpu_percent >= thresholds['cpu_warning']:
                alerts.append({
                    'type': 'CPU',
                    'level': 'WARNING',
                    'message': f'CPU usage is high: {cpu_percent}%',
                    'value': cpu_percent,
                    'threshold': thresholds['cpu_warning']
                })

            # Check memory usage
            memory = psutil.virtual_memory()
            if memory.percent >= thresholds['memory_critical']:
                alerts.append({
                    'type': 'MEMORY',
                    'level': 'CRITICAL',
                    'message': f'Memory usage is critically high: {memory.percent}%',
                    'value': memory.percent,
                    'threshold': thresholds['memory_critical']
                })
            elif memory.percent >= thresholds['memory_warning']:
                alerts.append({
                    'type': 'MEMORY',
                    'level': 'WARNING',
                    'message': f'Memory usage is high: {memory.percent}%',
                    'value': memory.percent,
                    'threshold': thresholds['memory_warning']
                })

            # Check disk usage
            disk = psutil.disk_usage('/')
            disk_percent = (disk.used / disk.total) * 100
            if disk_percent >= thresholds['disk_critical']:
                alerts.append({
                    'type': 'DISK',
                    'level': 'CRITICAL',
                    'message': f'Disk usage is critically high: {disk_percent:.1f}%',
                    'value': disk_percent,
                    'threshold': thresholds['disk_critical']
                })
            elif disk_percent >= thresholds['disk_warning']:
                alerts.append({
                    'type': 'DISK',
                    'level': 'WARNING',
                    'message': f'Disk usage is high: {disk_percent:.1f}%',
                    'value': disk_percent,
                    'threshold': thresholds['disk_warning']
                })

            metrics['alerts'] = {
                'active_alerts': alerts,
                'alert_count': len(alerts),
                'thresholds': thresholds,
                'last_check': datetime.now().isoformat()
            }

        except ImportError:
            metrics['alerts']['error'] = 'psutil not available'
        except Exception as e:
            metrics['alerts']['error'] = str(e)

        return metrics

    # Backup-related methods
    def get_backup_schedule(self) -> Dict[str, Any]:
        """Get current backup schedule configuration."""
        if not self.developer_auth.is_developer_authenticated():
            raise PermissionError("Developer authentication required")

        try:
            from apps.developer.backup_manager import BackupManager
            backup_manager = BackupManager(self)
            return backup_manager.get_schedule_info()
        except Exception as e:
            return {'error': str(e)}

    def enable_backup_schedule(self, frequency: str = 'daily', backup_time: str = '02:00',
                             backup_types: Optional[list] = None, encryption_enabled: bool = False,
                             retention_days: int = 30, max_backups: int = 50) -> Dict[str, Any]:
        """Enable automatic backup schedule."""
        if not self.developer_auth.is_developer_authenticated():
            raise PermissionError("Developer authentication required")

        try:
            from apps.developer.backup_manager import BackupManager
            backup_manager = BackupManager(self)

            # Update schedule config with all parameters
            backup_manager.schedule_config.update({
                'enabled': True,
                'frequency': frequency,
                'backup_time': backup_time,
                'backup_types': backup_types or ['full'],
                'encryption_enabled': encryption_enabled,
                'retention_days': retention_days,
                'max_backups': max_backups
            })

            return backup_manager.enable_schedule(frequency, backup_time, backup_types)
        except Exception as e:
            return {'error': str(e)}

    def disable_backup_schedule(self) -> Dict[str, Any]:
        """Disable automatic backup schedule."""
        if not self.developer_auth.is_developer_authenticated():
            raise PermissionError("Developer authentication required")

        try:
            from apps.developer.backup_manager import BackupManager
            backup_manager = BackupManager(self)
            return backup_manager.disable_schedule()
        except Exception as e:
            return {'error': str(e)}

    def set_backup_frequency(self, frequency: str) -> Dict[str, Any]:
        """Set backup frequency."""
        if not self.developer_auth.is_developer_authenticated():
            raise PermissionError("Developer authentication required")

        try:
            from apps.developer.backup_manager import BackupManager
            backup_manager = BackupManager(self)
            return backup_manager.set_frequency(frequency)
        except Exception as e:
            return {'error': str(e)}

    def set_backup_time(self, backup_time: str) -> Dict[str, Any]:
        """Set backup time."""
        if not self.developer_auth.is_developer_authenticated():
            raise PermissionError("Developer authentication required")

        try:
            from apps.developer.backup_manager import BackupManager
            backup_manager = BackupManager(self)
            return backup_manager.set_backup_time(backup_time)
        except Exception as e:
            return {'error': str(e)}

    def set_backup_types(self, backup_types: list) -> Dict[str, Any]:
        """Set backup types."""
        if not self.developer_auth.is_developer_authenticated():
            raise PermissionError("Developer authentication required")

        try:
            from apps.developer.backup_manager import BackupManager
            backup_manager = BackupManager(self)
            return backup_manager.set_backup_types(backup_types)
        except Exception as e:
            return {'error': str(e)}

    def get_backup_history(self) -> Dict[str, Any]:
        """Get backup history."""
        if not self.developer_auth.is_developer_authenticated():
            raise PermissionError("Developer authentication required")

        try:
            from apps.developer.backup_manager import BackupManager
            backup_manager = BackupManager(self)
            history = backup_manager.get_backup_history()
            return {'history': history}
        except Exception as e:
            return {'error': str(e)}

    def run_backup_now(self, backup_type: str = 'full') -> Dict[str, Any]:
        """Run a backup immediately."""
        if not self.developer_auth.is_developer_authenticated():
            raise PermissionError("Developer authentication required")

        try:
            from apps.developer.backup_manager import BackupManager
            backup_manager = BackupManager(self)

            if backup_type == 'full':
                return backup_manager.create_full_backup()
            elif backup_type == 'user':
                return backup_manager.create_user_backup()
            elif backup_type == 'database':
                return backup_manager.create_database_backup()
            else:
                return {'error': f'Unsupported backup type: {backup_type}'}
        except Exception as e:
            return {'error': str(e)}

    def list_backups(self) -> Dict[str, Any]:
        """List all available backups."""
        if not self.developer_auth.is_developer_authenticated():
            raise PermissionError("Developer authentication required")

        try:
            from apps.developer.backup_manager import BackupManager
            backup_manager = BackupManager(self)
            backups = backup_manager.list_backups()
            return {'backups': backups}
        except Exception as e:
            return {'error': str(e)}

    def delete_backup(self, filename: str) -> Dict[str, Any]:
        """Delete a backup file."""
        if not self.developer_auth.is_developer_authenticated():
            raise PermissionError("Developer authentication required")

        try:
            import os
            from apps.developer.backup_manager import BACKUP_DIR

            backup_path = os.path.join(BACKUP_DIR, filename)
            if os.path.exists(backup_path):
                os.remove(backup_path)
                return {'success': True, 'message': f'Backup {filename} deleted successfully'}
            else:
                return {'error': f'Backup file {filename} not found'}
        except Exception as e:
            return {'error': str(e)}

    def restore_backup(self, filename: str, encryption_key: Optional[str] = None) -> Dict[str, Any]:
        """Restore from a backup file."""
        if not self.developer_auth.is_developer_authenticated():
            raise PermissionError("Developer authentication required")

        try:
            from apps.developer.backup_manager import BackupManager
            backup_manager = BackupManager(self)
            return backup_manager.restore_backup(filename, encryption_key)
        except Exception as e:
            return {'error': str(e)}

    def create_backup(self, backup_type: str = 'full', backup_name: str = '') -> Dict[str, Any]:
        """Create a backup."""
        if not self.developer_auth.is_developer_authenticated():
            raise PermissionError("Developer authentication required")

        try:
            from apps.developer.backup_manager import BackupManager
            backup_manager = BackupManager(self)

            if backup_type == 'full':
                return backup_manager.create_full_backup()
            elif backup_type == 'user':
                return backup_manager.create_user_backup()
            elif backup_type == 'database':
                return backup_manager.create_database_backup()
            else:
                return {'error': f'Unsupported backup type: {backup_type}'}
        except Exception as e:
            return {'error': str(e)}
# EcoCycle Developer Mode

## Overview

EcoCycle Developer Mode provides advanced debugging and system management tools for developers and system administrators. This feature allows authorized users to access elevated privileges for troubleshooting, data management, and system diagnostics.

## Features

### 🔧 System Diagnostics
- Comprehensive system health checks
- Environment variable analysis
- Database status and integrity checks
- File system validation
- Log file analysis with error detection

### 🗄️ Database Management
- View all database tables
- Inspect table contents and structure
- Table statistics and row counts
- Database integrity verification

### 👥 User Data Management (Coming Soon)
- View and edit user profiles
- Manage user statistics
- Reset user data
- User account administration

### 🗂️ Cache Management (Coming Soon)
- View cache contents
- Clear specific or all caches
- Cache performance metrics
- Cache optimization tools

### 📧 Email System Testing (Coming Soon)
- Test SMTP configuration
- Send test verification emails
- Validate email templates
- Email delivery diagnostics

### ⚙️ Configuration Management (Coming Soon)
- View current configuration
- Modify application settings
- Feature flag management
- API key administration

### 📊 Performance Monitoring (Coming Soon)
- System resource usage
- Application performance metrics
- Memory and CPU monitoring
- Performance bottleneck identification

### 📋 Log Analysis (Coming Soon)
- Real-time log viewing
- Error pattern analysis
- Log filtering and search
- Log rotation management

## Setup

### 1. Generate Developer Credentials

Run the setup script to generate secure developer credentials:

```bash
python scripts/setup_developer_mode.py
```

This script will:
- Generate a secure password hash
- Create environment variables
- Optionally create/update a `.env` file
- Set appropriate file permissions

### 2. Environment Variables

Set the following environment variables:

```bash
export DEVELOPER_MODE_ENABLED=true
export DEVELOPER_USERNAME=dev_admin
export DEVELOPER_PASSWORD_HASH=<generated_hash>
```

Or add them to your `.env` file:

```env
DEVELOPER_MODE_ENABLED=true
DEVELOPER_USERNAME=dev_admin
DEVELOPER_PASSWORD_HASH=<generated_hash>
```

### 3. Manual Setup (Alternative)

If you prefer to set up credentials manually:

```python
from auth.developer_auth import DeveloperAuth

# Generate password hash
password_hash = DeveloperAuth.generate_password_hash("your_secure_password")
print(f"DEVELOPER_PASSWORD_HASH={password_hash}")
```

## Usage

### Accessing Developer Mode

1. Start the EcoCycle application
2. From the authentication menu, select "Developer Mode"
3. Enter your developer credentials
4. Access the developer tools dashboard

### Developer Tools Menu

```
🔧 DEVELOPER MODE ACTIVE
⚠️  You have elevated system privileges

📊 System & Monitoring
1. System Diagnostics
2. Performance Monitoring
3. Log Analysis
4. System Health Dashboard

🗄️ Data Management
5. Database Management
6. User Data Management
7. Cache Management
8. Export System Data

⚙️ Configuration & Testing
9. Configuration Management
10. Email System Testing
11. API Testing Tools
12. Security Audit

🔐 Session & Security
13. Session Management
14. Backup & Restore

🚪 Exit
0. Exit Developer Mode
```

### Session Management

- Developer sessions timeout after 30 minutes of inactivity
- Sessions are automatically extended on activity
- Clear visual indicators show when in developer mode
- All developer actions are logged for audit purposes

## Security Features

### 🔐 Secure Authentication
- Password hashing with PBKDF2 and salt
- Environment variable-based credential storage
- No hardcoded credentials in source code
- Session timeout protection

### 📝 Audit Logging
- All developer actions are logged
- Separate audit log file (`Logs/developer_audit.log`)
- Timestamps and action details
- Failed authentication attempts tracked

### 🛡️ Access Control
- Developer mode must be explicitly enabled
- Credentials stored securely outside source code
- Clear warnings about elevated privileges
- Non-interference with normal user operations

### 🔍 Visual Indicators
- Clear developer mode indicators in UI
- Warning messages about elevated privileges
- Session status and timeout information
- Distinct styling for developer interface

## Configuration

### Developer Settings

The developer mode configuration can be customized in `config/config_manager.py`:

```python
'developer': {
    'enabled': os.environ.get('DEVELOPER_MODE_ENABLED', 'false').lower() == 'true',
    'username': os.environ.get('DEVELOPER_USERNAME', 'dev_admin'),
    'password_hash': os.environ.get('DEVELOPER_PASSWORD_HASH', ''),
    'session_timeout': 1800,  # 30 minutes
    'audit_logging': True,
    'bypass_restrictions': True,
    'debug_level': 'DEBUG',
}
```

### Customization Options

- **session_timeout**: Session timeout in seconds (default: 1800)
- **audit_logging**: Enable/disable audit logging (default: True)
- **bypass_restrictions**: Allow bypassing normal user restrictions (default: True)
- **debug_level**: Logging level for developer actions (default: DEBUG)

## Troubleshooting

### Common Issues

1. **Developer mode not available**
   - Ensure `DEVELOPER_MODE_ENABLED=true`
   - Check that `DEVELOPER_PASSWORD_HASH` is set
   - Verify environment variables are loaded

2. **Authentication fails**
   - Verify password hash is correct
   - Check username matches `DEVELOPER_USERNAME`
   - Ensure no typos in environment variables

3. **Session timeout issues**
   - Default timeout is 30 minutes
   - Sessions extend automatically on activity
   - Check system clock for time drift

4. **Missing features**
   - Some features are marked "Coming Soon"
   - Core diagnostics and database tools are available
   - Additional features will be added in future updates

### Debug Information

Enable debug logging to troubleshoot issues:

```python
import logging
logging.getLogger('auth.developer_auth').setLevel(logging.DEBUG)
```

## Best Practices

### 🔒 Security
- Use strong passwords (12+ characters)
- Regularly rotate developer credentials
- Limit access to authorized personnel only
- Monitor audit logs for suspicious activity

### 🛠️ Usage
- Exit developer mode when not needed
- Use system diagnostics before making changes
- Create backups before data modifications
- Document any system changes made

### 📊 Monitoring
- Review audit logs regularly
- Monitor session activity
- Check for failed authentication attempts
- Validate system integrity after changes

## API Reference

### DeveloperAuth Class

```python
from auth.developer_auth import DeveloperAuth

dev_auth = DeveloperAuth()

# Check if enabled
if dev_auth.is_enabled():
    # Authenticate
    if dev_auth.authenticate_developer():
        # Access developer tools
        pass
```

### DeveloperTools Class

```python
from apps.developer.developer_tools import DeveloperTools

dev_tools = DeveloperTools(dev_auth)

# System diagnostics
diagnostics = dev_tools.system_diagnostics()

# Database operations
db_data = dev_tools.view_database_contents()

# Cache management
cache_info = dev_tools.manage_cache('view')
```

## Contributing

To add new developer tools:

1. Add methods to `DeveloperTools` class
2. Update `DeveloperUI` for interface
3. Add menu options in `UserManager._run_developer_mode()`
4. Update this documentation

## License

This feature is part of the EcoCycle project and follows the same license terms.

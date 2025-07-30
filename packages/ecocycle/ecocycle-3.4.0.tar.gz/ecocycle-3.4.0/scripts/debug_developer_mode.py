#!/usr/bin/env python3
"""
EcoCycle - Developer Mode Debug Script
Helps diagnose issues with developer mode configuration.
"""
import os
import sys

# Add the parent directory to the path so we can import from auth
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def check_environment_variables():
    """Check if developer mode environment variables are set."""
    print("🔍 Checking Environment Variables")
    print("=" * 50)
    
    required_vars = [
        'DEVELOPER_MODE_ENABLED',
        'DEVELOPER_USERNAME', 
        'DEVELOPER_PASSWORD_HASH'
    ]
    
    all_set = True
    for var in required_vars:
        value = os.environ.get(var)
        if value:
            if var == 'DEVELOPER_PASSWORD_HASH':
                # Don't show the full hash for security
                display_value = f"{value[:20]}..." if len(value) > 20 else value
            else:
                display_value = value
            print(f"✅ {var} = {display_value}")
        else:
            print(f"❌ {var} = NOT SET")
            all_set = False
    
    return all_set

def check_env_file():
    """Check if .env file exists and contains developer variables."""
    print("\n🔍 Checking .env File")
    print("=" * 50)
    
    env_file_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.env')
    
    if not os.path.exists(env_file_path):
        print(f"❌ .env file not found at: {env_file_path}")
        return False
    
    print(f"✅ .env file found at: {env_file_path}")
    
    try:
        with open(env_file_path, 'r') as f:
            content = f.read()
        
        required_vars = ['DEVELOPER_MODE_ENABLED', 'DEVELOPER_USERNAME', 'DEVELOPER_PASSWORD_HASH']
        found_vars = []
        
        for line in content.split('\n'):
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key = line.split('=')[0]
                if key in required_vars:
                    found_vars.append(key)
                    if key == 'DEVELOPER_PASSWORD_HASH':
                        value = line.split('=', 1)[1]
                        display_value = f"{value[:20]}..." if len(value) > 20 else value
                    else:
                        display_value = line.split('=', 1)[1]
                    print(f"✅ Found {key} = {display_value}")
        
        missing_vars = set(required_vars) - set(found_vars)
        if missing_vars:
            print(f"❌ Missing variables in .env file: {', '.join(missing_vars)}")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Error reading .env file: {e}")
        return False

def load_env_file():
    """Try to load .env file manually."""
    print("\n🔄 Attempting to Load .env File")
    print("=" * 50)
    
    env_file_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.env')
    
    if not os.path.exists(env_file_path):
        print("❌ No .env file to load")
        return False
    
    try:
        with open(env_file_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key] = value
                    if key.startswith('DEVELOPER_'):
                        if key == 'DEVELOPER_PASSWORD_HASH':
                            display_value = f"{value[:20]}..." if len(value) > 20 else value
                        else:
                            display_value = value
                        print(f"✅ Loaded {key} = {display_value}")
        
        print("✅ .env file loaded successfully")
        return True
        
    except Exception as e:
        print(f"❌ Error loading .env file: {e}")
        return False

def test_developer_auth():
    """Test the developer authentication system."""
    print("\n🧪 Testing Developer Authentication")
    print("=" * 50)
    
    try:
        from auth.developer_auth import DeveloperAuth
        
        dev_auth = DeveloperAuth()
        
        print(f"Enabled: {dev_auth.enabled}")
        print(f"Username: {dev_auth.dev_username}")
        print(f"Password Hash Set: {'Yes' if dev_auth.dev_password_hash else 'No'}")
        print(f"Session Timeout: {dev_auth.session_timeout}")
        print(f"Audit Logging: {dev_auth.audit_logging}")
        
        if dev_auth.is_enabled():
            print("✅ Developer mode is properly configured!")
            return True
        else:
            print("❌ Developer mode is not enabled or configured properly")
            
            # Detailed diagnosis
            if not dev_auth.enabled:
                print("   - DEVELOPER_MODE_ENABLED is not set to 'true'")
            if not dev_auth.dev_password_hash:
                print("   - DEVELOPER_PASSWORD_HASH is not set or empty")
            
            return False
            
    except ImportError as e:
        print(f"❌ Could not import DeveloperAuth: {e}")
        return False
    except Exception as e:
        print(f"❌ Error testing developer auth: {e}")
        return False

def suggest_fixes():
    """Suggest fixes for common issues."""
    print("\n💡 Suggested Fixes")
    print("=" * 50)
    
    print("1. If .env file exists but variables aren't loaded:")
    print("   - Make sure you're running from the project root directory")
    print("   - Try loading .env manually with: python-dotenv")
    print("   - Or export variables directly in your shell")
    print()
    
    print("2. If .env file doesn't exist:")
    print("   - Run: python scripts/setup_developer_mode.py")
    print("   - Choose 'y' when asked to create .env file")
    print()
    
    print("3. Manual environment variable setup:")
    print("   export DEVELOPER_MODE_ENABLED=true")
    print("   export DEVELOPER_USERNAME=dev_admin")
    print("   export DEVELOPER_PASSWORD_HASH=<your_hash>")
    print()
    
    print("4. If using python-dotenv:")
    print("   pip install python-dotenv")
    print("   Then add to your main.py:")
    print("   from dotenv import load_dotenv")
    print("   load_dotenv()")

def main():
    """Main diagnostic function."""
    print("🔧 EcoCycle Developer Mode Diagnostics")
    print("=" * 60)
    print()
    
    # Check current environment variables
    env_vars_ok = check_environment_variables()
    
    # Check .env file
    env_file_ok = check_env_file()
    
    # If env vars not set but .env file exists, try loading it
    if not env_vars_ok and env_file_ok:
        print("\n🔄 Environment variables not set, but .env file found. Attempting to load...")
        if load_env_file():
            env_vars_ok = check_environment_variables()
    
    # Test developer authentication
    auth_ok = test_developer_auth()
    
    # Summary
    print("\n📊 Diagnostic Summary")
    print("=" * 50)
    print(f"Environment Variables: {'✅ OK' if env_vars_ok else '❌ MISSING'}")
    print(f".env File: {'✅ OK' if env_file_ok else '❌ MISSING/INVALID'}")
    print(f"Developer Auth: {'✅ OK' if auth_ok else '❌ FAILED'}")
    
    if not auth_ok:
        suggest_fixes()
    else:
        print("\n🎉 Developer mode is properly configured!")
        print("You should be able to access it from the authentication menu.")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nDiagnostics cancelled by user.")
    except Exception as e:
        print(f"\n❌ Diagnostics failed: {e}")
        sys.exit(1)

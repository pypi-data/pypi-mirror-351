#!/usr/bin/env python3
"""
EcoCycle - Developer Password Test Script
Test and update developer password if needed.
"""
import os
import sys
import getpass

# Add the parent directory to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
from auth.developer_auth import DeveloperAuth

def main():
    """Test developer password and optionally update it."""
    print("🔧 EcoCycle Developer Password Test")
    print("=" * 50)
    
    # Load environment variables
    load_dotenv()
    
    # Get current hash from environment
    current_hash = os.environ.get('DEVELOPER_PASSWORD_HASH')
    username = os.environ.get('DEVELOPER_USERNAME', 'shirishdev')
    
    if not current_hash:
        print("❌ No developer password hash found in environment.")
        print("Please run: python scripts/setup_developer_mode.py")
        return
    
    print(f"Current developer username: {username}")
    print(f"Password hash found: {current_hash[:20]}...")
    print()
    
    # Test password verification
    dev_auth = DeveloperAuth()
    
    print("Testing password verification...")
    test_passwords = [
        "test_password",
        "developer123",
        "dev_password",
        "shirishdev123",
        "ecocycle_dev",
        "admin123"
    ]
    
    print("Trying common passwords...")
    for password in test_passwords:
        if dev_auth._verify_password(password, current_hash):
            print(f"✅ Password found: {password}")
            return
    
    print("❌ None of the common passwords worked.")
    print()
    
    # Ask if user wants to set a new password
    response = input("Would you like to set a new developer password? (y/N): ").strip().lower()
    if response == 'y':
        set_new_password()
    else:
        print("You can manually test passwords or run setup_developer_mode.py to create new credentials.")

def set_new_password():
    """Set a new developer password."""
    print("\n🔐 Setting New Developer Password")
    print("-" * 40)
    
    while True:
        password = getpass.getpass("Enter new developer password: ")
        if len(password) < 8:
            print("⚠️  Password should be at least 8 characters.")
            continue
        
        confirm = getpass.getpass("Confirm password: ")
        if password != confirm:
            print("❌ Passwords don't match. Try again.")
            continue
        
        break
    
    # Generate new hash
    new_hash = DeveloperAuth.generate_password_hash(password)
    
    print("\n✅ New password hash generated!")
    print(f"DEVELOPER_PASSWORD_HASH={new_hash}")
    
    # Update .env file
    env_file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.env')
    
    try:
        # Read current .env file
        with open(env_file, 'r') as f:
            lines = f.readlines()
        
        # Update the password hash line
        updated = False
        for i, line in enumerate(lines):
            if line.startswith('DEVELOPER_PASSWORD_HASH='):
                lines[i] = f"DEVELOPER_PASSWORD_HASH={new_hash}\n"
                updated = True
                break
        
        if not updated:
            # Add the line if it doesn't exist
            lines.append(f"DEVELOPER_PASSWORD_HASH={new_hash}\n")
        
        # Write back to file
        with open(env_file, 'w') as f:
            f.writelines(lines)
        
        print(f"✅ Updated .env file: {env_file}")
        print("\n🎉 Developer password updated successfully!")
        print("You can now use the new password to access developer mode.")
        
    except Exception as e:
        print(f"❌ Error updating .env file: {e}")
        print("Please manually update the DEVELOPER_PASSWORD_HASH in your .env file.")

def test_specific_password():
    """Test a specific password."""
    load_dotenv()
    current_hash = os.environ.get('DEVELOPER_PASSWORD_HASH')
    
    if not current_hash:
        print("❌ No password hash found.")
        return
    
    password = getpass.getpass("Enter password to test: ")
    dev_auth = DeveloperAuth()
    
    if dev_auth._verify_password(password, current_hash):
        print("✅ Password is correct!")
    else:
        print("❌ Password is incorrect.")

if __name__ == "__main__":
    try:
        if len(sys.argv) > 1 and sys.argv[1] == "test":
            test_specific_password()
        else:
            main()
    except KeyboardInterrupt:
        print("\n\nOperation cancelled.")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)

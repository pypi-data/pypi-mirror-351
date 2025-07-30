#!/usr/bin/env python3
"""
Test script for refactored user management modules.
This script tests the basic functionality of the new modular structure.
"""
import sys
import os
import tempfile
import shutil

# Add the project root to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from auth.user_management.password_security import PasswordSecurity
from auth.user_management.session_manager import SessionManager
from auth.user_management.user_data_manager import UserDataManager
from auth.user_management.user_registration import UserRegistration
from auth.user_management.auth_handler import AuthHandler


def test_password_security():
    """Test the PasswordSecurity module."""
    print("Testing PasswordSecurity module...")
    
    ps = PasswordSecurity()
    
    # Test salt generation
    salt = ps.generate_salt()
    assert len(salt) > 0, "Salt should not be empty"
    print(f"✓ Salt generated: {salt[:10]}...")
    
    # Test password hashing
    password = "TestPassword123!"
    password_hash = ps.hash_password(password, salt)
    assert len(password_hash) > 0, "Password hash should not be empty"
    print(f"✓ Password hashed: {password_hash[:10]}...")
    
    # Test password verification
    assert ps.verify_password(password, password_hash, salt), "Password verification should succeed"
    assert not ps.verify_password("WrongPassword", password_hash, salt), "Wrong password should fail"
    print("✓ Password verification works correctly")
    
    # Test password strength checking
    strength = ps.check_password_strength(password)
    assert strength['is_valid'], "Strong password should be valid"
    assert strength['strength_score'] > 3, "Strong password should have high score"
    print(f"✓ Password strength analysis: {strength['strength_text']}")
    
    print("✓ PasswordSecurity module tests passed!\n")


def test_session_manager():
    """Test the SessionManager module."""
    print("Testing SessionManager module...")
    
    # Set up environment variable for testing
    os.environ["SESSION_SECRET_KEY"] = "test_secret_key_for_testing_only"
    
    sm = SessionManager()
    
    # Test session secret retrieval
    secret = sm.get_session_secret()
    assert secret is not None, "Session secret should be available"
    print("✓ Session secret retrieved")
    
    # Test verifier calculation
    username = "testuser"
    verifier = sm.calculate_verifier(username)
    assert verifier is not None, "Verifier should be calculated"
    print(f"✓ Verifier calculated: {verifier[:10]}...")
    
    # Test session save/load (using temporary file)
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as tmp:
        # Temporarily override the session file path
        original_session_file = SessionManager.__dict__.get('SESSION_FILE')
        import auth.user_management.session_manager as sm_module
        sm_module.SESSION_FILE = tmp.name
        
        try:
            # Test saving session
            assert sm.save_session(username), "Session save should succeed"
            print("✓ Session saved")
            
            # Test loading session
            loaded_user = sm.load_session()
            assert loaded_user == username, f"Loaded user should be {username}, got {loaded_user}"
            print("✓ Session loaded correctly")
            
            # Test clearing session
            sm.clear_session(username)
            cleared_user = sm.load_session()
            assert cleared_user is None, "Session should be cleared"
            print("✓ Session cleared correctly")
            
        finally:
            # Clean up
            if os.path.exists(tmp.name):
                os.unlink(tmp.name)
            if original_session_file:
                sm_module.SESSION_FILE = original_session_file
    
    print("✓ SessionManager module tests passed!\n")


def test_user_data_manager():
    """Test the UserDataManager module."""
    print("Testing UserDataManager module...")
    
    # Create temporary directory for testing
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create a temporary users file
        temp_users_file = os.path.join(temp_dir, 'test_users.json')
        
        # Temporarily override the users file path
        import auth.user_management.user_data_manager as udm_module
        original_users_file = udm_module.DEFAULT_USERS_FILE
        udm_module.DEFAULT_USERS_FILE = temp_users_file
        
        try:
            udm = UserDataManager()
            
            # Test creating guest user
            guest_user = udm.create_guest_user(1)
            assert guest_user['username'] == 'guest1', "Guest user should have correct username"
            assert guest_user['is_guest'] is True, "Guest user should be marked as guest"
            print("✓ Guest user created correctly")
            
            # Test user data operations
            test_users = {
                'testuser': {
                    'username': 'testuser',
                    'name': 'Test User',
                    'email': 'test@example.com',
                    'stats': {'total_trips': 0, 'total_distance': 0.0, 'total_co2_saved': 0.0, 'total_calories': 0, 'trips': []},
                    'preferences': {}
                }
            }
            
            # Test saving users
            assert udm.save_users(test_users), "Users save should succeed"
            print("✓ Users saved successfully")
            
            # Test loading users
            loaded_users = udm.load_users()
            assert 'testuser' in loaded_users, "Test user should be in loaded users"
            assert loaded_users['testuser']['name'] == 'Test User', "User data should be preserved"
            print("✓ Users loaded successfully")
            
            # Test updating user stats
            user_data = loaded_users['testuser']
            assert udm.update_user_stats(user_data, 10.5, 2.5, 300, 45.0), "Stats update should succeed"
            assert user_data['stats']['total_trips'] == 1, "Trip count should be updated"
            assert user_data['stats']['total_distance'] == 10.5, "Distance should be updated"
            print("✓ User stats updated correctly")
            
            # Test updating user preferences
            assert udm.update_user_preference(user_data, 'theme', 'dark'), "Preference update should succeed"
            assert udm.get_user_preference(user_data, 'theme') == 'dark', "Preference should be retrievable"
            print("✓ User preferences updated correctly")
            
        finally:
            # Restore original users file path
            udm_module.DEFAULT_USERS_FILE = original_users_file
    
    print("✓ UserDataManager module tests passed!\n")


def test_user_registration():
    """Test the UserRegistration module (basic validation only)."""
    print("Testing UserRegistration module...")
    
    ur = UserRegistration()
    
    # Test username validation
    validation = ur._validate_username("testuser", {})
    assert validation['valid'], "Valid username should pass validation"
    print("✓ Username validation works")
    
    validation = ur._validate_username("", {})
    assert not validation['valid'], "Empty username should fail validation"
    print("✓ Empty username validation works")
    
    validation = ur._validate_username("admin", {})
    assert not validation['valid'], "Reserved username should fail validation"
    print("✓ Reserved username validation works")
    
    # Test password strength display (just ensure it doesn't crash)
    analysis = {'strength_score': 4, 'strength_text': 'Strong'}
    ur._display_password_strength(analysis)  # Should not raise exception
    print("✓ Password strength display works")
    
    print("✓ UserRegistration module tests passed!\n")


def test_auth_handler():
    """Test the AuthHandler module (basic functionality)."""
    print("Testing AuthHandler module...")
    
    ah = AuthHandler()
    
    # Test credential verification with mock users
    test_users = {
        'testuser': {
            'password_hash': 'dGVzdGhhc2g=',  # base64 encoded 'testhash'
            'salt': 'dGVzdHNhbHQ='  # base64 encoded 'testsalt'
        }
    }
    
    # This will fail because we're not using the actual password hashing
    # but it tests that the method doesn't crash
    result = ah.verify_credentials('testuser', 'wrongpassword', test_users)
    assert not result, "Wrong password should fail verification"
    print("✓ Credential verification works")
    
    # Test email verification check
    test_users_with_verification = {
        'testuser': {
            'email_verified': False,
            'preferences': {'require_email_verification': True}
        }
    }
    
    requires_verification = ah.check_email_verification_required('testuser', test_users_with_verification)
    assert requires_verification, "Unverified user should require verification"
    print("✓ Email verification check works")
    
    print("✓ AuthHandler module tests passed!\n")


def main():
    """Run all tests."""
    print("=" * 60)
    print("Testing Refactored User Management Modules")
    print("=" * 60)
    print()
    
    try:
        test_password_security()
        test_session_manager()
        test_user_data_manager()
        test_user_registration()
        test_auth_handler()
        
        print("=" * 60)
        print("🎉 All tests passed! The refactored modules are working correctly.")
        print("=" * 60)
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

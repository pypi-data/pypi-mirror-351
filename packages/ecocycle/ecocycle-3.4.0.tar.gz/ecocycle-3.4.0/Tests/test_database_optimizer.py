#!/usr/bin/env python3
"""
Test script for the database optimizer module.
This script tests the functionality of the database optimizer.
"""
import os
import sys
import unittest
from unittest.mock import patch, MagicMock
import tempfile
import sqlite3
import time

# Add the parent directory to the path so we can import the module
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import the module to test
import core.database_optimizer as db_optimizer
from core.database_manager import execute_query


class TestDatabaseOptimizer(unittest.TestCase):
    """Test cases for the database optimizer module."""

    def setUp(self):
        """Set up the test environment."""
        # Create a temporary database file
        self.temp_db_fd, self.temp_db_path = tempfile.mkstemp(suffix='.db')
        
        # Override the database file path
        self.original_db_file = db_optimizer.DATABASE_FILE
        db_optimizer.DATABASE_FILE = self.temp_db_path
        
        # Create a test database
        self.conn = sqlite3.connect(self.temp_db_path)
        self.create_test_database()
        
        # Clear the query cache
        db_optimizer.clear_query_cache()

    def tearDown(self):
        """Clean up after tests."""
        # Close the database connection
        if self.conn:
            self.conn.close()
        
        # Remove the temporary database file
        os.close(self.temp_db_fd)
        os.unlink(self.temp_db_path)
        
        # Restore the original database file path
        db_optimizer.DATABASE_FILE = self.original_db_file

    def create_test_database(self):
        """Create a test database with sample data."""
        # Create users table
        self.conn.execute('''
            CREATE TABLE users (
                id INTEGER PRIMARY KEY,
                username TEXT NOT NULL UNIQUE,
                email TEXT,
                password_hash TEXT,
                salt TEXT,
                google_id TEXT,
                is_admin INTEGER NOT NULL,
                is_guest INTEGER NOT NULL,
                registration_date TEXT,
                last_login_date TEXT,
                account_status TEXT DEFAULT 'active',
                email_verified INTEGER DEFAULT 0,
                guest_number INTEGER DEFAULT 0
            )
        ''')
        
        # Create preferences table
        self.conn.execute('''
            CREATE TABLE preferences (
                id INTEGER PRIMARY KEY,
                user_id INTEGER NOT NULL,
                key TEXT NOT NULL,
                value TEXT,
                last_updated TEXT,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        # Create trips table
        self.conn.execute('''
            CREATE TABLE trips (
                id INTEGER PRIMARY KEY,
                user_id INTEGER NOT NULL,
                date TEXT,
                distance REAL,
                duration REAL,
                co2_saved REAL,
                calories INTEGER,
                route_data TEXT,
                weather_data TEXT,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        # Insert sample data
        self.conn.execute('''
            INSERT INTO users (username, email, password_hash, salt, google_id, is_admin, is_guest, registration_date)
            VALUES ('testuser', 'test@example.com', 'hash', 'salt', NULL, 0, 0, '2023-01-01')
        ''')
        
        self.conn.execute('''
            INSERT INTO preferences (user_id, key, value, last_updated)
            VALUES (1, 'theme', 'dark', '2023-01-01')
        ''')
        
        self.conn.execute('''
            INSERT INTO trips (user_id, date, distance, duration, co2_saved, calories)
            VALUES (1, '2023-01-01', 10.5, 45.0, 2.0, 500)
        ''')
        
        self.conn.commit()

    def test_cached_query(self):
        """Test the cached_query function."""
        # First query should not be cached
        result1 = db_optimizer.cached_query("SELECT * FROM users WHERE id = ?", (1,), fetch_mode='one')
        self.assertIsNotNone(result1)
        
        # Second query should be cached
        with patch('core.database_manager.execute_query') as mock_execute:
            result2 = db_optimizer.cached_query("SELECT * FROM users WHERE id = ?", (1,), fetch_mode='one')
            # Check that execute_query was not called
            mock_execute.assert_not_called()
        
        # Check that the results are the same
        self.assertEqual(result1, result2)
        
        # Query with different parameters should not be cached
        with patch('core.database_manager.execute_query', return_value=None) as mock_execute:
            db_optimizer.cached_query("SELECT * FROM users WHERE id = ?", (2,), fetch_mode='one')
            # Check that execute_query was called
            mock_execute.assert_called_once()
        
        # Non-SELECT query should not be cached
        with patch('core.database_manager.execute_query', return_value=None) as mock_execute:
            db_optimizer.cached_query("UPDATE users SET username = ? WHERE id = ?", ('newuser', 1), fetch_mode=None)
            # Check that execute_query was called
            mock_execute.assert_called_once()
        
        # Test cache expiration
        result3 = db_optimizer.cached_query("SELECT * FROM users WHERE id = ?", (3,), max_age=0.1, fetch_mode='one')
        
        # Wait for cache to expire
        time.sleep(0.2)
        
        # Query should be executed again
        with patch('core.database_manager.execute_query', return_value=None) as mock_execute:
            db_optimizer.cached_query("SELECT * FROM users WHERE id = ?", (3,), max_age=0.1, fetch_mode='one')
            # Check that execute_query was called
            mock_execute.assert_called_once()

    def test_clear_query_cache(self):
        """Test the clear_query_cache function."""
        # Add some queries to the cache
        db_optimizer.cached_query("SELECT * FROM users WHERE id = ?", (1,), fetch_mode='one')
        db_optimizer.cached_query("SELECT * FROM users WHERE username = ?", ('testuser',), fetch_mode='one')
        
        # Clear the cache
        db_optimizer.clear_query_cache()
        
        # Check that the cache is empty
        self.assertEqual(len(db_optimizer._query_cache), 0)
        
        # Query should be executed again
        with patch('core.database_manager.execute_query', return_value=None) as mock_execute:
            db_optimizer.cached_query("SELECT * FROM users WHERE id = ?", (1,), fetch_mode='one')
            # Check that execute_query was called
            mock_execute.assert_called_once()

    def test_analyze_database(self):
        """Test the analyze_database function."""
        # Analyze the database
        analysis = db_optimizer.analyze_database()
        
        # Check that the analysis contains the expected keys
        self.assertIn('tables', analysis)
        self.assertIn('indexes', analysis)
        self.assertIn('missing_indexes', analysis)
        self.assertIn('unused_indexes', analysis)
        self.assertIn('fragmentation', analysis)
        self.assertIn('size', analysis)
        self.assertIn('recommendations', analysis)
        
        # Check that the tables were analyzed
        self.assertIn('users', analysis['tables'])
        self.assertIn('preferences', analysis['tables'])
        self.assertIn('trips', analysis['tables'])
        
        # Check that the row counts are correct
        self.assertEqual(analysis['tables']['users']['row_count'], 1)
        self.assertEqual(analysis['tables']['preferences']['row_count'], 1)
        self.assertEqual(analysis['tables']['trips']['row_count'], 1)

    def test_optimize_database(self):
        """Test the optimize_database function."""
        # Optimize the database
        results = db_optimizer.optimize_database()
        
        # Check that the results contain the expected keys
        self.assertIn('actions', results)
        self.assertIn('errors', results)
        
        # Check that ANALYZE was run
        self.assertIn("Updated database statistics with ANALYZE", results['actions'])

    def test_create_optimized_indexes(self):
        """Test the create_optimized_indexes function."""
        # Create optimized indexes
        results = db_optimizer.create_optimized_indexes()
        
        # Check that the results contain the expected keys
        self.assertIn('created_indexes', results)
        self.assertIn('errors', results)
        
        # Check that some indexes were created
        self.assertGreater(len(results['created_indexes']), 0)
        
        # Check that the indexes exist in the database
        cursor = self.conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='index' AND name LIKE 'idx_%'")
        indexes = cursor.fetchall()
        
        # Check that at least one index was created
        self.assertGreater(len(indexes), 0)

    def test_optimize_queries(self):
        """Test the optimize_queries function."""
        # Optimize queries
        results = db_optimizer.optimize_queries()
        
        # Check that the results contain the expected keys
        self.assertIn('optimized_queries', results)
        
        # Check that some queries were optimized
        self.assertGreater(len(results['optimized_queries']), 0)

    def test_get_database_stats(self):
        """Test the get_database_stats function."""
        # Get database stats
        stats = db_optimizer.get_database_stats()
        
        # Check that the stats contain the expected keys
        self.assertIn('size', stats)
        self.assertIn('tables', stats)
        self.assertIn('total_rows', stats)
        
        # Check that the tables were analyzed
        self.assertIn('users', stats['tables'])
        self.assertIn('preferences', stats['tables'])
        self.assertIn('trips', stats['tables'])
        
        # Check that the row counts are correct
        self.assertEqual(stats['tables']['users']['row_count'], 1)
        self.assertEqual(stats['tables']['preferences']['row_count'], 1)
        self.assertEqual(stats['tables']['trips']['row_count'], 1)
        
        # Check that the total row count is correct
        self.assertEqual(stats['total_rows'], 3)


if __name__ == '__main__':
    unittest.main()

#!/usr/bin/env python3
"""
EcoCycle - Database Optimizer Module
Provides optimization for database queries and data storage.
"""
import os
import time
import logging
import sqlite3
import json
from typing import Dict, List, Any, Optional, Tuple, Set, Union
from contextlib import contextmanager

# Import database manager
from core.database_manager import get_connection, execute_query, transaction

# Import config module for paths
try:
    import config.config as config
    # Use config module for log directory
    LOG_DIR = config.LOG_DIR
    DATABASE_FILE = config.DATABASE_FILE
except ImportError:
    # Fallback if config module is not available
    LOG_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'Logs')
    DATABASE_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'ecocycle.db')

# Configure logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(os.path.join(LOG_DIR, 'database_optimizer.log'))
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

# Constants
QUERY_CACHE_SIZE = 100
INDEX_THRESHOLD = 1000  # Number of rows before considering an index
VACUUM_THRESHOLD = 10 * 1024 * 1024  # 10MB threshold for vacuum
ANALYZE_INTERVAL = 24 * 60 * 60  # 24 hours in seconds
OPTIMIZE_INTERVAL = 7 * 24 * 60 * 60  # 7 days in seconds

# Query cache
_query_cache: Dict[str, Tuple[Any, float]] = {}


def cached_query(query: str, params: Tuple = (), max_age: float = 60.0, fetch_mode: Optional[str] = None) -> Any:
    """
    Execute a query with caching.
    
    Args:
        query: SQL query string
        params: Query parameters
        max_age: Maximum age of cached result in seconds
        fetch_mode: None, 'one', 'all', or 'lastrowid'
        
    Returns:
        Query results
    """
    # Only cache SELECT queries
    if not query.strip().upper().startswith("SELECT"):
        return execute_query(query, params, fetch_mode)
    
    # Create cache key
    cache_key = f"{query}:{str(params)}"
    
    # Check if result is in cache and not expired
    current_time = time.time()
    if cache_key in _query_cache:
        result, timestamp = _query_cache[cache_key]
        if current_time - timestamp <= max_age:
            logger.debug(f"Cache hit for query: {query}")
            return result
    
    # Execute query
    result = execute_query(query, params, fetch_mode)
    
    # Cache result
    _query_cache[cache_key] = (result, current_time)
    
    # Limit cache size
    if len(_query_cache) > QUERY_CACHE_SIZE:
        # Remove oldest entries
        sorted_keys = sorted(_query_cache.keys(), key=lambda k: _query_cache[k][1])
        for key in sorted_keys[:len(_query_cache) - QUERY_CACHE_SIZE]:
            del _query_cache[key]
    
    return result


def clear_query_cache() -> None:
    """Clear the query cache."""
    global _query_cache
    _query_cache = {}
    logger.info("Query cache cleared")


def analyze_database() -> Dict[str, Any]:
    """
    Analyze the database structure and usage.
    
    Returns:
        Dictionary with analysis results
    """
    results = {
        "tables": {},
        "indexes": {},
        "missing_indexes": [],
        "unused_indexes": [],
        "fragmentation": 0,
        "size": 0,
        "recommendations": []
    }
    
    try:
        # Get database size
        if os.path.exists(DATABASE_FILE):
            results["size"] = os.path.getsize(DATABASE_FILE)
        
        with get_connection() as conn:
            # Get list of tables
            tables = execute_query("SELECT name FROM sqlite_master WHERE type='table'", fetch_mode='all', conn=conn)
            
            for table in tables:
                table_name = table[0]
                
                # Skip sqlite internal tables
                if table_name.startswith('sqlite_'):
                    continue
                
                # Get table info
                table_info = execute_query(f"PRAGMA table_info({table_name})", fetch_mode='all', conn=conn)
                
                # Get row count
                row_count = execute_query(f"SELECT COUNT(*) FROM {table_name}", fetch_mode='one', conn=conn)[0]
                
                # Get indexes
                indexes = execute_query(f"PRAGMA index_list({table_name})", fetch_mode='all', conn=conn)
                
                # Store table info
                results["tables"][table_name] = {
                    "columns": [col[1] for col in table_info],
                    "row_count": row_count,
                    "indexes": [idx[1] for idx in indexes]
                }
                
                # Check for missing indexes on foreign keys and frequently queried columns
                for col in table_info:
                    col_name = col[1]
                    
                    # Check if column is a foreign key
                    if col_name.endswith('_id') and col_name != 'id':
                        # Check if there's an index on this column
                        has_index = False
                        for idx in indexes:
                            idx_info = execute_query(f"PRAGMA index_info({idx[1]})", fetch_mode='all', conn=conn)
                            if any(col_name == idx_col[2] for idx_col in idx_info):
                                has_index = True
                                break
                        
                        if not has_index and row_count > INDEX_THRESHOLD:
                            results["missing_indexes"].append({
                                "table": table_name,
                                "column": col_name,
                                "reason": "Foreign key without index"
                            })
                            results["recommendations"].append(
                                f"Create index on {table_name}.{col_name} (foreign key without index)"
                            )
                
                # Check for unused indexes
                for idx in indexes:
                    idx_name = idx[1]
                    idx_info = execute_query(f"PRAGMA index_info({idx_name})", fetch_mode='all', conn=conn)
                    
                    # Skip primary key indexes
                    if idx_name.startswith(f"sqlite_autoindex_{table_name}"):
                        continue
                    
                    # Check if index is used (simplified check - in a real system we would use query stats)
                    if row_count < INDEX_THRESHOLD:
                        results["unused_indexes"].append({
                            "table": table_name,
                            "index": idx_name,
                            "columns": [idx_col[2] for idx_col in idx_info],
                            "reason": f"Table has only {row_count} rows, below threshold of {INDEX_THRESHOLD}"
                        })
                        results["recommendations"].append(
                            f"Consider dropping index {idx_name} on {table_name} (table has few rows)"
                        )
            
            # Check for fragmentation
            fragmentation = execute_query("PRAGMA integrity_check", fetch_mode='one', conn=conn)[0]
            results["fragmentation"] = 0 if fragmentation == "ok" else 1
            
            # Check if vacuum is needed
            if results["size"] > VACUUM_THRESHOLD:
                results["recommendations"].append(
                    f"Run VACUUM to optimize database size (current size: {results['size']} bytes)"
                )
    
    except Exception as e:
        logger.error(f"Error analyzing database: {e}")
        results["error"] = str(e)
    
    return results


def optimize_database() -> Dict[str, Any]:
    """
    Optimize the database based on analysis.
    
    Returns:
        Dictionary with optimization results
    """
    results = {
        "actions": [],
        "errors": []
    }
    
    try:
        # Analyze database first
        analysis = analyze_database()
        
        with get_connection() as conn:
            # Create missing indexes
            for missing_index in analysis["missing_indexes"]:
                table = missing_index["table"]
                column = missing_index["column"]
                index_name = f"idx_{table}_{column}"
                
                try:
                    execute_query(f"CREATE INDEX IF NOT EXISTS {index_name} ON {table}({column})", conn=conn)
                    results["actions"].append(f"Created index {index_name} on {table}({column})")
                except Exception as e:
                    error_msg = f"Error creating index {index_name}: {e}"
                    logger.error(error_msg)
                    results["errors"].append(error_msg)
            
            # Drop unused indexes (commented out for safety - in a real system we would be more careful)
            # for unused_index in analysis["unused_indexes"]:
            #     table = unused_index["table"]
            #     index = unused_index["index"]
            #     
            #     try:
            #         execute_query(f"DROP INDEX IF EXISTS {index}", conn=conn)
            #         results["actions"].append(f"Dropped unused index {index}")
            #     except Exception as e:
            #         error_msg = f"Error dropping index {index}: {e}"
            #         logger.error(error_msg)
            #         results["errors"].append(error_msg)
            
            # Run ANALYZE to update statistics
            try:
                execute_query("ANALYZE", conn=conn)
                results["actions"].append("Updated database statistics with ANALYZE")
            except Exception as e:
                error_msg = f"Error running ANALYZE: {e}"
                logger.error(error_msg)
                results["errors"].append(error_msg)
            
            # Run VACUUM if needed
            if analysis["size"] > VACUUM_THRESHOLD:
                try:
                    # VACUUM cannot be run inside a transaction
                    conn.isolation_level = None
                    conn.execute("VACUUM")
                    conn.isolation_level = ''  # Reset to default
                    results["actions"].append("Optimized database size with VACUUM")
                except Exception as e:
                    error_msg = f"Error running VACUUM: {e}"
                    logger.error(error_msg)
                    results["errors"].append(error_msg)
    
    except Exception as e:
        error_msg = f"Error optimizing database: {e}"
        logger.error(error_msg)
        results["errors"].append(error_msg)
    
    return results


def create_optimized_indexes() -> Dict[str, Any]:
    """
    Create optimized indexes based on common query patterns.
    
    Returns:
        Dictionary with results
    """
    results = {
        "created_indexes": [],
        "errors": []
    }
    
    # Define indexes to create
    indexes_to_create = [
        # Users table indexes
        {"table": "users", "columns": ["username"], "name": "idx_users_username"},
        {"table": "users", "columns": ["email"], "name": "idx_users_email"},
        {"table": "users", "columns": ["is_admin"], "name": "idx_users_is_admin"},
        {"table": "users", "columns": ["is_guest"], "name": "idx_users_is_guest"},
        {"table": "users", "columns": ["account_status"], "name": "idx_users_account_status"},
        {"table": "users", "columns": ["email_verified"], "name": "idx_users_email_verified"},
        
        # Preferences table indexes
        {"table": "preferences", "columns": ["user_id"], "name": "idx_preferences_user_id"},
        {"table": "preferences", "columns": ["user_id", "key"], "name": "idx_preferences_user_id_key"},
        
        # Verification tokens table indexes
        {"table": "verification_tokens", "columns": ["user_id"], "name": "idx_verification_tokens_user_id"},
        {"table": "verification_tokens", "columns": ["token"], "name": "idx_verification_tokens_token"},
        {"table": "verification_tokens", "columns": ["token_type"], "name": "idx_verification_tokens_token_type"},
        {"table": "verification_tokens", "columns": ["expires_at"], "name": "idx_verification_tokens_expires_at"},
        
        # Stats table indexes
        {"table": "stats", "columns": ["user_id"], "name": "idx_stats_user_id"},
        
        # Trips table indexes
        {"table": "trips", "columns": ["user_id"], "name": "idx_trips_user_id"},
        {"table": "trips", "columns": ["date"], "name": "idx_trips_date"},
        {"table": "trips", "columns": ["user_id", "date"], "name": "idx_trips_user_id_date"}
    ]
    
    try:
        with get_connection() as conn:
            # Check existing indexes to avoid duplicates
            existing_indexes = {}
            tables = execute_query("SELECT name FROM sqlite_master WHERE type='table'", fetch_mode='all', conn=conn)
            
            for table in tables:
                table_name = table[0]
                
                # Skip sqlite internal tables
                if table_name.startswith('sqlite_'):
                    continue
                
                # Get indexes for this table
                indexes = execute_query(f"PRAGMA index_list({table_name})", fetch_mode='all', conn=conn)
                existing_indexes[table_name] = [idx[1] for idx in indexes]
            
            # Create indexes
            for index in indexes_to_create:
                table = index["table"]
                columns = index["columns"]
                name = index["name"]
                
                # Skip if table doesn't exist
                if table not in existing_indexes:
                    continue
                
                # Skip if index already exists
                if name in existing_indexes[table]:
                    continue
                
                try:
                    column_str = ", ".join(columns)
                    execute_query(f"CREATE INDEX IF NOT EXISTS {name} ON {table}({column_str})", conn=conn)
                    results["created_indexes"].append(f"Created index {name} on {table}({column_str})")
                except Exception as e:
                    error_msg = f"Error creating index {name}: {e}"
                    logger.error(error_msg)
                    results["errors"].append(error_msg)
    
    except Exception as e:
        error_msg = f"Error creating optimized indexes: {e}"
        logger.error(error_msg)
        results["errors"].append(error_msg)
    
    return results


def optimize_queries() -> Dict[str, Any]:
    """
    Optimize common queries by creating prepared statements.
    
    Returns:
        Dictionary with results
    """
    results = {
        "optimized_queries": []
    }
    
    # Define common queries to optimize
    optimized_queries = [
        # User queries
        "SELECT * FROM users WHERE username = ?",
        "SELECT * FROM users WHERE email = ?",
        "SELECT * FROM users WHERE id = ?",
        "SELECT * FROM users WHERE is_admin = 1",
        "SELECT * FROM users WHERE account_status = 'active'",
        
        # Preferences queries
        "SELECT * FROM preferences WHERE user_id = ?",
        "SELECT * FROM preferences WHERE user_id = ? AND key = ?",
        
        # Trips queries
        "SELECT * FROM trips WHERE user_id = ? ORDER BY date DESC",
        "SELECT * FROM trips WHERE user_id = ? AND date >= ? AND date <= ?",
        
        # Stats queries
        "SELECT * FROM stats WHERE user_id = ?"
    ]
    
    try:
        with get_connection() as conn:
            # Prepare statements
            for query in optimized_queries:
                try:
                    # SQLite automatically prepares statements, but we'll execute them once
                    # to ensure they're in the statement cache
                    cursor = conn.cursor()
                    cursor.execute(query, (1,) * query.count('?'))
                    results["optimized_queries"].append(query)
                except Exception as e:
                    logger.error(f"Error preparing query '{query}': {e}")
    
    except Exception as e:
        logger.error(f"Error optimizing queries: {e}")
    
    return results


def get_database_stats() -> Dict[str, Any]:
    """
    Get database statistics.
    
    Returns:
        Dictionary with database statistics
    """
    stats = {
        "size": 0,
        "tables": {},
        "total_rows": 0,
        "last_analyzed": None,
        "last_optimized": None
    }
    
    try:
        # Get database size
        if os.path.exists(DATABASE_FILE):
            stats["size"] = os.path.getsize(DATABASE_FILE)
        
        with get_connection() as conn:
            # Get list of tables
            tables = execute_query("SELECT name FROM sqlite_master WHERE type='table'", fetch_mode='all', conn=conn)
            
            for table in tables:
                table_name = table[0]
                
                # Skip sqlite internal tables
                if table_name.startswith('sqlite_'):
                    continue
                
                # Get row count
                row_count = execute_query(f"SELECT COUNT(*) FROM {table_name}", fetch_mode='one', conn=conn)[0]
                
                # Store table info
                stats["tables"][table_name] = {
                    "row_count": row_count
                }
                
                # Update total row count
                stats["total_rows"] += row_count
    
    except Exception as e:
        logger.error(f"Error getting database stats: {e}")
    
    return stats

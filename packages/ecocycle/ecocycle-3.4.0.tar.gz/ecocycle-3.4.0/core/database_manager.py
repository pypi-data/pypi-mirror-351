import datetime
import logging
import sqlite3
import os
import time
import threading
import queue
import shutil
from sqlite3 import Error
from contextlib import contextmanager
from typing import Optional, List, Tuple, Dict, Any, Union
import config.config as config

# Configuration
DATABASE_FILE = config.DATABASE_FILE
BACKUP_DIR = config.BACKUP_DIR
MAX_CONNECTIONS = 5
CONNECTION_TIMEOUT = 30  # seconds
ENABLE_FOREIGN_KEYS = True
ENABLE_PERFORMANCE_MONITORING = True

# Connection pool
connection_pool = queue.Queue(maxsize=MAX_CONNECTIONS)
connection_lock = threading.RLock()
_pool_initialized = False

# Performance monitoring
query_stats = {
    "total_queries": 0,
    "slow_queries": 0,
    "query_times": []
}
SLOW_QUERY_THRESHOLD = 0.1  # seconds

def initialize_connection_pool():
    """Initialize the connection pool with connections."""
    global _pool_initialized
    if _pool_initialized:
        return

    with connection_lock:
        if not _pool_initialized:
            for _ in range(MAX_CONNECTIONS):
                try:
                    # Create connection with timeout and WAL mode for better concurrency
                    conn = sqlite3.connect(
                        DATABASE_FILE,
                        check_same_thread=False,
                        timeout=30.0  # 30 second timeout for database locks
                    )

                    # Configure SQLite for better concurrency and performance
                    conn.execute("PRAGMA foreign_keys = ON")
                    conn.execute("PRAGMA journal_mode = WAL")  # Write-Ahead Logging for better concurrency
                    conn.execute("PRAGMA synchronous = NORMAL")  # Balance between safety and performance
                    conn.execute("PRAGMA cache_size = 10000")  # Increase cache size
                    conn.execute("PRAGMA temp_store = MEMORY")  # Store temp tables in memory
                    conn.execute("PRAGMA busy_timeout = 30000")  # 30 second busy timeout

                    connection_pool.put(conn)
                except Error as e:
                    logging.error(f"Error initializing connection pool: {e}")
            _pool_initialized = True
            logging.info(f"Connection pool initialized with {MAX_CONNECTIONS} connections")

def reset_connection_pool():
    """Reset the connection pool with new configuration."""
    global _pool_initialized
    with connection_lock:
        # Close all existing connections
        connections = []
        while not connection_pool.empty():
            try:
                connections.append(connection_pool.get_nowait())
            except queue.Empty:
                break

        # Close all connections
        for conn in connections:
            try:
                conn.close()
            except:
                pass

        # Reset the pool
        _pool_initialized = False

        # Reinitialize with new configuration
        initialize_connection_pool()
        logging.info("Connection pool reset with new configuration")

@contextmanager
def get_connection():
    """Get a connection from the pool with context management for automatic return."""
    if not _pool_initialized:
        initialize_connection_pool()

    conn = None
    try:
        # Try to get a connection from the pool with timeout
        conn = connection_pool.get(timeout=CONNECTION_TIMEOUT)
        yield conn
    except queue.Empty:
        logging.error("Timeout waiting for database connection from pool")
        # Create a temporary connection if pool is exhausted
        conn = sqlite3.connect(DATABASE_FILE, timeout=30.0)
        # Apply the same SQLite configuration as the pool connections
        conn.execute("PRAGMA foreign_keys = ON")
        conn.execute("PRAGMA journal_mode = WAL")
        conn.execute("PRAGMA synchronous = NORMAL")
        conn.execute("PRAGMA cache_size = 10000")
        conn.execute("PRAGMA temp_store = MEMORY")
        conn.execute("PRAGMA busy_timeout = 30000")
        yield conn
        # Don't return temporary connections to the pool
        conn.close()
        conn = None
    except Exception as e:
        logging.error(f"Error getting connection from pool: {e}")
        if conn:
            # Return the connection to the pool on error
            connection_pool.put(conn)
            conn = None
        raise
    finally:
        # Return the connection to the pool if it came from the pool
        if conn and not connection_pool.full():
            connection_pool.put(conn)

def create_connection():
    """
    Create a database connection to the SQLite database specified by DATABASE_FILE.

    Note: This function is maintained for backward compatibility.
    New code should use the get_connection() context manager instead.

    Returns:
        Connection object or None
    """
    conn = None
    try:
        conn = sqlite3.connect(DATABASE_FILE, timeout=30.0)
        # Apply the same SQLite configuration for consistency
        conn.execute("PRAGMA foreign_keys = ON")
        conn.execute("PRAGMA journal_mode = WAL")
        conn.execute("PRAGMA synchronous = NORMAL")
        conn.execute("PRAGMA cache_size = 10000")
        conn.execute("PRAGMA temp_store = MEMORY")
        conn.execute("PRAGMA busy_timeout = 30000")
        logging.info("Database connection created successfully.")
        return conn
    except Error as e:
        logging.error(f"Error creating database connection: {e}")
    return conn

def close_connection(conn):
    """
    Close a database connection.

    Args:
        conn: Connection object
    """
    if conn:
        try:
            conn.close()
            logging.info("Database connection closed successfully.")
        except Error as e:
            logging.error(f"Error closing database connection: {e}")

def execute_query(query, params=(), fetch_mode=None, conn=None):
    """
    Execute a query with performance monitoring and connection management.

    Args:
        query: SQL query string
        params: Query parameters
        fetch_mode: None, 'one', 'all', or 'lastrowid'
        conn: Optional connection object. If provided, this connection will be used
              instead of getting one from the pool. Useful for transactions.

    Returns:
        Query results based on fetch_mode
    """
    start_time = time.time()
    result = None
    should_commit = True

    # Determine if this is a SELECT query (which doesn't need a commit)
    is_select = query.strip().upper().startswith("SELECT")
    if is_select:
        should_commit = False

    # Use provided connection or get one from the pool
    if conn:
        # Use the provided connection
        try:
            cursor = conn.cursor()
            cursor.execute(query, params)

            if fetch_mode == 'one':
                result = cursor.fetchone()
            elif fetch_mode == 'all':
                result = cursor.fetchall()
            elif fetch_mode == 'lastrowid':
                if should_commit:
                    conn.commit()
                result = cursor.lastrowid
            else:
                if should_commit:
                    conn.commit()

            # Performance monitoring
            if ENABLE_PERFORMANCE_MONITORING:
                query_time = time.time() - start_time
                with connection_lock:
                    query_stats["total_queries"] += 1
                    query_stats["query_times"].append(query_time)
                    if query_time > SLOW_QUERY_THRESHOLD:
                        query_stats["slow_queries"] += 1
                        logging.warning(f"Slow query detected ({query_time:.4f}s): {query}")

        except Error as e:
            logging.error(f"Database error executing query: {e}")
            logging.error(f"Query: {query}")
            logging.error(f"Params: {params}")
            raise
    else:
        # Get a connection from the pool
        with get_connection() as conn:
            try:
                cursor = conn.cursor()
                cursor.execute(query, params)

                if fetch_mode == 'one':
                    result = cursor.fetchone()
                elif fetch_mode == 'all':
                    result = cursor.fetchall()
                elif fetch_mode == 'lastrowid':
                    if should_commit:
                        conn.commit()
                    result = cursor.lastrowid
                else:
                    if should_commit:
                        conn.commit()

                # Performance monitoring
                if ENABLE_PERFORMANCE_MONITORING:
                    query_time = time.time() - start_time
                    with connection_lock:
                        query_stats["total_queries"] += 1
                        query_stats["query_times"].append(query_time)
                        if query_time > SLOW_QUERY_THRESHOLD:
                            query_stats["slow_queries"] += 1
                            logging.warning(f"Slow query detected ({query_time:.4f}s): {query}")

            except Error as e:
                logging.error(f"Database error executing query: {e}")
                logging.error(f"Query: {query}")
                logging.error(f"Params: {params}")
                raise

    return result

def create_table(conn, create_table_sql):
    """Create a table from the create_table_sql statement."""
    try:
        c = conn.cursor()
        c.execute(create_table_sql)
        logging.info("Table created successfully.")
    except Error as e:
        logging.error(f"Error creating table: {e}")

def create_backup():
    """
    Create a backup of the database.

    Returns:
        str: Path to the backup file or None if backup failed
    """
    if not os.path.exists(DATABASE_FILE):
        logging.error(f"Cannot backup: Database file {DATABASE_FILE} does not exist")
        return None

    # Create backup directory if it doesn't exist
    if not os.path.exists(BACKUP_DIR):
        try:
            os.makedirs(BACKUP_DIR)
            logging.info(f"Created backup directory: {BACKUP_DIR}")
        except OSError as e:
            logging.error(f"Error creating backup directory: {e}")
            return None

    # Generate backup filename with timestamp
    timestamp = time.strftime("%Y%m%d-%H%M%S")
    backup_file = os.path.join(BACKUP_DIR, f"ecocycle_backup_{timestamp}.db")

    try:
        # Close all connections in the pool to ensure a clean backup
        with connection_lock:
            # Empty the pool
            connections = []
            while not connection_pool.empty():
                try:
                    connections.append(connection_pool.get_nowait())
                except queue.Empty:
                    break

            # Copy the database file
            shutil.copy2(DATABASE_FILE, backup_file)

            # Return connections to the pool
            for conn in connections:
                connection_pool.put(conn)

        logging.info(f"Database backup created successfully: {backup_file}")
        return backup_file
    except Exception as e:
        logging.error(f"Error creating database backup: {e}")
        return None

def restore_backup(backup_file):
    """
    Restore the database from a backup file.

    Args:
        backup_file (str): Path to the backup file

    Returns:
        bool: True if restore was successful, False otherwise
    """
    if not os.path.exists(backup_file):
        logging.error(f"Cannot restore: Backup file {backup_file} does not exist")
        return False

    try:
        # Close all connections in the pool
        with connection_lock:
            # Empty the pool
            connections = []
            while not connection_pool.empty():
                try:
                    connections.append(connection_pool.get_nowait())
                except queue.Empty:
                    break

            # Close all connections
            for conn in connections:
                conn.close()

            # Replace the database file
            shutil.copy2(backup_file, DATABASE_FILE)

            # Reinitialize the connection pool
            global _pool_initialized
            _pool_initialized = False
            initialize_connection_pool()

        logging.info(f"Database restored successfully from: {backup_file}")
        return True
    except Exception as e:
        logging.error(f"Error restoring database from backup: {e}")
        return False

def get_performance_stats():
    """
    Get database performance statistics.

    Returns:
        dict: Performance statistics
    """
    with connection_lock:
        stats = query_stats.copy()

        # Calculate average query time
        if stats["query_times"]:
            stats["avg_query_time"] = sum(stats["query_times"]) / len(stats["query_times"])
        else:
            stats["avg_query_time"] = 0

        # Calculate slow query percentage
        if stats["total_queries"] > 0:
            stats["slow_query_percentage"] = (stats["slow_queries"] / stats["total_queries"]) * 100
        else:
            stats["slow_query_percentage"] = 0

        # Limit the size of query_times list to prevent memory issues
        if len(query_stats["query_times"]) > 1000:
            query_stats["query_times"] = query_stats["query_times"][-1000:]

    return stats

@contextmanager
def transaction():
    """
    Context manager for database transactions.

    Usage:
        with transaction() as conn:
            # Perform multiple operations that should be atomic
            execute_query("INSERT INTO ...", params, conn=conn)
            execute_query("UPDATE ...", params, conn=conn)

    Note:
        The execute_query function now accepts a conn parameter that allows it to use
        an existing connection instead of getting one from the pool. This is essential
        for transactions to work properly.
    """
    with get_connection() as conn:
        try:
            # Start transaction
            conn.execute("BEGIN TRANSACTION")
            yield conn
            # Commit transaction
            conn.commit()
            logging.info("Transaction committed successfully")
        except Exception as e:
            # Rollback transaction on error
            conn.rollback()
            logging.error(f"Transaction rolled back due to error: {e}")
            raise

def initialize_database():
    """Initialize the database with the required tables."""
    # Create backup directory if it doesn't exist
    if not os.path.exists(BACKUP_DIR):
        try:
            os.makedirs(BACKUP_DIR)
        except OSError as e:
            logging.error(f"Error creating backup directory: {e}")

    # Create database schema
    sql_create_users_table = """ CREATE TABLE IF NOT EXISTS users (
                                        id integer PRIMARY KEY,
                                        username text NOT NULL UNIQUE,
                                        name text,
                                        email text,
                                        password_hash text,
                                        salt text,
                                        google_id text,
                                        is_admin integer NOT NULL,
                                        is_guest integer NOT NULL,
                                        registration_date text,
                                        last_login_date text,
                                        account_status text DEFAULT 'active',
                                        email_verified integer DEFAULT 0,
                                        guest_number integer DEFAULT 0
                                    ); """

    sql_create_preferences_table = """CREATE TABLE IF NOT EXISTS preferences (
                                    id integer PRIMARY KEY,
                                    user_id integer NOT NULL,
                                    key text NOT NULL,
                                    value text,
                                    last_updated text,
                                    FOREIGN KEY (user_id) REFERENCES users (id)
                                );"""

    sql_create_verification_tokens_table = """CREATE TABLE IF NOT EXISTS verification_tokens (
                                    id integer PRIMARY KEY,
                                    user_id integer NOT NULL,
                                    token text NOT NULL,
                                    token_type text NOT NULL,
                                    created_at text NOT NULL,
                                    expires_at text NOT NULL,
                                    used integer DEFAULT 0,
                                    FOREIGN KEY (user_id) REFERENCES users (id)
                                );"""

    sql_create_stats_table = """CREATE TABLE IF NOT EXISTS stats (
                                id integer PRIMARY KEY,
                                user_id integer NOT NULL,
                                total_trips integer,
                                total_distance real,
                                total_co2_saved real,
                                total_calories integer,
                                last_updated text,
                                FOREIGN KEY (user_id) REFERENCES users (id)
                            );"""

    sql_create_trips_table = """CREATE TABLE IF NOT EXISTS trips (
                                id integer PRIMARY KEY,
                                user_id integer NOT NULL,
                                date text,
                                distance real,
                                duration real,
                                co2_saved real,
                                calories integer,
                                route_data text,
                                weather_data text,
                                FOREIGN KEY (user_id) REFERENCES users (id)
                            );"""

    sql_create_migrations_table = """CREATE TABLE IF NOT EXISTS migrations (
                                id integer PRIMARY KEY,
                                version text NOT NULL,
                                applied_at text NOT NULL
                            );"""

    # Initialize connection pool
    initialize_connection_pool()

    # Create tables
    with get_connection() as conn:
        create_table(conn, sql_create_users_table)
        create_table(conn, sql_create_preferences_table)
        create_table(conn, sql_create_verification_tokens_table)
        create_table(conn, sql_create_stats_table)
        create_table(conn, sql_create_trips_table)
        create_table(conn, sql_create_migrations_table)

    # Apply migrations if needed
    apply_migrations()

    # Create initial backup
    if os.path.exists(DATABASE_FILE) and not os.listdir(BACKUP_DIR):
        create_backup()

    logging.info("Database initialized successfully")

def validate_user_data(user_data, is_update=False):
    """
    Validate user data before database operations.

    Args:
        user_data: User data tuple
        is_update: Whether this is an update operation

    Returns:
        tuple: (is_valid, error_message)
    """
    # Check if required fields are present
    if not user_data:
        return False, "User data is empty"

    # For update operations, check if username (last field) is provided
    if is_update and not user_data[-1]:
        return False, "Username is required for update"

    # For insert operations, check if username (first field) is provided
    if not is_update and not user_data[0]:
        return False, "Username is required"

    # Check if admin and guest flags are valid integers
    # For update operations, the indices are different because username is at the end
    if is_update:
        admin_index = 5
        guest_index = 6
    else:
        admin_index = 6
        guest_index = 7

    try:
        if admin_index < len(user_data) and user_data[admin_index] is not None:
            int(user_data[admin_index])
        if guest_index < len(user_data) and user_data[guest_index] is not None:
            int(user_data[guest_index])
    except (ValueError, TypeError):
        return False, "Admin and guest flags must be integers"

    return True, ""

def apply_migrations():
    """
    Apply database migrations to update the schema.

    Returns:
        bool: True if migrations were applied successfully
    """
    # Define migrations
    migrations = [
        {
            "version": "1.0.1",
            "description": "Add last_login_date to users table",
            "sql": "ALTER TABLE users ADD COLUMN last_login_date text;"
        },
        {
            "version": "1.0.2",
            "description": "Add account_status to users table",
            "sql": "ALTER TABLE users ADD COLUMN account_status text DEFAULT 'active';"
        },
        {
            "version": "1.0.3",
            "description": "Add last_updated to preferences table",
            "sql": "ALTER TABLE preferences ADD COLUMN last_updated text;"
        },
        {
            "version": "1.0.4",
            "description": "Add last_updated to stats table",
            "sql": "ALTER TABLE stats ADD COLUMN last_updated text;"
        },
        {
            "version": "1.0.5",
            "description": "Add route_data and weather_data to trips table",
            "sql": "ALTER TABLE trips ADD COLUMN route_data text; ALTER TABLE trips ADD COLUMN weather_data text;"
        },
        {
            "version": "1.0.6",
            "description": "Add email verification fields to users table",
            "sql": "ALTER TABLE users ADD COLUMN email_verified INTEGER DEFAULT 0; ALTER TABLE users ADD COLUMN guest_number INTEGER DEFAULT 0;"
        }
    ]

    # Get applied migrations
    with get_connection() as conn:
        try:
            # First, ensure the migrations table exists and has the correct structure
            cursor = conn.cursor()

            # Check if migrations table exists
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='migrations'")
            table_exists = cursor.fetchone() is not None

            if not table_exists:
                # Create migrations table if it doesn't exist
                logging.info("Migrations table does not exist. Creating it now.")
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS migrations (
                        id integer PRIMARY KEY,
                        version text NOT NULL,
                        applied_at text NOT NULL
                    )
                """)
                conn.commit()
                applied_versions = []
            else:
                # Get applied migrations
                try:
                    applied_versions = []
                    cursor.execute("SELECT version FROM migrations ORDER BY id")
                    for row in cursor.fetchall():
                        applied_versions.append(row[0])
                except Error as e:
                    logging.error(f"Error retrieving applied migrations: {e}")
                    applied_versions = []  # Assume no migrations applied if there's an error

            # Apply missing migrations
            for migration in migrations:
                if migration["version"] not in applied_versions:
                    logging.info(f"Applying migration {migration['version']}: {migration['description']}")

                    # Split multiple statements
                    statements = migration["sql"].split(';')
                    try:
                        for statement in statements:
                            if statement.strip():
                                cursor.execute(statement)

                        # Record the migration
                        cursor.execute(
                            "INSERT INTO migrations (version, applied_at) VALUES (?, datetime('now'))",
                            (migration["version"],)
                        )
                        conn.commit()
                        logging.info(f"Migration {migration['version']} applied successfully")
                    except Error as e:
                        logging.error(f"Error applying migration {migration['version']}: {e}")
                        # Continue with next migration even if this one fails
                        conn.rollback()

            return True
        except Error as e:
            logging.error(f"Error in migration process: {e}")
            return False

def add_user(conn, user):
    """
    Create a new user into the users table.

    Args:
        conn: Connection object or None (if None, a connection will be obtained from the pool)
        user: Tuple containing (username, name, email, password_hash, salt, google_id, is_admin, is_guest, registration_date)

    Returns:
        int: User ID or None if operation failed
    """
    # Validate user data
    is_valid, error_message = validate_user_data(user)
    if not is_valid:
        logging.error(f"Invalid user data: {error_message}")
        return None

    sql = '''INSERT INTO users(username, name, email, password_hash, salt, google_id, is_admin, is_guest, registration_date)
             VALUES(?,?,?,?,?,?,?,?,?)'''

    # Use provided connection or get one from the pool
    if conn:
        try:
            cur = conn.cursor()
            cur.execute(sql, user)
            conn.commit()
            user_id = cur.lastrowid
            logging.info(f"User {user[0]} added successfully with ID {user_id}.")
            return user_id
        except Error as e:
            logging.error(f"Error adding user {user[0]}: {e}")
            return None
    else:
        try:
            return execute_query(sql, user, fetch_mode='lastrowid')
        except Error as e:
            logging.error(f"Error adding user {user[0]}: {e}")
            return None

def update_user(conn, user):
    """
    Update user data in the users table.

    Args:
        conn: Connection object or None (if None, a connection will be obtained from the pool)
        user: Tuple containing (name, email, password_hash, salt, google_id, is_admin, is_guest, registration_date, username)

    Returns:
        bool: True if update was successful, False otherwise
    """
    # Validate user data
    is_valid, error_message = validate_user_data(user, is_update=True)
    if not is_valid:
        logging.error(f"Invalid user data for update: {error_message}")
        return False

    sql = '''UPDATE users
             SET name = ?,
                 email = ?,
                 password_hash = ?,
                 salt = ?,
                 google_id = ?,
                 is_admin = ?,
                 is_guest = ?,
                 registration_date = ?,
                 last_login_date = datetime('now')
             WHERE username = ?'''

    # Use provided connection or get one from the pool
    if conn:
        try:
            cur = conn.cursor()
            cur.execute(sql, user)
            conn.commit()
            success = cur.rowcount > 0
            if success:
                logging.info(f"User {user[-1]} updated successfully.")
            else:
                logging.warning(f"User {user[-1]} update had no effect (user may not exist).")
            return success
        except Error as e:
            logging.error(f"Error updating user {user[-1]}: {e}")
            return False
    else:
        try:
            execute_query(sql, user)
            return True
        except Error as e:
            logging.error(f"Error updating user {user[-1]}: {e}")
            return False

def update_user_email_verified(conn, user_id, verified):
    """
    Update a user's email verification status.

    Args:
        conn: Connection object or None (if None, a connection will be obtained from the pool)
        user_id: User ID
        verified: Boolean indicating if email is verified

    Returns:
        bool: True if update was successful, False otherwise
    """
    sql = "UPDATE users SET email_verified = ? WHERE id = ?"
    params = (1 if verified else 0, user_id)

    # Use provided connection or get one from the pool
    if conn:
        try:
            cur = conn.cursor()
            cur.execute(sql, params)
            conn.commit()
            success = cur.rowcount > 0
            if success:
                logging.info(f"Email verification status for user ID {user_id} updated to {verified}.")
            else:
                logging.warning(f"Email verification update for user ID {user_id} had no effect (user may not exist).")
            return success
        except Error as e:
            logging.error(f"Error updating email verification status for user ID {user_id}: {e}")
            return False
    else:
        try:
            execute_query(sql, params)
            return True
        except Error as e:
            logging.error(f"Error updating email verification status for user ID {user_id}: {e}")
            return False

def get_user(conn, username):
    """
    Query user by username or email.

    Args:
        conn: Connection object or None (if None, a connection will be obtained from the pool)
        username: Username or email to query

    Returns:
        tuple: User data or None if not found
    """
    # First try to find by username
    sql = "SELECT * FROM users WHERE username=?"
    params = (username,)

    # Use provided connection or get one from the pool
    if conn:
        try:
            cur = conn.cursor()
            cur.execute(sql, params)
            row = cur.fetchone()

            # If not found by username, try to find by email
            if not row:
                sql_email = "SELECT * FROM users WHERE email=?"
                cur.execute(sql_email, params)
                row = cur.fetchone()

            if row:
                logging.info(f"User {username} retrieved successfully.")
            else:
                logging.info(f"User {username} not found by username or email.")
            return row
        except Error as e:
            logging.error(f"Error retrieving user {username}: {e}")
            return None
    else:
        try:
            # Try by username first
            row = execute_query(sql, params, fetch_mode='one')

            # If not found, try by email
            if not row:
                sql_email = "SELECT * FROM users WHERE email=?"
                row = execute_query(sql_email, params, fetch_mode='one')

            return row
        except Error as e:
            logging.error(f"Error retrieving user {username}: {e}")
            return None

def get_user_by_id(conn, user_id):
    """
    Query user by ID.

    Args:
        conn: Connection object or None (if None, a connection will be obtained from the pool)
        user_id: User ID to query

    Returns:
        tuple: User data or None if not found
    """
    sql = "SELECT * FROM users WHERE id=?"
    params = (user_id,)

    # Use provided connection or get one from the pool
    if conn:
        try:
            cur = conn.cursor()
            cur.execute(sql, params)
            row = cur.fetchone()
            if row:
                logging.info(f"User with ID {user_id} retrieved successfully.")
            else:
                logging.info(f"User with ID {user_id} not found.")
            return row
        except Error as e:
            logging.error(f"Error retrieving user with ID {user_id}: {e}")
            return None
    else:
        try:
            return execute_query(sql, params, fetch_mode='one')
        except Error as e:
            logging.error(f"Error retrieving user with ID {user_id}: {e}")
            return None

def get_all_users(conn):
    """
    Query all users from the users table.

    Args:
        conn: Connection object or None (if None, a connection will be obtained from the pool)

    Returns:
        list: List of user tuples or empty list if error
    """
    sql = "SELECT * FROM users"

    # Use provided connection or get one from the pool
    if conn:
        try:
            cur = conn.cursor()
            cur.execute(sql)
            rows = cur.fetchall()
            logging.info(f"Retrieved {len(rows)} users successfully.")
            return rows
        except Error as e:
            logging.error(f"Error retrieving all users: {e}")
            return []
    else:
        try:
            result = execute_query(sql, fetch_mode='all')
            return result if result else []
        except Error as e:
            logging.error(f"Error retrieving all users: {e}")
            return []

def get_active_users(conn=None):
    """
    Query all active users from the users table.

    Args:
        conn: Connection object or None (if None, a connection will be obtained from the pool)

    Returns:
        list: List of active user tuples or empty list if error
    """
    sql = "SELECT * FROM users WHERE account_status = 'active'"

    # Use provided connection or get one from the pool
    if conn:
        try:
            cur = conn.cursor()
            cur.execute(sql)
            rows = cur.fetchall()
            logging.info(f"Retrieved {len(rows)} active users successfully.")
            return rows
        except Error as e:
            logging.error(f"Error retrieving active users: {e}")
            return []
    else:
        try:
            result = execute_query(sql, fetch_mode='all')
            return result if result else []
        except Error as e:
            logging.error(f"Error retrieving active users: {e}")
            return []

def validate_preference_data(preference_data, is_update=False):
    """
    Validate preference data before database operations.

    Args:
        preference_data: Preference data tuple
        is_update: Whether this is an update operation

    Returns:
        tuple: (is_valid, error_message)
    """
    # Check if required fields are present
    if not preference_data:
        return False, "Preference data is empty"

    # For update operations, check if all required fields are provided
    if is_update:
        if len(preference_data) < 3:
            return False, "Value, user_id, and key are required for update"
        if not preference_data[1] or not preference_data[2]:
            return False, "User ID and key are required for update"
    else:
        # For insert operations
        if len(preference_data) < 3:
            return False, "User ID, key, and value are required"
        if not preference_data[0] or not preference_data[1]:
            return False, "User ID and key are required"

    # Validate user_id is an integer
    try:
        user_id_index = 1 if is_update else 0
        if preference_data[user_id_index]:
            int(preference_data[user_id_index])
    except (ValueError, TypeError):
        return False, "User ID must be an integer"

    return True, ""

def add_preference(conn, preference):
    """
    Create a new preference into the preferences table.

    Args:
        conn: Connection object or None (if None, a connection will be obtained from the pool)
        preference: Tuple containing (user_id, key, value)

    Returns:
        int: Preference ID or None if operation failed
    """
    # Validate preference data
    is_valid, error_message = validate_preference_data(preference)
    if not is_valid:
        logging.error(f"Invalid preference data: {error_message}")
        return None

    # Add timestamp to the data
    preference_with_timestamp = preference + (time.strftime("%Y-%m-%d %H:%M:%S"),)

    sql = '''INSERT INTO preferences(user_id, key, value, last_updated)
             VALUES(?,?,?,?)'''

    # Use provided connection or get one from the pool
    if conn:
        try:
            cur = conn.cursor()
            cur.execute(sql, preference_with_timestamp)
            conn.commit()
            pref_id = cur.lastrowid
            logging.info(f"Preference {preference[1]} for user {preference[0]} added successfully with ID {pref_id}.")
            return pref_id
        except Error as e:
            logging.error(f"Error adding preference {preference[1]} for user {preference[0]}: {e}")
            return None
    else:
        try:
            return execute_query(sql, preference_with_timestamp, fetch_mode='lastrowid')
        except Error as e:
            logging.error(f"Error adding preference {preference[1]} for user {preference[0]}: {e}")
            return None

def update_preference(conn, preference):
    """
    Update preference data in the preferences table.

    Args:
        conn: Connection object or None (if None, a connection will be obtained from the pool)
        preference: Tuple containing (value, user_id, key)

    Returns:
        bool: True if update was successful, False otherwise
    """
    # Validate preference data
    is_valid, error_message = validate_preference_data(preference, is_update=True)
    if not is_valid:
        logging.error(f"Invalid preference data for update: {error_message}")
        return False

    # Add timestamp to the data
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    preference_with_timestamp = (preference[0], timestamp, preference[1], preference[2])

    sql = '''UPDATE preferences
             SET value = ?,
                 last_updated = ?
             WHERE user_id = ? AND key = ?'''

    # Use provided connection or get one from the pool
    if conn:
        try:
            cur = conn.cursor()
            cur.execute(sql, preference_with_timestamp)
            conn.commit()
            success = cur.rowcount > 0
            if success:
                logging.info(f"Preference {preference[2]} for user {preference[1]} updated successfully.")
            else:
                logging.warning(f"Preference {preference[2]} for user {preference[1]} update had no effect (preference may not exist).")
            return success
        except Error as e:
            logging.error(f"Error updating preference {preference[2]} for user {preference[1]}: {e}")
            return False
    else:
        try:
            execute_query(sql, preference_with_timestamp)
            return True
        except Error as e:
            logging.error(f"Error updating preference {preference[2]} for user {preference[1]}: {e}")
            return False

def get_preference(conn, user_id, key):
    """
    Query preference by user_id and key.

    Args:
        conn: Connection object or None (if None, a connection will be obtained from the pool)
        user_id: User ID
        key: Preference key

    Returns:
        tuple: Preference data or None if not found
    """
    sql = "SELECT * FROM preferences WHERE user_id=? AND key=?"
    params = (user_id, key)

    # Use provided connection or get one from the pool
    if conn:
        try:
            cur = conn.cursor()
            cur.execute(sql, params)
            row = cur.fetchone()
            if row:
                logging.info(f"Preference {key} for user {user_id} retrieved successfully.")
            else:
                logging.info(f"Preference {key} for user {user_id} not found.")
            return row
        except Error as e:
            logging.error(f"Error retrieving preference {key} for user {user_id}: {e}")
            return None
    else:
        try:
            return execute_query(sql, params, fetch_mode='one')
        except Error as e:
            logging.error(f"Error retrieving preference {key} for user {user_id}: {e}")
            return None

def get_all_preferences(conn, user_id):
    """
    Query all preferences for a user.

    Args:
        conn: Connection object or None (if None, a connection will be obtained from the pool)
        user_id: User ID

    Returns:
        list: List of preference tuples or empty list if error
    """
    sql = "SELECT * FROM preferences WHERE user_id=?"
    params = (user_id,)

    # Use provided connection or get one from the pool
    if conn:
        try:
            cur = conn.cursor()
            cur.execute(sql, params)
            rows = cur.fetchall()
            logging.info(f"Retrieved {len(rows)} preferences for user {user_id} successfully.")
            return rows
        except Error as e:
            logging.error(f"Error retrieving preferences for user {user_id}: {e}")
            return []
    else:
        try:
            result = execute_query(sql, params, fetch_mode='all')
            return result if result else []
        except Error as e:
            logging.error(f"Error retrieving preferences for user {user_id}: {e}")
            return []

def validate_trip_data(trip_data, is_update=False):
    """
    Validate trip data before database operations.

    Args:
        trip_data: Trip data tuple
        is_update: Whether this is an update operation

    Returns:
        tuple: (is_valid, error_message)
    """
    # Check if required fields are present
    if not trip_data:
        return False, "Trip data is empty"

    # For update operations, check if trip_id (last field) is provided
    if is_update:
        if len(trip_data) < 6:
            return False, "Date, distance, duration, co2_saved, calories, and trip_id are required for update"
        if not trip_data[-1]:
            return False, "Trip ID is required for update"
    else:
        # For insert operations
        if len(trip_data) < 6:
            return False, "User ID, date, distance, duration, co2_saved, and calories are required"
        if not trip_data[0]:
            return False, "User ID is required"

    # Validate numeric fields
    try:
        # For update operations
        if is_update:
            # distance
            if trip_data[1] is not None:
                float(trip_data[1])
            # duration
            if trip_data[2] is not None:
                float(trip_data[2])
            # co2_saved
            if trip_data[3] is not None:
                float(trip_data[3])
            # calories
            if trip_data[4] is not None:
                int(trip_data[4])
            # trip_id
            if trip_data[5] is not None:
                int(trip_data[5])
        else:
            # user_id
            if trip_data[0] is not None:
                int(trip_data[0])
            # distance
            if trip_data[2] is not None:
                float(trip_data[2])
            # duration
            if trip_data[3] is not None:
                float(trip_data[3])
            # co2_saved
            if trip_data[4] is not None:
                float(trip_data[4])
            # calories
            if trip_data[5] is not None:
                int(trip_data[5])
    except (ValueError, TypeError):
        return False, "Numeric fields must have valid values"

    return True, ""

def add_trip(conn, trip):
    """
    Create a new trip into the trips table.

    Args:
        conn: Connection object or None (if None, a connection will be obtained from the pool)
        trip: Tuple containing (user_id, date, distance, duration, co2_saved, calories)

    Returns:
        int: Trip ID or None if operation failed
    """
    # Validate trip data
    is_valid, error_message = validate_trip_data(trip)
    if not is_valid:
        logging.error(f"Invalid trip data: {error_message}")
        return None

    # Check if extended trip data is provided (with route_data and weather_data)
    if len(trip) > 6:
        sql = '''INSERT INTO trips(user_id, date, distance, duration, co2_saved, calories, route_data, weather_data)
                 VALUES(?,?,?,?,?,?,?,?)'''
    else:
        sql = '''INSERT INTO trips(user_id, date, distance, duration, co2_saved, calories)
                 VALUES(?,?,?,?,?,?)'''

    # Use provided connection or get one from the pool
    if conn:
        try:
            cur = conn.cursor()
            cur.execute(sql, trip)
            conn.commit()
            trip_id = cur.lastrowid
            logging.info(f"Trip for user {trip[0]} on {trip[1]} added successfully with ID {trip_id}.")
            return trip_id
        except Error as e:
            logging.error(f"Error adding trip for user {trip[0]} on {trip[1]}: {e}")
            return None
    else:
        try:
            return execute_query(sql, trip, fetch_mode='lastrowid')
        except Error as e:
            logging.error(f"Error adding trip for user {trip[0]} on {trip[1]}: {e}")
            return None


def get_user_trips(conn, user_id):
    """
    Retrieve all trips for a specific user from the database.

    Args:
        conn: Connection object or None (if None, a connection will be obtained from the pool)
        user_id: User ID to retrieve trips for

    Returns:
        List of trip tuples or empty list if no trips found
    """
    sql = '''SELECT id, user_id, date, distance, duration, co2_saved, calories, route_data, weather_data
             FROM trips WHERE user_id = ? ORDER BY date DESC'''

    # Use provided connection or get one from the pool
    if conn:
        try:
            cur = conn.cursor()
            cur.execute(sql, (user_id,))
            trips = cur.fetchall()
            logging.info(f"Retrieved {len(trips)} trips for user {user_id} from database.")
            return trips
        except Error as e:
            logging.error(f"Error retrieving trips for user {user_id}: {e}")
            return []
    else:
        try:
            return execute_query(sql, (user_id,), fetch_mode='all') or []
        except Error as e:
            logging.error(f"Error retrieving trips for user {user_id}: {e}")
            return []

def update_trip(conn, trip):
    """
    Update trip data in the trips table.

    Args:
        conn: Connection object or None (if None, a connection will be obtained from the pool)
        trip: Tuple containing (date, distance, duration, co2_saved, calories, id)

    Returns:
        bool: True if update was successful, False otherwise
    """
    # Validate trip data
    is_valid, error_message = validate_trip_data(trip, is_update=True)
    if not is_valid:
        logging.error(f"Invalid trip data for update: {error_message}")
        return False

    # Check if extended trip data is provided (with route_data and weather_data)
    if len(trip) > 6:
        sql = '''UPDATE trips
                 SET date = ?,
                     distance = ?,
                     duration = ?,
                     co2_saved = ?,
                     calories = ?,
                     route_data = ?,
                     weather_data = ?
                 WHERE id = ?'''
    else:
        sql = '''UPDATE trips
                 SET date = ?,
                     distance = ?,
                     duration = ?,
                     co2_saved = ?,
                     calories = ?
                 WHERE id = ?'''

    # Use provided connection or get one from the pool
    if conn:
        try:
            cur = conn.cursor()
            cur.execute(sql, trip)
            conn.commit()
            success = cur.rowcount > 0
            if success:
                logging.info(f"Trip {trip[-1]} updated successfully.")
            else:
                logging.warning(f"Trip {trip[-1]} update had no effect (trip may not exist).")
            return success
        except Error as e:
            logging.error(f"Error updating trip {trip[-1]}: {e}")
            return False
    else:
        try:
            # Execute the query and check if any rows were affected
            cursor = execute_query(sql, trip, conn=None)
            # Since we don't have direct access to rowcount, we'll assume success if no exception is raised
            # In a future update, we could modify execute_query to return rowcount for UPDATE operations
            logging.info(f"Trip {trip[-1]} updated successfully.")
            return True
        except Error as e:
            logging.error(f"Error updating trip {trip[-1]}: {e}")
            return False

def get_trip(conn, trip_id):
    """
    Query trip by trip_id.

    Args:
        conn: Connection object or None (if None, a connection will be obtained from the pool)
        trip_id: Trip ID

    Returns:
        tuple: Trip data or None if not found
    """
    sql = "SELECT * FROM trips WHERE id=?"
    params = (trip_id,)

    # Use provided connection or get one from the pool
    if conn:
        try:
            cur = conn.cursor()
            cur.execute(sql, params)
            row = cur.fetchone()
            if row:
                logging.info(f"Trip {trip_id} retrieved successfully.")
            else:
                logging.info(f"Trip {trip_id} not found.")
            return row
        except Error as e:
            logging.error(f"Error retrieving trip {trip_id}: {e}")
            return None
    else:
        try:
            return execute_query(sql, params, fetch_mode='one')
        except Error as e:
            logging.error(f"Error retrieving trip {trip_id}: {e}")
            return None



def validate_stat_data(stat_data, is_update=False):
    """
    Validate stat data before database operations.

    Args:
        stat_data: Stat data tuple
        is_update: Whether this is an update operation

    Returns:
        tuple: (is_valid, error_message)
    """
    # Check if required fields are present
    if not stat_data:
        return False, "Stat data is empty"

    # For update operations, check if user_id (last field) is provided
    if is_update:
        if len(stat_data) < 5:
            return False, "Total trips, total distance, total CO2 saved, total calories, and user ID are required for update"
        if not stat_data[-1]:
            return False, "User ID is required for update"
    else:
        # For insert operations
        if len(stat_data) < 5:
            return False, "User ID, total trips, total distance, total CO2 saved, and total calories are required"
        if not stat_data[0]:
            return False, "User ID is required"

    # Validate numeric fields
    try:
        # For update operations
        if is_update:
            # total_trips
            if stat_data[0] is not None:
                int(stat_data[0])
            # total_distance
            if stat_data[1] is not None:
                float(stat_data[1])
            # total_co2_saved
            if stat_data[2] is not None:
                float(stat_data[2])
            # total_calories
            if stat_data[3] is not None:
                int(stat_data[3])
            # user_id
            if stat_data[4] is not None:
                int(stat_data[4])
        else:
            # user_id
            if stat_data[0] is not None:
                int(stat_data[0])
            # total_trips
            if stat_data[1] is not None:
                int(stat_data[1])
            # total_distance
            if stat_data[2] is not None:
                float(stat_data[2])
            # total_co2_saved
            if stat_data[3] is not None:
                float(stat_data[3])
            # total_calories
            if stat_data[4] is not None:
                int(stat_data[4])
    except (ValueError, TypeError):
        return False, "Numeric fields must have valid values"

    return True, ""

def add_stat(conn, stat):
    """
    Create a new stat into the stats table.

    Args:
        conn: Connection object or None (if None, a connection will be obtained from the pool)
        stat: Tuple containing (user_id, total_trips, total_distance, total_co2_saved, total_calories)

    Returns:
        int: Stat ID or None if operation failed
    """
    # Validate stat data
    is_valid, error_message = validate_stat_data(stat)
    if not is_valid:
        logging.error(f"Invalid stat data: {error_message}")
        return None

    # Add timestamp to the data
    stat_with_timestamp = stat + (time.strftime("%Y-%m-%d %H:%M:%S"),)

    sql = '''INSERT INTO stats(user_id, total_trips, total_distance, total_co2_saved, total_calories, last_updated)
             VALUES(?,?,?,?,?,?)'''

    # Use provided connection or get one from the pool
    if conn:
        try:
            cur = conn.cursor()
            cur.execute(sql, stat_with_timestamp)
            conn.commit()
            stat_id = cur.lastrowid
            logging.info(f"Stat for user {stat[0]} added successfully with ID {stat_id}.")
            return stat_id
        except Error as e:
            logging.error(f"Error adding stat for user {stat[0]}: {e}")
            return None
    else:
        try:
            return execute_query(sql, stat_with_timestamp, fetch_mode='lastrowid')
        except Error as e:
            logging.error(f"Error adding stat for user {stat[0]}: {e}")
            return None

def update_stat(conn, stat):
    """
    Update stat data in the stats table.

    Args:
        conn: Connection object or None (if None, a connection will be obtained from the pool)
        stat: Tuple containing (total_trips, total_distance, total_co2_saved, total_calories, user_id)

    Returns:
        bool: True if update was successful, False otherwise
    """
    # Validate stat data
    is_valid, error_message = validate_stat_data(stat, is_update=True)
    if not is_valid:
        logging.error(f"Invalid stat data for update: {error_message}")
        return False

    # Add timestamp to the data
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    stat_with_timestamp = stat[0:4] + (timestamp, stat[4])

    sql = '''UPDATE stats
             SET total_trips = ?,
                 total_distance = ?,
                 total_co2_saved = ?,
                 total_calories = ?,
                 last_updated = ?
             WHERE user_id = ?'''

    # Use provided connection or get one from the pool
    if conn:
        try:
            cur = conn.cursor()
            cur.execute(sql, stat_with_timestamp)
            conn.commit()
            success = cur.rowcount > 0
            if success:
                logging.info(f"Stat for user {stat[-1]} updated successfully.")
            else:
                logging.warning(f"Stat for user {stat[-1]} update had no effect (stat may not exist).")
            return success
        except Error as e:
            logging.error(f"Error updating stat for user {stat[-1]}: {e}")
            return False
    else:
        try:
            execute_query(sql, stat_with_timestamp)
            return True
        except Error as e:
            logging.error(f"Error updating stat for user {stat[-1]}: {e}")
            return False

def get_stat(conn, user_id):
    """
    Query stat by user_id.

    Args:
        conn: Connection object or None (if None, a connection will be obtained from the pool)
        user_id: User ID

    Returns:
        tuple: Stat data or None if not found
    """
    sql = "SELECT * FROM stats WHERE user_id=?"
    params = (user_id,)

    # Use provided connection or get one from the pool
    if conn:
        try:
            cur = conn.cursor()
            cur.execute(sql, params)
            row = cur.fetchone()
            if row:
                logging.info(f"Stat for user {user_id} retrieved successfully.")
            else:
                logging.info(f"Stat for user {user_id} not found.")
            return row
        except Error as e:
            logging.error(f"Error retrieving stat for user {user_id}: {e}")
            return None
    else:
        try:
            return execute_query(sql, params, fetch_mode='one')
        except Error as e:
            logging.error(f"Error retrieving stat for user {user_id}: {e}")
            return None

def get_all_stats(conn=None):
    """
    Query all stats from the stats table.

    Args:
        conn: Connection object or None (if None, a connection will be obtained from the pool)

    Returns:
        list: List of stat tuples or empty list if error
    """
    sql = "SELECT * FROM stats"

    # Use provided connection or get one from the pool
    if conn:
        try:
            cur = conn.cursor()
            cur.execute(sql)
            rows = cur.fetchall()
            logging.info(f"Retrieved {len(rows)} stats successfully.")
            return rows
        except Error as e:
            logging.error(f"Error retrieving all stats: {e}")
            return []
    else:
        try:
            result = execute_query(sql, fetch_mode='all')
            return result if result else []
        except Error as e:
            logging.error(f"Error retrieving all stats: {e}")
            return []

def get_global_stats(conn=None):
    """
    Calculate global statistics by aggregating all user stats.

    Args:
        conn: Connection object or None (if None, a connection will be obtained from the pool)

    Returns:
        dict: Global statistics or empty dict if error
    """
    sql = """
    SELECT
        COUNT(DISTINCT user_id) as total_users,
        SUM(total_trips) as total_trips,
        SUM(total_distance) as total_distance,
        SUM(total_co2_saved) as total_co2_saved,
        SUM(total_calories) as total_calories
    FROM stats
    """

    # Use provided connection or get one from the pool
    if conn:
        try:
            cur = conn.cursor()
            cur.execute(sql)
            row = cur.fetchone()
            if row:
                global_stats = {
                    "total_users": row[0] or 0,
                    "total_trips": row[1] or 0,
                    "total_distance": row[2] or 0,
                    "total_co2_saved": row[3] or 0,
                    "total_calories": row[4] or 0
                }
                logging.info("Global stats retrieved successfully.")
                return global_stats
            else:
                logging.info("No stats found for global calculation.")
                return {}
        except Error as e:
            logging.error(f"Error retrieving global stats: {e}")
            return {}
    else:
        try:
            row = execute_query(sql, fetch_mode='one')
            if row:
                global_stats = {
                    "total_users": row[0] or 0,
                    "total_trips": row[1] or 0,
                    "total_distance": row[2] or 0,
                    "total_co2_saved": row[3] or 0,
                    "total_calories": row[4] or 0
                }
                return global_stats
            else:
                return {}
        except Error as e:
            logging.error(f"Error retrieving global stats: {e}")
            return {}

def optimize_database(conn=None):
    """
    Optimize the database by running VACUUM and ANALYZE.

    Args:
        conn: Connection object or None (if None, a connection will be obtained from the pool)

    Returns:
        bool: True if optimization was successful, False otherwise
    """
    # Use provided connection or get one from the pool
    if conn:
        try:
            cur = conn.cursor()
            cur.execute("VACUUM")
            cur.execute("ANALYZE")
            logging.info("Database optimized successfully.")
            return True
        except Error as e:
            logging.error(f"Error optimizing database: {e}")
            return False
    else:
        try:
            with get_connection() as conn:
                cur = conn.cursor()
                cur.execute("VACUUM")
                cur.execute("ANALYZE")
                logging.info("Database optimized successfully.")
                return True
        except Error as e:
            logging.error(f"Error optimizing database: {e}")
            return False

def get_database_info(conn=None):
    """
    Get information about the database.

    Args:
        conn: Connection object or None (if None, a connection will be obtained from the pool)

    Returns:
        dict: Database information or empty dict if error
    """
    # SQL to get table information
    sql_tables = """
    SELECT
        name,
        sql
    FROM
        sqlite_master
    WHERE
        type='table' AND
        name NOT LIKE 'sqlite_%'
    """

    # SQL to get database size
    sql_size = """
    SELECT
        page_count * page_size as size_bytes
    FROM
        pragma_page_count(),
        pragma_page_size()
    """

    # Use provided connection or get one from the pool
    if conn:
        try:
            cur = conn.cursor()

            # Get tables
            cur.execute(sql_tables)
            tables = cur.fetchall()

            # Get size
            cur.execute(sql_size)
            size_row = cur.fetchone()
            size_bytes = size_row[0] if size_row else 0

            # Get row counts for each table
            table_stats = []
            for table_name, table_sql in tables:
                cur.execute(f"SELECT COUNT(*) FROM {table_name}")
                row_count = cur.fetchone()[0]
                table_stats.append({
                    "name": table_name,
                    "row_count": row_count,
                    "schema": table_sql
                })

            # Format size
            size_kb = size_bytes / 1024
            size_mb = size_kb / 1024
            size_formatted = f"{size_mb:.2f} MB" if size_mb >= 1 else f"{size_kb:.2f} KB"

            db_info = {
                "file_path": DATABASE_FILE,
                "size_bytes": size_bytes,
                "size_formatted": size_formatted,
                "tables": table_stats,
                "connection_pool_size": MAX_CONNECTIONS,
                "performance_monitoring": ENABLE_PERFORMANCE_MONITORING,
                "foreign_keys_enabled": ENABLE_FOREIGN_KEYS
            }

            logging.info("Database information retrieved successfully.")
            return db_info
        except Error as e:
            logging.error(f"Error retrieving database information: {e}")
            return {}
    else:
        try:
            with get_connection() as conn:
                cur = conn.cursor()

                # Get tables
                cur.execute(sql_tables)
                tables = cur.fetchall()

                # Get size
                cur.execute(sql_size)
                size_row = cur.fetchone()
                size_bytes = size_row[0] if size_row else 0

                # Get row counts for each table
                table_stats = []
                for table_name, table_sql in tables:
                    cur.execute(f"SELECT COUNT(*) FROM {table_name}")
                    row_count = cur.fetchone()[0]
                    table_stats.append({
                        "name": table_name,
                        "row_count": row_count,
                        "schema": table_sql
                    })

                # Format size
                size_kb = size_bytes / 1024
                size_mb = size_kb / 1024
                size_formatted = f"{size_mb:.2f} MB" if size_mb >= 1 else f"{size_kb:.2f} KB"

                db_info = {
                    "file_path": DATABASE_FILE,
                    "size_bytes": size_bytes,
                    "size_formatted": size_formatted,
                    "tables": table_stats,
                    "connection_pool_size": MAX_CONNECTIONS,
                    "performance_monitoring": ENABLE_PERFORMANCE_MONITORING,
                    "foreign_keys_enabled": ENABLE_FOREIGN_KEYS
                }

                return db_info
        except Error as e:
            logging.error(f"Error retrieving database information: {e}")
            return {}

def get_database_manager_help():
    """
    Get help information about the database manager.

    Returns:
        str: Help text with usage examples
    """
    help_text = """
    EcoCycle Database Manager
    ========================

    The database manager provides functions for interacting with the EcoCycle SQLite database.

    Key Features:
    - Connection pooling for efficient database connections
    - Transaction management for data integrity
    - Database backup and restore functionality
    - Performance monitoring for query optimization
    - Data validation for security
    - Migration support for schema updates

    Usage Examples:

    1. Using the connection pool (recommended):
       ```python
       # The connection is automatically returned to the pool when done
       with get_connection() as conn:
           # Perform database operations
           cursor = conn.cursor()
           cursor.execute("SELECT * FROM users")
           rows = cursor.fetchall()
       ```

    2. Using transactions for atomic operations:
       ```python
       # All operations succeed or fail together
       with transaction() as conn:
           execute_query("INSERT INTO users VALUES (...)", params, conn=conn)
           execute_query("UPDATE stats SET ... WHERE user_id = ?", (user_id,), conn=conn)
       ```

    3. Creating database backups:
       ```python
       # Create a backup
       backup_file = create_backup()
       print(f"Backup created at: {backup_file}")

       # Restore from backup
       success = restore_backup(backup_file)
       ```

    4. Monitoring database performance:
       ```python
       # Get performance statistics
       stats = get_performance_stats()
       print(f"Total queries: {stats['total_queries']}")
       print(f"Slow queries: {stats['slow_queries']}")
       print(f"Average query time: {stats['avg_query_time']:.4f}s")
       ```

    5. Getting database information:
       ```python
       # Get database information
       db_info = get_database_info()
       print(f"Database size: {db_info['size_formatted']}")
       print(f"Number of tables: {len(db_info['tables'])}")
       ```

    6. Optimizing the database:
       ```python
       # Optimize the database
       optimize_database()
       ```

    For more information, see the function documentation in the database_manager.py file.
    """

    return help_text

# --- Forum methods ---
def get_forum_posts(category='all', page=1, limit=10):
    """Get forum posts with pagination and category filtering."""
    try:
        with get_connection() as conn:
            cursor = conn.cursor()

            if category and category != 'all':
                query = """
                    SELECT id, title, content, username, category, created_at,
                           (SELECT COUNT(*) FROM forum_post_comments WHERE post_id = forum_posts.id) AS comment_count,
                           (SELECT COUNT(*) FROM forum_post_likes WHERE post_id = forum_posts.id) AS likes
                    FROM forum_posts
                    WHERE category = ?
                    ORDER BY created_at DESC
                    LIMIT ? OFFSET ?
                """
                offset = (page - 1) * limit
                cursor.execute(query, (category, limit, offset))
            else:
                query = """
                    SELECT id, title, content, username, category, created_at,
                           (SELECT COUNT(*) FROM forum_post_comments WHERE post_id = forum_posts.id) AS comment_count,
                           (SELECT COUNT(*) FROM forum_post_likes WHERE post_id = forum_posts.id) AS likes
                    FROM forum_posts
                    ORDER BY created_at DESC
                    LIMIT ? OFFSET ?
                """
                offset = (page - 1) * limit
                cursor.execute(query, (limit, offset))

            posts = []
            columns = [col[0] for col in cursor.description]
            for row in cursor.fetchall():
                post = dict(zip(columns, row))
                posts.append(post)

            return posts
    except Exception as e:
        logging.error(f"Error getting forum posts: {e}")
        return []

def count_forum_posts(category='all'):
    """Count total forum posts, optionally filtered by category."""
    try:
        with get_connection() as conn:
            cursor = conn.cursor()

            if category and category != 'all':
                query = "SELECT COUNT(*) FROM forum_posts WHERE category = ?"
                cursor.execute(query, (category,))
            else:
                query = "SELECT COUNT(*) FROM forum_posts"
                cursor.execute(query)

            return cursor.fetchone()[0]
    except Exception as e:
        logging.error(f"Error counting forum posts: {e}")
        return 0

def create_forum_post(post_data):
    """Create a new forum post."""
    try:
        with get_connection() as conn:
            cursor = conn.cursor()

            query = """
                INSERT INTO forum_posts (title, content, username, category, created_at)
                VALUES (?, ?, ?, ?, ?)
            """
            cursor.execute(query, (
                post_data['title'],
                post_data['content'],
                post_data['username'],
                post_data.get('category', 'general'),
                post_data.get('created_at', datetime.datetime.now().isoformat())
            ))
            conn.commit()

            return cursor.lastrowid
    except Exception as e:
        logging.error(f"Error creating forum post: {e}")
        return None

def get_top_contributors(limit=5):
    """Get top contributors based on forum activity and eco points."""
    try:
        with get_connection() as conn:
            cursor = conn.cursor()

            query = """
                SELECT username,
                       (SELECT COUNT(*) FROM forum_posts WHERE username = users.username) as post_count,
                       eco_points
                FROM users
                ORDER BY eco_points DESC, post_count DESC
                LIMIT ?
            """
            cursor.execute(query, (limit,))

            contributors = []
            columns = [col[0] for col in cursor.description]
            for row in cursor.fetchall():
                contributor = dict(zip(columns, row))
                contributors.append(contributor)

            return contributors
    except Exception as e:
        logging.error(f"Error getting top contributors: {e}")
        return []

# --- Challenge methods ---
def get_user_challenges(username, status='active'):
    """Get challenges for a user filtered by status."""
    try:
        with get_connection() as conn:
            cursor = conn.cursor()

            query = """
                SELECT c.id, c.name, c.description, c.points, c.icon, c.image,
                       c.start_date, c.end_date, c.difficulty,
                       uc.progress, uc.joined_date, uc.completed_date,
                       (SELECT COUNT(*) FROM user_challenges WHERE challenge_id = c.id) as participants
                FROM challenges c
                JOIN user_challenges uc ON c.id = uc.challenge_id
                WHERE uc.username = ? AND uc.status = ?
                ORDER BY
                    CASE WHEN ? = 'active' THEN uc.progress END DESC,
                    CASE WHEN ? = 'completed' THEN uc.completed_date END DESC
            """
            cursor.execute(query, (username, status, status, status))

            challenges = []
            columns = [col[0] for col in cursor.description]
            for row in cursor.fetchall():
                challenge = dict(zip(columns, row))
                challenges.append(challenge)

            return challenges
    except Exception as e:
        logging.error(f"Error getting user challenges: {e}")
        return []

def get_available_challenges(username):
    """Get challenges that are available to join (user hasn't joined yet)."""
    try:
        with get_connection() as conn:
            cursor = conn.cursor()

            query = """
                SELECT c.id, c.name, c.description, c.points, c.icon, c.image,
                       c.start_date, c.end_date, c.difficulty, c.duration,
                       (SELECT COUNT(*) FROM user_challenges WHERE challenge_id = c.id) as participants
                FROM challenges c
                WHERE c.id NOT IN (
                    SELECT challenge_id FROM user_challenges WHERE username = ?
                )
                AND c.end_date > datetime('now')
                ORDER BY c.start_date DESC
            """
            cursor.execute(query, (username,))

            challenges = []
            columns = [col[0] for col in cursor.description]
            for row in cursor.fetchall():
                challenge = dict(zip(columns, row))
                challenges.append(challenge)

            return challenges
    except Exception as e:
        logging.error(f"Error getting available challenges: {e}")
        return []

def join_challenge(username, challenge_id):
    """Join a challenge."""
    try:
        with get_connection() as conn:
            cursor = conn.cursor()

            # Check if already joined
            cursor.execute(
                "SELECT id FROM user_challenges WHERE username = ? AND challenge_id = ?",
                (username, challenge_id)
            )
            if cursor.fetchone():
                return False  # Already joined

            # Join challenge
            query = """
                INSERT INTO user_challenges (username, challenge_id, status, progress, joined_date)
                VALUES (?, ?, 'active', 0, ?)
            """
            cursor.execute(query, (
                username,
                challenge_id,
                datetime.datetime.now().isoformat()
            ))
            conn.commit()

            return True
    except Exception as e:
        logging.error(f"Error joining challenge: {e}")
        return False

def update_challenge_progress(username, challenge_id, progress):
    """Update progress for a challenge."""
    try:
        with get_connection() as conn:
            cursor = conn.cursor()

            # Get current challenge status
            cursor.execute(
                "SELECT status, progress FROM user_challenges WHERE username = ? AND challenge_id = ?",
                (username, challenge_id)
            )
            result = cursor.fetchone()
            if not result:
                return False  # Challenge not found

            current_status, _ = result  # _ is used to ignore the current_progress value

            # Check if completed
            completed_date = None
            new_status = current_status
            if progress >= 100 and current_status != 'completed':
                new_status = 'completed'
                completed_date = datetime.datetime.now().isoformat()

                # Get challenge points
                cursor.execute("SELECT points FROM challenges WHERE id = ?", (challenge_id,))
                challenge_points = cursor.fetchone()[0]

                # Update user eco points
                cursor.execute(
                    "UPDATE users SET eco_points = eco_points + ?, challenges_completed = challenges_completed + 1 WHERE username = ?",
                    (challenge_points, username)
                )

            # Update challenge progress
            if completed_date:
                query = """
                    UPDATE user_challenges
                    SET progress = ?, status = ?, completed_date = ?
                    WHERE username = ? AND challenge_id = ?
                """
                cursor.execute(query, (
                    progress,
                    new_status,
                    completed_date,
                    username,
                    challenge_id
                ))
            else:
                query = """
                    UPDATE user_challenges
                    SET progress = ?, status = ?
                    WHERE username = ? AND challenge_id = ?
                """
                cursor.execute(query, (
                    progress,
                    new_status,
                    username,
                    challenge_id
                ))

            conn.commit()
            return True
    except Exception as e:
        logging.error(f"Error updating challenge progress: {e}")
        return False

# --- Route methods ---
def get_sample_forum_posts(_limit=10):
    """Get sample forum posts for testing."""
    # Return dummy data for now
    # Note: _limit parameter is ignored in this implementation
    return [
        {
            'id': 1,
            'title': 'Best cycling routes in the city?',
            'content': 'I\'m looking for some nice cycling routes in the city. Any recommendations?',
            'username': 'cyclist123',
            'category': 'routes',
            'created_at': '2025-05-01T14:30:00',
            'comment_count': 5,
            'likes': 12
        },
        {
            'id': 2,
            'title': 'New bike lane on Main Street',
            'content': 'Has anyone tried the new bike lane on Main Street? It looks great!',
            'username': 'bikefan',
            'category': 'general',
            'created_at': '2025-05-02T09:15:00',
            'comment_count': 8,
            'likes': 24
        },
        {
            'id': 3,
            'title': 'Looking for cycling buddies',
            'content': 'Anyone interested in weekly group rides? I\'m thinking Saturday mornings.',
            'username': 'rideordie',
            'category': 'events',
            'created_at': '2025-05-03T16:45:00',
            'comment_count': 15,
            'likes': 30
        }
    ]

def initialize_database():
    """Initialize the database tables if they don't exist."""
    try:
        with get_connection() as conn:
            cursor = conn.cursor()

            # Create forum tables if they don't exist
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS forum_posts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    content TEXT NOT NULL,
                    username TEXT NOT NULL,
                    category TEXT DEFAULT 'general',
                    created_at TEXT NOT NULL
                )
            ''')

            cursor.execute('''
                CREATE TABLE IF NOT EXISTS forum_post_comments (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    post_id INTEGER NOT NULL,
                    username TEXT NOT NULL,
                    content TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    FOREIGN KEY (post_id) REFERENCES forum_posts (id) ON DELETE CASCADE
                )
            ''')

            cursor.execute('''
                CREATE TABLE IF NOT EXISTS forum_post_likes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    post_id INTEGER NOT NULL,
                    username TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    UNIQUE(post_id, username),
                    FOREIGN KEY (post_id) REFERENCES forum_posts (id) ON DELETE CASCADE
                )
            ''')

            # Create challenges tables if they don't exist
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS challenges (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    description TEXT NOT NULL,
                    points INTEGER NOT NULL,
                    start_date TEXT NOT NULL,
                    end_date TEXT NOT NULL,
                    difficulty INTEGER DEFAULT 1,
                    icon TEXT DEFAULT 'fas fa-leaf',
                    image TEXT,
                    duration TEXT DEFAULT '4 weeks'
                )
            ''')

            cursor.execute('''
                CREATE TABLE IF NOT EXISTS user_challenges (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT NOT NULL,
                    challenge_id INTEGER NOT NULL,
                    status TEXT NOT NULL,
                    progress INTEGER DEFAULT 0,
                    joined_date TEXT NOT NULL,
                    completed_date TEXT,
                    UNIQUE(username, challenge_id),
                    FOREIGN KEY (challenge_id) REFERENCES challenges (id) ON DELETE CASCADE
                )
            ''')

            # Create user related tables
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    username TEXT PRIMARY KEY,
                    password TEXT NOT NULL,
                    email TEXT NOT NULL,
                    name TEXT,
                    joined_date TEXT NOT NULL,
                    last_login TEXT,
                    eco_points INTEGER DEFAULT 0,
                    badge TEXT,
                    total_routes INTEGER DEFAULT 0,
                    total_posts INTEGER DEFAULT 0,
                    challenges_completed INTEGER DEFAULT 0,
                    preferences TEXT
                )
            ''')

            # Create routes table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS routes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    username TEXT NOT NULL,
                    start_point TEXT NOT NULL,
                    end_point TEXT NOT NULL,
                    distance REAL NOT NULL,
                    duration INTEGER NOT NULL,
                    route_type TEXT DEFAULT 'fastest',
                    coordinates TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    notes TEXT
                )
            ''')

            # Add some sample data if tables are empty
            cursor.execute("SELECT COUNT(*) FROM challenges")
            if cursor.fetchone()[0] == 0:
                # Insert sample challenges
                sample_challenges = [
                    (
                        "Commuter Champion",
                        "Replace your car commute with cycling for 20 days this month.",
                        500,
                        "2025-05-01",
                        "2025-05-31",
                        2,
                        "fas fa-bicycle",
                        "commuter.jpg",
                        "1 month"
                    ),
                    (
                        "Carbon Footprint Reducer",
                        "Save 50kg of CO2 emissions through cycling this month.",
                        300,
                        "2025-05-01",
                        "2025-05-31",
                        3,
                        "fas fa-leaf",
                        "carbon.jpg",
                        "1 month"
                    ),
                    (
                        "Century Rider",
                        "Complete a 100km ride in a single session.",
                        1000,
                        "2025-05-01",
                        "2025-06-30",
                        5,
                        "fas fa-road",
                        "century.jpg",
                        "2 months"
                    ),
                    (
                        "Social Cyclist",
                        "Participate in 5 group rides this month.",
                        200,
                        "2025-05-01",
                        "2025-05-31",
                        1,
                        "fas fa-users",
                        "social.jpg",
                        "1 month"
                    ),
                    (
                        "Early Bird",
                        "Complete 10 rides before 8:00 AM.",
                        300,
                        "2025-05-01",
                        "2025-05-31",
                        2,
                        "fas fa-sun",
                        "early.jpg",
                        "1 month"
                    )
                ]

                cursor.executemany(
                    """
                    INSERT INTO challenges (name, description, points, start_date, end_date, difficulty, icon, image, duration)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    sample_challenges
                )

            conn.commit()
    except Exception as e:
        logging.error(f"Error initializing database: {e}")
        raise

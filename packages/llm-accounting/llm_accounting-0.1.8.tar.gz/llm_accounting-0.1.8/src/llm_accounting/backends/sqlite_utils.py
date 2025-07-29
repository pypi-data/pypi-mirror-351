import sqlite3
from pathlib import Path


def validate_db_filename(filename: str):
    """Validate database filename meets requirements"""
    # Handle SQLite URI format
    clean_name = filename.split("?")[0].replace("file:", "")
    db_path = Path(clean_name)

    # Allow in-memory databases
    if clean_name == ":memory:":
        return

    # Check for valid extensions
    if not any(
        clean_name.lower().endswith(ext) for ext in (".sqlite", ".sqlite3", ".db")
    ):
        raise ValueError(
            f"Invalid database filename '{filename}'. "
            "Must end with .sqlite, .sqlite3 or .db"
        )

    # Check for protected paths (Windows specific examples)
    protected_paths = [
        Path("C:/Windows"),
        Path("C:/Program Files"),
        Path("C:/Program Files (x86)"),
        Path("/root"),  # Common protected path on Linux/Unix
    ]

    # Normalize path for comparison
    absolute_db_path = db_path.resolve()

    def is_subpath(child, parent):
        try:
            child = child.resolve()
            parent = parent.resolve()
            return str(child).startswith(str(parent))
        except Exception:
            return False

    try:
        if any(
            is_subpath(absolute_db_path, protected_path)
            for protected_path in protected_paths
        ):
            raise PermissionError(
                f"Access to protected path '{filename}' is not allowed."
            )
    except Exception as e:
        raise PermissionError(
            f"Access to protected path '{filename}' is not allowed (error during path check: {str(e)})."
        )


def initialize_db_schema(conn: sqlite3.Connection) -> None:
    """Initialize the SQLite database schema (create table and add missing columns)"""
    # Create accounting_entries table if it doesn't exist
    conn.execute(
        """CREATE TABLE IF NOT EXISTS accounting_entries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            model TEXT NOT NULL,
            prompt_tokens INTEGER,
            completion_tokens INTEGER,
            total_tokens INTEGER,
            local_prompt_tokens INTEGER,
            local_completion_tokens INTEGER,
            local_total_tokens INTEGER,
            project TEXT DEFAULT NULL,
            cost REAL NOT NULL,
            execution_time REAL NOT NULL,
            caller_name TEXT NOT NULL DEFAULT '',
            username TEXT NOT NULL DEFAULT '',
            cached_tokens INTEGER NOT NULL DEFAULT 0,
            reasoning_tokens INTEGER NOT NULL DEFAULT 0
        )"""
    )

    # Create usage_limits table if it doesn't exist
    conn.execute(
        """CREATE TABLE IF NOT EXISTS usage_limits (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            scope TEXT NOT NULL,
            limit_type TEXT NOT NULL,
            model TEXT,
            username TEXT,
            caller_name TEXT,
            project_name TEXT DEFAULT NULL, -- Added project_name
            max_value REAL NOT NULL,
            interval_unit TEXT NOT NULL,
            interval_value INTEGER NOT NULL,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        )"""
    )

    # Check for and add any missing columns to accounting_entries
    cursor = conn.execute("PRAGMA table_info(accounting_entries)")
    accounting_columns = {column[1] for column in cursor.fetchall()}

    if "local_prompt_tokens" not in accounting_columns:
        conn.execute(
            "ALTER TABLE accounting_entries ADD COLUMN local_prompt_tokens INTEGER"
        )
    if "local_completion_tokens" not in accounting_columns:
        conn.execute(
            "ALTER TABLE accounting_entries ADD COLUMN local_completion_tokens INTEGER"
        )
    if "local_total_tokens" not in accounting_columns:
        conn.execute(
            "ALTER TABLE accounting_entries ADD COLUMN local_total_tokens INTEGER"
        )
    if "caller_name" not in accounting_columns:
        conn.execute(
            'ALTER TABLE accounting_entries ADD COLUMN caller_name TEXT NOT NULL DEFAULT ""'
        )
    if "username" not in accounting_columns:
        conn.execute(
            'ALTER TABLE accounting_entries ADD COLUMN username TEXT NOT NULL DEFAULT ""'
        )
    if "cached_tokens" not in accounting_columns:
        conn.execute(
            "ALTER TABLE accounting_entries ADD COLUMN cached_tokens INTEGER NOT NULL DEFAULT 0"
        )
    if "reasoning_tokens" not in accounting_columns:
        conn.execute(
            "ALTER TABLE accounting_entries ADD COLUMN reasoning_tokens INTEGER NOT NULL DEFAULT 0"
        )
    if "project" not in accounting_columns:
        conn.execute(
            'ALTER TABLE accounting_entries ADD COLUMN project TEXT DEFAULT NULL'
        )

    # Check for and add any missing columns to usage_limits
    cursor = conn.execute("PRAGMA table_info(usage_limits)")
    usage_limits_columns = {column[1] for column in cursor.fetchall()}
    
    if 'project_name' not in usage_limits_columns:
        conn.execute('ALTER TABLE usage_limits ADD COLUMN project_name TEXT DEFAULT NULL')

    conn.commit()

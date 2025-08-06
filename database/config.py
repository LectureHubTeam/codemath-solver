# database/config.py
"""
Database configuration
"""

from pathlib import Path

# Database configuration
DATABASE_CONFIG = {
    "db_path": "database/codemath_solver.db",
    "backup_dir": "database/backups",
    "max_backups": 10,
    "auto_backup": True,
    "schema_path": "database/sql/version1/0001_init_database.sql",
}

# Table configurations
TABLE_CONFIGS = {
    "problems": {
        "batch_size": 100,
        "indexes": ["problem_code", "category", "difficulty", "solved_status"],
    },
    "submissions": {
        "batch_size": 50,
        "indexes": ["problem_id", "status", "submitted_at"],
    },
    "crawl_sessions": {"batch_size": 10, "indexes": ["crawl_started_at", "status"]},
}

# Migration settings
MIGRATION_CONFIG = {
    "csv_encoding": "utf-8",
    "skip_duplicates": True,
    "validate_data": True,
}


def get_database_path() -> str:
    """Get database path"""
    return DATABASE_CONFIG["db_path"]


def get_backup_dir() -> str:
    """Get backup directory"""
    backup_dir = DATABASE_CONFIG["backup_dir"]
    Path(backup_dir).mkdir(parents=True, exist_ok=True)
    return backup_dir


def ensure_database_directory():
    """Ensure database directory exists"""
    db_path = Path(DATABASE_CONFIG["db_path"])
    db_path.parent.mkdir(parents=True, exist_ok=True)

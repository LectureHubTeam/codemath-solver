# database/migrate.py
"""
Migration scripts for database
"""

import os

import pandas as pd

from database.manager import DatabaseManager


def migrate_csv_to_database(csv_file: str, platform: int):
    """Migrate data from CSV to database"""
    print(f"🔄 Migrating data from {csv_file} to database...")

    db_manager = DatabaseManager()

    try:
        migrated_count = db_manager.migrate_from_csv(csv_file, platform)
        print(f"✅ Successfully migrated {migrated_count} problems to database")

        # Show statistics
        stats = db_manager.get_statistics()
        print("📊 Database statistics:")
        print(f"   - Total problems: {stats['total_problems']}")
        print(f"   - Solved problems: {stats['solved_problems']}")
        print(f"   - Unsolved problems: {stats['unsolved_problems']}")

    except Exception as e:
        print(f"❌ Migration failed: {e}")
        raise


def migrate_all_csv_files():
    """Migrate all CSV files in the project"""
    csv_files = [
        ("lqdoj_problems_data.csv", 2),
        ("problems_data.csv", 1),
    ]

    for csv_file, platform in csv_files:
        if os.path.exists(csv_file):
            print(f"\n📁 Processing {csv_file} for {platform}...")
            migrate_csv_to_database(csv_file, platform)
        else:
            print(f"⚠️  CSV file not found: {csv_file}")


def create_backup():
    """Create a backup of the database"""
    db_manager = DatabaseManager()
    backup_path = (
        f"database/backup/backup_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.db"
    )
    os.makedirs(os.path.dirname(backup_path), exist_ok=True)
    try:
        db_manager.backup_database(backup_path)
        print(f"✅ Database backup created: {backup_path}")
    except Exception as e:
        print(f"❌ Backup failed: {e}")


def export_database_to_csv():
    """Export database to CSV files"""
    db_manager = DatabaseManager()

    try:
        # Export problems
        problems_count = db_manager.export_to_csv(
            "database/problems_export.csv", "problems"
        )
        print(f"✅ Exported {problems_count} problems to database/problems_export.csv")

        # Export submissions
        submissions_count = db_manager.export_to_csv(
            "database/submissions_export.csv", "submissions"
        )
        print(
            f"✅ Exported {submissions_count} submissions to database/submissions_export.csv"
        )

    except Exception as e:
        print(f"❌ Export failed: {e}")


if __name__ == "__main__":
    print("🚀 Starting database migration...")

    # Create backup first
    create_backup()

    # Migrate all CSV files
    migrate_all_csv_files()

    # Export to CSV for verification
    export_database_to_csv()

    print("🎉 Migration completed!")

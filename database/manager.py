import os
import sqlite3
from pathlib import Path

from database.enums import Difficulty, SolvedStatus

from .crud import ProblemCRUD, SubmissionCRUD
from .models import Problem


class DatabaseManager:
    """Main database manager class"""

    def __init__(
        self,
        db_path: str = "database/codemath_solver.db",
        schema_path: str = "database/sql/version1/0001_init_database.sql",
    ):
        self.db_path = db_path
        self.schema_path = schema_path
        self._ensure_db_directory()
        self._init_database()

        # Initialize CRUD classes
        self.problems = ProblemCRUD(db_path)
        self.submissions = SubmissionCRUD(db_path)

    def _ensure_db_directory(self):
        """Ensure database directory exists"""
        db_dir = Path(self.db_path).parent
        db_dir.mkdir(parents=True, exist_ok=True)

    def _init_database(self):
        """Initialize database with schema"""
        if not os.path.exists(self.schema_path):
            raise FileNotFoundError(f"Schema file not found: {self.schema_path}")

        with open(self.schema_path, "r", encoding="utf-8") as f:
            schema = f.read()

        with sqlite3.connect(self.db_path) as conn:
            conn.executescript(schema)
            conn.commit()

    def get_connection(self) -> sqlite3.Connection:
        """Get database connection"""
        return sqlite3.connect(self.db_path)

    def close(self):
        """Close database connection"""
        # SQLite connections are automatically closed when they go out of scope
        pass

    def backup_database(self, backup_path: str):
        """Create a backup of the database"""
        import shutil

        shutil.copy2(self.db_path, backup_path)

    def get_database_info(self) -> dict:
        """Get database information"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # Get table counts
            tables = [
                "problems",
                "submissions",
                "tags",
            ]
            counts = {}

            for table in tables:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                counts[table] = cursor.fetchone()[0]

            # Get database size
            db_size = os.path.getsize(self.db_path)

            return {
                "database_path": self.db_path,
                "database_size_mb": round(db_size / (1024 * 1024), 2),
                "table_counts": counts,
            }

    def _get_points(self, points: str) -> int:
        """Get points from string"""
        if isinstance(points, int):
            return points

        if points.endswith("p"):
            return int(points.replace("p", ""))

        return int(points.replace(",", ""))

    def _get_ac_rate(self, ac_rate: str) -> float:
        """Get ac rate from string"""
        if isinstance(ac_rate, str):
            ac_rate = ac_rate.replace(",", "")
            if ac_rate.endswith("%"):
                ac_rate = float(ac_rate.replace("%", ""))
        if isinstance(ac_rate, float):
            return ac_rate

        return float(ac_rate.replace(",", ""))

    def _get_solved_status(self, solved: str | int) -> SolvedStatus:
        if solved in [1, "1", "Solved"]:
            return SolvedStatus.SOLVED.value
        if solved in [0, "0", "Unsolved"]:
            return SolvedStatus.UNSOLVED.value
        return SolvedStatus.NOT_SOLVED.value

    def migrate_from_csv(self, csv_file: str, platform: int):
        """Migrate data from CSV file to database"""
        import pandas as pd

        if not os.path.exists(csv_file):
            raise FileNotFoundError(f"CSV file not found: {csv_file}")

        df = pd.read_csv(csv_file)
        migrated_count = 0

        for _, row in df.iterrows():
            # Create problem object from CSV row
            problem = Problem(
                problem_code=row.get("problem-code", "").lower(),
                problem_name=row.get("problem-name", ""),
                platform=platform,
                category=row.get("category", ""),
                difficulty=row.get("difficulty", Difficulty.UNKNOWN),
                points=self._get_points(row.get("points", 0)),
                ac_rate=self._get_ac_rate(row.get("ac-rate", 0)),
                users_solved=int(row.get("users", 0)) if row.get("users") else 0,
                solved_status=self._get_solved_status(
                    row.get("solved", SolvedStatus.UNSOLVED.value)
                ),
            )

            # Check if problem already exists
            existing = self.problems.get_by_code(problem.problem_code)
            if not existing:
                self.problems.create(problem)
                migrated_count += 1

        return migrated_count

    def export_to_csv(self, output_file: str, table: str = "problems"):
        """Export database table to CSV"""
        import pandas as pd

        with sqlite3.connect(self.db_path) as conn:
            df = pd.read_sql_query(f"SELECT * FROM {table}", conn)
            df.to_csv(output_file, index=False)

        return len(df)

    def get_statistics(self) -> dict:
        """Get database statistics"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            stats = {}

            # Problem statistics
            cursor.execute("SELECT COUNT(*) FROM problems")
            stats["total_problems"] = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM problems WHERE solved_status = 1")
            stats["solved_problems"] = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM problems WHERE solved_status = 0")
            stats["unsolved_problems"] = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM problems WHERE solved_status = -1")
            stats["not_solved_problems"] = cursor.fetchone()[0]

            # Submission statistics
            cursor.execute("SELECT COUNT(*) FROM submissions")
            stats["total_submissions"] = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM submissions WHERE status = 'AC'")
            stats["accepted_submissions"] = cursor.fetchone()[0]

            # Platform statistics
            cursor.execute("SELECT platform, COUNT(*) FROM problems GROUP BY platform")
            stats["problems_by_platform"] = dict(cursor.fetchall())

            # Category statistics
            cursor.execute("SELECT category, COUNT(*) FROM problems GROUP BY category")
            stats["problems_by_category"] = dict(cursor.fetchall())

            return stats

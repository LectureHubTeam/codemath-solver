import sqlite3
from datetime import datetime
from typing import List, Optional

from .models import Problem, Submission


class ProblemCRUD:
    """CRUD operations for problems table"""

    def __init__(self, db_path: str):
        self.db_path = db_path

    def create(self, problem: Problem) -> int:
        """Create a new problem"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO problems (
                    problem_code, problem_name, platform, problem_url,
                    category, difficulty, points, ac_rate, users_solved, solved_status,
                    submission_count, best_submission_id, created_at, updated_at, del_flag, notes
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    problem.problem_code,
                    problem.problem_name,
                    problem.platform,
                    problem.problem_url,
                    problem.category,
                    problem.difficulty,
                    problem.points,
                    problem.ac_rate,
                    problem.users_solved,
                    problem.solved_status,
                    problem.submission_count,
                    problem.best_submission_id,
                    problem.created_at or datetime.now(),
                    problem.updated_at or datetime.now(),
                    problem.del_flag,
                    problem.notes,
                ),
            )
            return cursor.lastrowid

    def get_by_id(self, problem_id: int) -> Optional[Problem]:
        """Get problem by ID"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM problems WHERE id = ?", (problem_id,))
            row = cursor.fetchone()
            if row:
                return self._row_to_problem(row)
            return None

    def get_by_code(self, problem_code: str) -> Optional[Problem]:
        """Get problem by code (deprecated - use get_by_code_and_platform instead)"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM problems WHERE problem_code = ?", (problem_code,)
            )
            row = cursor.fetchone()
            if row:
                return self._row_to_problem(row)
            return None

    def get_by_code_and_platform(
        self, problem_code: str, platform: int
    ) -> Optional[Problem]:
        """Get problem by code and platform"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM problems WHERE problem_code = ? AND platform = ?",
                (problem_code, platform),
            )
            row = cursor.fetchone()
            if row:
                return self._row_to_problem(row)
            return None

    def get_all(self, limit: Optional[int] = None, offset: int = 0) -> List[Problem]:
        """Get all problems with optional pagination"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            query = "SELECT * FROM problems ORDER BY created_at DESC"
            if limit:
                query += f" LIMIT {limit} OFFSET {offset}"
            cursor.execute(query)
            rows = cursor.fetchall()
            return [self._row_to_problem(row) for row in rows]

    def update(self, problem: Problem) -> bool:
        """Update a problem"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                UPDATE problems SET
                    problem_name = ?, platform = ?, problem_url = ?,
                    category = ?, difficulty = ?, points = ?, ac_rate = ?, users_solved = ?,
                    solved_status = ?, submission_count = ?, best_submission_id = ?,
                    updated_at = ?, del_flag = ?, notes = ?
                WHERE id = ?
            """,
                (
                    problem.problem_name,
                    problem.platform,
                    problem.problem_url,
                    problem.category,
                    problem.difficulty,
                    problem.points,
                    problem.ac_rate,
                    problem.users_solved,
                    problem.solved_status,
                    problem.submission_count,
                    problem.best_submission_id,
                    datetime.now(),
                    problem.del_flag,
                    problem.notes,
                    problem.id,
                ),
            )
            return cursor.rowcount > 0

    def delete(self, problem_id: int) -> bool:
        """Delete a problem"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM problems WHERE id = ?", (problem_id,))
            return cursor.rowcount > 0

    def search(self, **kwargs) -> List[Problem]:
        """Search problems by criteria"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            conditions = []
            params = []

            for key, value in kwargs.items():
                if value is not None:
                    conditions.append(f"{key} = ?")
                    params.append(value)

            if not conditions:
                return self.get_all()

            query = f"SELECT * FROM problems WHERE {' AND '.join(conditions)} ORDER BY created_at DESC"
            cursor.execute(query, params)
            rows = cursor.fetchall()
            return [self._row_to_problem(row) for row in rows]

    def _row_to_problem(self, row) -> Problem:
        """Convert database row to Problem object"""
        return Problem(
            id=row[0],
            problem_code=row[1],
            problem_name=row[2],
            platform=row[3],
            category=row[4],
            difficulty=row[5],
            points=row[6],
            ac_rate=row[7],
            users_solved=row[8],
            solved_status=row[9],
            submission_count=row[10],
            best_submission_id=row[11],
            created_at=datetime.fromisoformat(row[12]) if row[12] else None,
            updated_at=datetime.fromisoformat(row[13]) if row[13] else None,
            del_flag=bool(row[14]),
            notes=row[15] or "",
        )


class SubmissionCRUD:
    """CRUD operations for submissions table"""

    def __init__(self, db_path: str):
        self.db_path = db_path

    def create(self, submission: Submission) -> int:
        """Create a new submission"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO submissions (
                    problem_id, submission_code, language, status,
                    execution_time, memory_used, submitted_at, is_best
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    submission.problem_id,
                    submission.submission_code,
                    submission.language,
                    submission.status,
                    submission.execution_time,
                    submission.memory_used,
                    submission.submitted_at or datetime.now(),
                    submission.is_best,
                ),
            )
            return cursor.lastrowid

    def get_by_problem_id(self, problem_id: int) -> List[Submission]:
        """Get all submissions for a problem"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM submissions WHERE problem_id = ? ORDER BY submitted_at DESC",
                (problem_id,),
            )
            rows = cursor.fetchall()
            return [self._row_to_submission(row) for row in rows]

    def get_best_submission(self, problem_id: int) -> Optional[Submission]:
        """Get best submission for a problem"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM submissions WHERE problem_id = ? AND is_best = 1",
                (problem_id,),
            )
            row = cursor.fetchone()
            if row:
                return self._row_to_submission(row)
            return None

    def _row_to_submission(self, row) -> Submission:
        """Convert database row to Submission object"""
        return Submission(
            id=row[0],
            problem_id=row[1],
            submission_code=row[2],
            language=row[3],
            status=row[4],
            execution_time=row[5],
            memory_used=row[6],
            submitted_at=datetime.fromisoformat(row[7]) if row[7] else None,
            is_best=bool(row[8]),
        )

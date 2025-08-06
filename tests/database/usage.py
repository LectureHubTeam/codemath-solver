# Example usage
from database import DatabaseManager, Problem, Submission
from database.config import DATABASE_CONFIG
from database.enums import SolvedStatus

# Initialize database
db = DatabaseManager(
    db_path=DATABASE_CONFIG["db_path"],
    schema_path=DATABASE_CONFIG["schema_path"],
)

# Create a problem
problem = Problem(
    problem_code="tt25candy",
    problem_name="Thích kẹo ngọt",
    platform="LQDOJ",
    category="ABC",
    points=2000,
    ac_rate=17.0,
    users_solved=22,
    solved_status=SolvedStatus.UNSOLVED,
)

# Save to database
problem_id = db.problems.create(problem)

# Create a submission
submission = Submission(
    problem_id=problem_id,
    submission_code="print('Hello World')",
    language="Python",
    status="AC",
    execution_time=100,
    memory_used=1024,
    is_best=True,
)

# Save submission
submission_id = db.submissions.create(submission)

# Get problem with submissions
problem = db.problems.get_by_id(problem_id)
submissions = db.submissions.get_by_problem_id(problem_id)

print(f"Problem: {problem.problem_name}")
print(f"Submissions: {len(submissions)}")

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, Optional


@dataclass
class Problem:
    """Model cho bảng problems"""

    id: Optional[int] = None
    problem_code: str = ""
    problem_name: str = ""
    platform: int = 0
    problem_url: str = ""
    category: str = ""
    difficulty: str = ""
    points: int = 0
    ac_rate: float = 0.0
    users_solved: int = 0
    solved_status: int = -1
    submission_count: int = 0
    best_submission_id: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    del_flag: bool = False
    notes: str = ""

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "id": self.id,
            "problem_code": self.problem_code,
            "problem_name": self.problem_name,
            "platform": self.platform,
            "problem_url": self.problem_url,
            "category": self.category,
            "difficulty": self.difficulty,
            "points": self.points,
            "ac_rate": self.ac_rate,
            "users_solved": self.users_solved,
            "solved_status": self.solved_status,
            "submission_count": self.submission_count,
            "best_submission_id": self.best_submission_id,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "del_flag": self.del_flag,
            "notes": self.notes,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Problem":
        """Create from dictionary"""
        return cls(**data)


@dataclass
class Submission:
    """Model cho bảng submissions"""

    id: Optional[int] = None
    problem_id: int = 0
    submission_code: str = ""
    language: str = "Python"
    status: str = ""
    execution_time: int = 0
    memory_used: int = 0
    submitted_at: Optional[datetime] = None
    is_best: bool = False

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "id": self.id,
            "problem_id": self.problem_id,
            "submission_code": self.submission_code,
            "language": self.language,
            "status": self.status,
            "execution_time": self.execution_time,
            "memory_used": self.memory_used,
            "submitted_at": self.submitted_at,
            "is_best": self.is_best,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Submission":
        """Create from dictionary"""
        return cls(**data)


@dataclass
class Tag:
    """Model cho bảng tags"""

    id: Optional[int] = None
    name: str = ""
    description: str = ""
    created_at: Optional[datetime] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "created_at": self.created_at,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Tag":
        """Create from dictionary"""
        return cls(**data)


@dataclass
class Solution:
    """Model cho bảng solutions"""

    id: Optional[int] = None
    problem_id: int = 0
    solution_type: str = "Explanation"
    content: str = ""
    language: str = "Vietnamese"
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "id": self.id,
            "problem_id": self.problem_id,
            "solution_type": self.solution_type,
            "content": self.content,
            "language": self.language,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Solution":
        """Create from dictionary"""
        return cls(**data)

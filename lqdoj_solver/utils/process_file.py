"""
LQDOJ file processing utilities.
Uses shared utilities from base_solver for common functionality.
"""

from base_solver.shared_utils import clear_data as shared_clear_data


def clear_data(folder_path: str = "data"):
    """
    Clear all files in the specified folder.
    Uses shared utility for consistency.

    Args:
        folder_path: Path to the folder to clear
    """
    shared_clear_data(folder_path)

"""
LQDOJ Gemini Solver implementation.
Inherits from BaseGeminiSolver to provide LQDOJ-specific functionality.
"""

from base_solver.base_llm import BaseGeminiSolver
from conf.lqdoj_settings import LQDOJ_GEMINI_PROMPT_PDF, LQDOJ_GEMINI_PROMPT_TEXT


class LQDOJGeminiSolver(BaseGeminiSolver):
    """
    LQDOJ-specific Gemini solver implementation.
    Inherits common functionality from BaseGeminiSolver.
    """

    def get_prompt_text(self, problem_text: str) -> str:
        """
        Get the text prompt for LQDOJ problems.

        Args:
            problem_text: The problem text to format

        Returns:
            Formatted prompt string for LQDOJ
        """
        return LQDOJ_GEMINI_PROMPT_TEXT.format(problem_text=problem_text)

    def get_prompt_pdf(self) -> str:
        """
        Get the PDF prompt for LQDOJ problems.

        Returns:
            PDF prompt string for LQDOJ
        """
        return LQDOJ_GEMINI_PROMPT_PDF

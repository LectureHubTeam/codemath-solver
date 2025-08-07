"""
CodeMath Gemini Solver implementation.
Inherits from BaseGeminiSolver to provide CodeMath-specific functionality.
"""

from base_solver.base_llm import BaseGeminiSolver
from conf.codemath_settings import (
    CODEMATH_GEMINI_PROMPT_PDF,
    CODEMATH_GEMINI_PROMPT_TEXT,
)


class CodeMathGeminiSolver(BaseGeminiSolver):
    """
    CodeMath-specific Gemini solver implementation.
    Inherits common functionality from BaseGeminiSolver.
    """

    def get_prompt_text(self, problem_text: str) -> str:
        """
        Get the text prompt for CodeMath problems.

        Args:
            problem_text: The problem text to format

        Returns:
            Formatted prompt string for CodeMath
        """
        return CODEMATH_GEMINI_PROMPT_TEXT.format(problem_text=problem_text)

    def get_prompt_pdf(self) -> str:
        """
        Get the PDF prompt for CodeMath problems.

        Returns:
            PDF prompt string for CodeMath
        """
        return CODEMATH_GEMINI_PROMPT_PDF


if __name__ == "__main__":
    input_file = "data/chiabi.pdf"  # Replace with your input file path
    solver = CodeMathGeminiSolver()
    solver.solve_problem(input_file, mode="pdf")

"""
CodeMath web automation agent.
Inherits from BaseAgent to provide CodeMath-specific functionality.
"""

from base_solver.base_agent import BaseAgent
from codemath_solver.agent.llm import CodeMathGeminiSolver
from conf.agent_settings import CODEMATH_AGENT_CONFIG


class CodeMathAgent(BaseAgent):
    """
    CodeMath-specific web automation agent.
    Inherits common functionality from BaseAgent.
    """

    def __init__(self):
        super().__init__(
            url_base=CODEMATH_AGENT_CONFIG["url_base"],
            prefix=CODEMATH_AGENT_CONFIG["prefix"],
            solved_status_icon=CODEMATH_AGENT_CONFIG["solved_status_icon"],
            unsolved_status_icon=CODEMATH_AGENT_CONFIG["unsolved_status_icon"],
            select_file_submit=CODEMATH_AGENT_CONFIG["select_file_submit"],
            button_submit=CODEMATH_AGENT_CONFIG["button_submit"],
            problem_title_class=CODEMATH_AGENT_CONFIG["problem_title_class"],
        )

    def create_solver(self):
        """
        Create the CodeMath solver instance.

        Returns:
            CodeMath solver instance
        """
        return CodeMathGeminiSolver()


if __name__ == "__main__":
    agent = CodeMathAgent()
    agent.process_problems(["chiabi"])

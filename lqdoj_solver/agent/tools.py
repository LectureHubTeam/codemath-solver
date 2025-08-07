"""
LQDOJ web automation agent.
Inherits from BaseAgent to provide LQDOJ-specific functionality.
"""

from base_solver.base_agent import BaseAgent
from conf.agent_settings import LQDOJ_AGENT_CONFIG
from lqdoj_solver.agent.llm import LQDOJGeminiSolver


class LQDOJAgent(BaseAgent):
    """
    LQDOJ-specific web automation agent.
    Inherits common functionality from BaseAgent.
    """

    def __init__(self):
        super().__init__(
            url_base=LQDOJ_AGENT_CONFIG["url_base"],
            prefix=LQDOJ_AGENT_CONFIG["prefix"],
            solved_status_icon=LQDOJ_AGENT_CONFIG["solved_status_icon"],
            unsolved_status_icon=LQDOJ_AGENT_CONFIG["unsolved_status_icon"],
            select_file_submit=LQDOJ_AGENT_CONFIG["select_file_submit"],
            button_submit=LQDOJ_AGENT_CONFIG["button_submit"],
            problem_title_class=LQDOJ_AGENT_CONFIG["problem_title_class"],
        )

    def create_solver(self):
        """
        Create the LQDOJ solver instance.

        Returns:
            LQDOJ solver instance
        """
        return LQDOJGeminiSolver()


if __name__ == "__main__":
    agent = LQDOJAgent()
    agent.process_problems(["ktp2a11", "skydef", "mang1cb06"])

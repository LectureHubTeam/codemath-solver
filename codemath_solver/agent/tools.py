"""
CodeMath web automation agent.
Inherits from BaseAgent to provide CodeMath-specific functionality.
"""

import os
import time

from selenium.webdriver.common.by import By

from base_solver.base_agent import BaseAgent
from codemath_solver.agent.llm import CodeMathGeminiSolver


class CodeMathAgent(BaseAgent):
    """
    CodeMath-specific web automation agent.
    Inherits common functionality from BaseAgent.
    """

    def __init__(
        self, url_base: str = "https://laptrinh.codemath.vn", prefix: str = "codemath"
    ):
        super().__init__(url_base=url_base, prefix=prefix)

    def create_solver(self):
        """
        Create the CodeMath solver instance.

        Returns:
            CodeMath solver instance
        """
        return CodeMathGeminiSolver()

    def submit_problem(self, submission_file: str):
        """
        Submit solution file to CodeMath website.

        Args:
            submission_file: Path to the solution file
        """
        # CodeMath có thể có cấu trúc submit khác

        self.driver.get(self.get_submission_url())
        time.sleep(1)

        file_input = self.driver.find_element(By.ID, "file_select")
        submission_file = os.path.join(self.project_root, submission_file)
        file_input.send_keys(submission_file)
        self.click_button(
            path='//*[@id="problem_submit"]/div[2]/input[2]', by_type="xpath"
        )
        time.sleep(3)


if __name__ == "__main__":
    agent = CodeMathAgent()
    agent.process_problems(["chiabi"])

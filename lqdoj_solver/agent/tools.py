"""
LQDOJ web automation agent.
Inherits from BaseAgent to provide LQDOJ-specific functionality.
"""

import os
import time

from selenium.webdriver.common.by import By

from base_solver.base_agent import BaseAgent
from lqdoj_solver.agent.llm import LQDOJGeminiSolver


class LQDOJAgent(BaseAgent):
    """
    LQDOJ-specific web automation agent.
    Inherits common functionality from BaseAgent.
    """

    def __init__(self, url_base: str = "https://lqdoj.edu.vn", prefix: str = "lqdoj"):
        super().__init__(url_base=url_base, prefix=prefix)

    def create_solver(self):
        """
        Create the LQDOJ solver instance.

        Returns:
            LQDOJ solver instance
        """
        return LQDOJGeminiSolver()

    def submit_problem(self, submission_file: str):
        """
        Submit solution file to LQDOJ website.

        Args:
            submission_file: Path to the solution file
        """
        self.driver.get(self.get_submission_url())
        time.sleep(1)

        file_input = self.driver.find_element(By.ID, "id_source_file")
        submission_file = os.path.join(self.project_root, submission_file)
        file_input.send_keys(submission_file)
        self.click_button(path='//*[@id="submit-button"]', by_type="xpath")
        time.sleep(3)


if __name__ == "__main__":
    agent = LQDOJAgent()
    agent.process_problems(["ktp2a11", "skydef", "mang1cb06"])

import time

import pyautogui
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager

from codemath_solver.agent.llm import GeminiSolver
from codemath_solver.utils.process_file import clear_data


class CodeMathAgent:
    def __init__(self):
        self.solver = GeminiSolver()
        options = webdriver.ChromeOptions()
        options.add_argument("--start-maximized")
        options.debugger_address = "localhost:9222"
        self.driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()), options=options
        )

    def click_button(self, path: str, by_type: str = "id", wait_time: int = 10):
        if by_type == "id":
            by = By.ID
        elif by_type == "xpath":
            by = By.XPATH
        else:
            raise ValueError(f"Unsupported by_type: {by_type}")
        try:
            button = WebDriverWait(self.driver, wait_time).until(
                EC.element_to_be_clickable((by, path))
            )
            button.click()
        except Exception as e:
            print(f"❌ Button not found: {e}")

    def download_problem(self, file_name: str):
        self.click_button(path="pdf_button", by_type="id")
        time.sleep(3)
        print("📂 Pressing Enter to save PDF...")
        pyautogui.press("enter")
        time.sleep(3)
        pyautogui.write(file_name, interval=0.25)
        time.sleep(2)
        pyautogui.press("enter")
        time.sleep(2)

    def submit_problem(self, submission_file: str):
        self.click_button(path='//*[@id="content-right"]/div/a', by_type="xpath")
        time.sleep(3)
        file_input = self.driver.find_element(By.ID, "file_select")
        file_input.send_keys(submission_file)
        self.click_button(
            path='//*[@id="problem_submit"]/div[2]/input[2]', by_type="xpath"
        )
        time.sleep(3)

    def process_problems(self, problems_code: list):
        URLS = [
            f"https://laptrinh.codemath.vn/problem/{code}" for code in problems_code
        ]
        try:
            for index, url in enumerate(URLS):
                file_name = url.split("/")[-1] + ".pdf"
                print(f"🔹 Accessing: {url}")
                self.driver.get(url)
                time.sleep(2)
                self.download_problem(file_name=file_name)
                file_name_path = f"data/{file_name}"
                output_path = self.solver.solve_problem(
                    input_path=file_name_path, mode="pdf"
                )
                self.submit_problem(
                    submission_file=f"/Users/NghiaKhang/Coding/Projects/codemath-solver/{output_path}"
                )
        except Exception as e:
            print(f"❌ Error: {e}")
        finally:
            self.driver.quit()
            clear_data("data")
        print("🎯 DONE!")
        return True


if __name__ == "__main__":
    problems_code = ["chiabi"]
    agent = CodeMathAgent()
    agent.process_problems(problems_code)

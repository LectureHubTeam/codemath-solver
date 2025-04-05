import time

import pyautogui
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager

from codemath_solver.agent.llm import solve_problem
from codemath_solver.utils.process_file import clear_data
from codemath_solver.utils.process_pdf import process_ocr


def __init_driver():
    global driver
    options = webdriver.ChromeOptions()

    # options.add_argument("--headless")  # Run in headless mode
    options.add_argument("--start-maximized")  # Maximize Chrome window
    # Run command: /Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome --remote-debugging-port=9222 --user-data-dir="/tmp/ChromeProfile"
    options.debugger_address = "localhost:9222"

    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()), options=options
    )


def __click_button(path: str, type: str = "id", wait_time: int = 10):
    if type == "id":
        by_type = By.ID
    elif type == "xpath":
        by_type = By.XPATH

    try:
        pdf_button = WebDriverWait(driver, wait_time).until(
            EC.element_to_be_clickable((by_type, path))
        )
        pdf_button.click()
    except Exception as e:
        print(f"❌ Button not found: {e}")


def download_problem(file_name: str):
    __click_button(path="pdf_button", type="id")

    time.sleep(3)
    print("📂 Pressing Enter to save PDF...")
    pyautogui.press("enter")

    time.sleep(3)

    pyautogui.write(file_name, interval=0.25)
    time.sleep(2)
    pyautogui.press("enter")
    time.sleep(2)


def submit_problem(submission_file: str):
    __click_button(path='//*[@id="content-right"]/div/a', type="xpath")
    time.sleep(3)
    file_input = driver.find_element(By.ID, "file_select")
    file_input.send_keys(submission_file)
    __click_button(path='//*[@id="problem_submit"]/div[2]/input[2]', type="xpath")
    time.sleep(3)


def start_process(problems_code: list):
    __init_driver()

    URLS = [f"https://laptrinh.codemath.vn/problem/{code}" for code in problems_code]
    try:
        for index, url in enumerate(URLS):
            file_name = url.split("/")[-1] + ".pdf"
            print(f"🔹 Accessing: {url}")
            driver.get(url)
            time.sleep(2)
            download_problem(file_name=file_name)
            file_name = f"data/{file_name}"
            file_processed = process_ocr(file_name=file_name)
            output_path = solve_problem(input_path=file_processed)
            submit_problem(
                submission_file=f"/Users/NghiaKhang/Coding/Projects/codemath-solver/{output_path}"
            )
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        driver.quit()
        clear_data("data")
    print("🎯 DONE!")
    return True


if __name__ == "__main__":
    problems_code = ["dss3"]
    start_process(problems_code=problems_code)

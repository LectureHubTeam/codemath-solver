import json
import os
import platform
import random
import sys
import time
from pathlib import Path
from typing import Dict, List

import pyautogui
import pyperclip
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager

# Add the parent directory to the path to import codemath_solver
sys.path.append(str(Path(__file__).parent.parent))


def load_problems_from_info() -> List[str]:
    """Load all unique problem codes from info.json"""
    info_path = Path(__file__).parent.parent / "submissions_codemath" / "info.json"

    if not info_path.exists():
        raise FileNotFoundError(f"info.json not found at {info_path}")

    with open(info_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Extract unique problem codes
    problem_codes = set()
    for submission_id, submission_data in data.items():
        if "problem" in submission_data:
            problem_codes.add(submission_data["problem"])

    return sorted(list(problem_codes))


class BrowserDownloader:
    """Browser-based downloader that simulates user actions with a fixed profile"""

    def __init__(self):
        self.driver = None
        self.setup_driver()

    def setup_driver(self):
        """Setup Chrome driver with fixed profile and download options"""
        options = webdriver.ChromeOptions()
        # Specify a fixed user profile directory
        profile_dir = str(Path(__file__).parent.parent / "chrome_profile")
        options.add_argument(f"--user-data-dir={profile_dir}")
        options.add_argument("--profile-directory=Default")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option("useAutomationExtension", False)

        # Set download directory and PDF handling
        download_dir = str(Path(__file__).parent.parent / "data")
        prefs = {
            "download.default_directory": download_dir,
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "safebrowsing.enabled": True,
            "plugins.always_open_pdf_externally": True,  # Force download PDFs instead of opening
        }
        options.add_experimental_option("prefs", prefs)

        try:
            self.driver = webdriver.Chrome(
                service=Service(ChromeDriverManager().install()), options=options
            )
            # Remove webdriver property
            self.driver.execute_script(
                "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
            )
            print("✅ Browser driver created successfully with fixed profile")
        except Exception as e:
            print(f"❌ Error creating browser driver: {str(e)}")
            raise

    def click_button(self, path: str, by_type: str = "id", wait_time: int = 10):
        """Click a button on the page"""
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
            raise

    def type_via_clipboard(self, text: str):
        """Type text using clipboard to avoid keyboard layout issues"""
        pyperclip.copy(text)
        time.sleep(0.2)
        print(pyperclip.paste())

        system = platform.system()
        if system == "Darwin":  # macOS
            pyautogui.hotkey("command", "v", interval=0.1)
        elif system == "Windows":
            pyautogui.hotkey("ctrl", "v", interval=0.1)
        else:  # Linux
            pyautogui.hotkey("ctrl", "v", interval=0.1)
        time.sleep(0.5)

    def download_problem(self, problem_code: str):
        """Download a problem PDF"""
        try:
            # Navigate to the problem page
            url = f"https://laptrinh.codemath.vn/problem/{problem_code}"
            print(f"🔗 Navigating to: {url}")
            self.driver.get(url)
            time.sleep(3)

            # Click the PDF download button
            print(f"📂 Clicking PDF download button for {problem_code}")
            self.click_button(path="pdf_button", by_type="id")
            time.sleep(3)

            # Simulate pressing Enter to save PDF
            print("📂 Pressing Enter to save PDF...")
            pyautogui.press("enter")
            time.sleep(3)

            # Type the filename
            file_name = f"{problem_code}.pdf"
            # pyautogui.write(file_name, interval=0.25)
            self.type_via_clipboard(file_name)
            time.sleep(2)

            # Press Enter to confirm
            pyautogui.press("enter")
            time.sleep(2)

            print(f"✅ Successfully downloaded {problem_code}")
            return True

        except Exception as e:
            print(f"❌ Error downloading {problem_code}: {str(e)}")
            return False

    def close(self):
        """Close the browser"""
        if self.driver:
            try:
                self.driver.quit()
                print("🔒 Browser closed")
            except Exception:
                pass


def download_problems_batch(
    problem_codes: List[str], batch_size: int = 10
) -> Dict[str, bool]:
    """
    Download problems in batches using browser simulation

    Args:
        problem_codes: List of problem codes to download
        batch_size: Number of problems to process before restarting browser

    Returns:
        Dictionary mapping problem codes to success status
    """
    print(
        f"🔄 Starting browser-based download of {len(problem_codes)} problems in batches of {batch_size}"
    )

    results = {}
    total_batches = (len(problem_codes) + batch_size - 1) // batch_size

    for batch_num in range(total_batches):
        start_idx = batch_num * batch_size
        end_idx = min(start_idx + batch_size, len(problem_codes))
        batch_problems = problem_codes[start_idx:end_idx]

        print(
            f"\n📦 Processing batch {batch_num + 1}/{total_batches} ({len(batch_problems)} problems)"
        )
        print("Problems: " + ", ".join(batch_problems))

        # Create a new browser instance for each batch
        browser = None
        try:
            browser = BrowserDownloader()

            for i, problem_code in enumerate(batch_problems, 1):
                try:
                    print(f"📥 [{i}/{len(batch_problems)}] Downloading {problem_code}")

                    # Download the problem
                    success = browser.download_problem(problem_code)
                    results[problem_code] = success

                    # Small delay between downloads
                    time.sleep(2)

                except Exception as e:
                    print(f"❌ Error downloading {problem_code}: {str(e)}")
                    results[problem_code] = False

        except Exception as e:
            print(f"❌ Error initializing browser for batch {batch_num + 1}: {str(e)}")
            # Mark all problems in this batch as failed
            for problem_code in batch_problems:
                results[problem_code] = False

        finally:
            if browser:
                browser.close()

            # Wait between batches
            if batch_num < total_batches - 1:
                print("⏳ Waiting 5 seconds before next batch...")
                time.sleep(5)

    return results


def main():
    """Main function to orchestrate the download process"""
    print("🎯 CodeMath Problem Downloader (Browser Simulation with Fixed Profile)")
    print("=" * 60)

    # Create profile and data directories
    profile_dir = Path(__file__).parent.parent / "chrome_profile"
    data_dir = Path(__file__).parent.parent / "data"
    profile_dir.mkdir(exist_ok=True)
    data_dir.mkdir(exist_ok=True)

    # Load problem codes from info.json
    try:
        problem_codes = load_problems_from_info()
        print(f"📋 Found {len(problem_codes)} unique problems in info.json")
        problem_codes_downloaded = [
            file.split(".")[0]
            for file in os.listdir(Path(__file__).parent.parent / "data")
        ]
        problem_codes = [
            code for code in problem_codes if code not in problem_codes_downloaded
        ]
        random.shuffle(problem_codes)
        print(f"📋 Found {len(problem_codes)} unique problems to download")
    except Exception as e:
        print(f"❌ Error loading problems: {str(e)}")
        return

    # Ask user for batch size
    print("\n📊 Download Configuration:")
    print(
        "This script uses browser simulation with a fixed Chrome profile to download problems."
    )
    print("Each batch will restart the browser to ensure stability.")

    batch_size = 10
    while True:
        try:
            user_input = input(f"Batch size (1-20, default {batch_size}): ").strip()
            if not user_input:
                break
            batch_size = int(user_input)
            if 1 <= batch_size <= 20:
                break
            print("Please enter a number between 1 and 20")
        except ValueError:
            print("Please enter a valid number")

    print("\n🚀 Starting download process...")
    start_time = time.time()

    # Download problems
    results = download_problems_batch(problem_codes, batch_size)

    # Calculate statistics
    end_time = time.time()
    duration = end_time - start_time

    successful = sum(1 for success in results.values() if success)
    failed = len(results) - successful

    print("\n" + "=" * 50)
    print("📊 Download Summary")
    print("=" * 50)
    print(f"Total problems: {len(problem_codes)}")
    print(f"Successfully downloaded: {successful}")
    print(f"Failed: {failed}")
    print(f"Success rate: {(successful / len(problem_codes) * 100):.1f}%")
    print(f"Total time: {duration:.2f} seconds")
    print(f"Average time per problem: {duration / len(problem_codes):.2f} seconds")

    # Show failed downloads
    if failed > 0:
        print("\n❌ Failed downloads:")
        for problem_code, success in results.items():
            if not success:
                print(f"  - {problem_code}")

    print(f"\n📁 Downloaded files are saved in: {data_dir.absolute()}")


if __name__ == "__main__":
    main()

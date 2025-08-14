"""
Base class for web automation agents.
Contains common functionality for both codemath and lqdoj agents.
"""

import os
import random
import shutil
import time
from abc import ABC, abstractmethod

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager

from base_solver.base_llm import BaseGeminiSolver
from base_solver.shared_utils import (
    check_file_exists,
    delete_abnormal_files,
    find_project_root,
    press_enter,
    type_via_clipboard,
)
from database.enums import SolvedStatus
from database.manager import DatabaseManager


class BaseAgent(ABC):
    """
    Abstract base class for web automation agents.
    Provides common functionality for browser automation and file operations.
    """

    def __init__(
        self,
        url_base: str = None,
        prefix: str = None,
        solved_status_icon: str = None,
        unsolved_status_icon: str = None,
        select_file_submit: str = None,
        button_submit: str = None,
        problem_title_class: str = "problem-title",
        profile_dir: str = None,
        window_layout: tuple = None,
    ):
        """Initialize the base agent with solver and driver setup."""
        self.project_root = find_project_root()
        self.solver = self.create_solver()
        self.driver = None
        self.profile_dir = profile_dir
        self.window_layout = window_layout
        self.setup_driver()
        self.problem_code = None
        self.url_base = url_base
        self.prefix = prefix

        # For checking solved status
        self.solved_status_icon = solved_status_icon
        self.unsolved_status_icon = unsolved_status_icon
        self.problem_title_class = problem_title_class

        # For submitting problem
        self.select_file_submit = select_file_submit
        self.button_submit = button_submit

        self.chrome_profile = None

        # Initialize database manager
        self.db_manager = DatabaseManager()

        # Determine platform ID based on prefix
        self.platform_id = self._get_platform_id()

    def _get_platform_id(self) -> int:
        """Get platform ID based on prefix"""
        if self.prefix == "codemath":
            return 1  # CodeMath platform ID
        elif self.prefix == "lqdoj":
            return 2  # LQDOJ platform ID
        else:
            raise ValueError(f"Unknown platform prefix: {self.prefix}")

    @abstractmethod
    def create_solver(self) -> BaseGeminiSolver:
        """
        Create the appropriate solver instance.
        Must be implemented by subclasses.

        Returns:
            Solver instance
        """
        pass

    def setup_driver(self):
        """Setup Chrome driver with fixed profile and download options"""
        options = webdriver.ChromeOptions()

        # Specify a fixed user profile directory
        # Use custom profile directory if provided, otherwise create temporary one
        if self.profile_dir:
            profile_dir = self.profile_dir
        else:
            # Get the base chrome profile from root directory
            profile_dir_base = os.path.join(self.project_root, "chrome_profile")

            # Check if base profile exists
            if not os.path.exists(profile_dir_base):
                print(f"⚠️ Base chrome profile not found at: {profile_dir_base}")
                print("🔧 Creating new chrome profile...")
                profile_dir = os.path.join(
                    self.project_root,
                    "chrome_profile_temp",
                    f"chrome_profile_{random.randint(100000, 999999)}",
                )
                os.makedirs(profile_dir, exist_ok=True)
            else:
                # Create temporary profile by duplicating base profile
                profile_dir = os.path.join(
                    self.project_root,
                    "chrome_profile_temp",
                    f"chrome_profile_{random.randint(100000, 999999)}",
                )
                print(f"📋 Duplicating base profile from: {profile_dir_base}")
                print(f"📋 To temporary profile: {profile_dir}")
                shutil.copytree(profile_dir_base, profile_dir)

        self.chrome_profile = profile_dir

        print(f"🔹 Profile directory: {profile_dir}")
        options.add_argument(f"--user-data-dir={profile_dir}")
        options.add_argument("--profile-directory=Default")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option("useAutomationExtension", False)

        # Set window size and position based on layout
        x, y, width, height = (
            self.window_layout if self.window_layout else (100, 100, 800, 600)
        )

        options.add_argument(f"--window-size={width},{height}")
        options.add_argument(f"--window-position={x},{y}")

        # Disable extensions, infobars, sandbox, and dev shm usage
        options.add_argument("--disable-extensions")
        options.add_argument("--disable-infobars")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")

        # Set download directory and PDF handling
        download_dir = str(self.project_root / "data")
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
        """
        Click a button on the webpage.

        Args:
            path: Element identifier (ID, XPath, etc.)
            by_type: Type of selector ("id", "xpath", etc.)
            wait_time: Maximum wait time in seconds
        """
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

    def download_problem(
        self,
        file_name: str,
        element_path="pdf_button",
        element_type="id",
        wait_time: int = 3,
        max_retries: int = 5,
    ):
        """
        Download problem PDF from the website with improved error handling.

        Args:
            file_name: Name for the downloaded file
            element_path: Path to the download button
            element_type: Type of element selector
            wait_time: Base wait time in seconds
            max_retries: Maximum number of retry attempts
        """
        # Ensure file has .pdf extension
        if not file_name.endswith(".pdf"):
            file_name = f"{file_name}.pdf"

        # Ensure data directory exists
        data_dir = os.path.join(self.project_root, "data")
        os.makedirs(data_dir, exist_ok=True)

        file_downloaded = os.path.join(data_dir, file_name)

        # Check if file already exists
        if check_file_exists(file_downloaded):
            print(f"✅ File already downloaded: {file_downloaded}")
            return file_downloaded

        print(f"🔄 Starting download for: {file_name}")

        # Step 1: Click download button
        try:
            self.click_button(path=element_path, by_type=element_type)
            print(f"✅ Clicked download button: {element_path}")
        except Exception as e:
            print(f"❌ Failed to click download button: {e}")
            raise Exception(f"Download button not found: {element_path}")

        time.sleep(wait_time * 2)
        press_enter(wait_time=wait_time * 2.5)
        type_via_clipboard(file_name)
        press_enter(wait_time=wait_time)

        # Step 2: Wait for download dialog and handle it
        attempts = 0
        download_success = True if check_file_exists(file_downloaded) else False

        while attempts < max_retries and not download_success:
            attempts += 1
            print(f" Download attempt {attempts}/{max_retries}")

            # Clear pdf file downloaded without renaming
            delete_abnormal_files()

            try:
                # Type filename
                type_via_clipboard(file_name, wait_time=wait_time / 2)
                print(f"📝 Typed filename: {file_name}")

                # Press Enter to save
                press_enter(wait_time=wait_time * 2)
                print("💾 Pressed Enter to save file")

                # Check if file was downloaded
                if check_file_exists(file_downloaded):
                    download_success = True
                    print(f"✅ Download successful: {file_downloaded}")
                    break
                else:
                    print(f"⚠️ File not found after attempt {attempts}, retrying...")
                    time.sleep(wait_time)

            except Exception as e:
                print(f"❌ Error during download attempt {attempts}: {e}")
                if attempts < max_retries:
                    time.sleep(wait_time)
                    continue
                else:
                    break

        # Final check
        if not check_file_exists(file_downloaded):
            error_msg = (
                f"❌ Failed to download file {file_name} after {max_retries} attempts"
            )
            print(f" Expected location: {file_downloaded}")
            raise Exception(error_msg)

        # Verify file size
        file_size = os.path.getsize(file_downloaded)
        if file_size == 0:
            print(f"⚠️ Warning: Downloaded file is empty: {file_downloaded}")

        print(f"✅ File downloaded successfully: {file_downloaded} ({file_size} bytes)")
        return file_downloaded

    def submit_problem(self, submission_file: str):
        """
        Submit solution file to the website.

        Args:
            submission_file: Path to the solution file
        """
        try:
            print(f"📤 Submitting solution: {submission_file}")

            # Navigate to submission page
            submission_url = self.get_submission_url()
            print(f"🌐 Navigating to: {submission_url}")
            self.driver.get(submission_url)
            time.sleep(2)

            # Check if file exists
            full_path = os.path.join(self.project_root, submission_file)
            if not os.path.exists(full_path):
                print(f"❌ Solution file not found: {full_path}")
                return False

            print(f"✅ Solution file found: {full_path}")

            # Find and fill file input
            try:
                file_input = self.driver.find_element(By.ID, self.select_file_submit)
                file_input.send_keys(full_path)
            except Exception as e:
                print(f"❌ Error finding file input: {e}")
                return False

            # Click submit button
            try:
                self.click_button(path=self.button_submit, by_type="xpath")
            except Exception as e:
                print(f"❌ Error clicking submit button: {e}")
                return False

            # Wait for submission to complete
            time.sleep(3)
            print("✅ Solution submitted successfully")
            return True

        except Exception as e:
            print(f"❌ Error submitting solution: {e}")
            return False

    def get_problem_url(self) -> str:
        """
        Get the URL for a specific problem.

        Args:
            problem_code: The problem code

        Returns:
            URL for the problem
        """
        return f"{self.url_base}/problem/{self.problem_code}"

    def get_submission_url(self) -> str:
        """
        Get the URL for the submission page.

        Returns:
            URL for the submission page
        """
        return f"{self.url_base}/problem/{self.problem_code}/submit"

    def check_solved_status(self) -> SolvedStatus:
        """
        Check the solved status of the problem based on CSS classes in the problem-title element.

        Returns:
            SolvedStatus: SOLVED if problem is solved, UNSOLVED if attempted but not solved, NOT_SOLVED if not attempted
        """
        try:
            # Navigate to the problem page if not already there
            if not self.driver.current_url.endswith(self.problem_code):
                self.driver.get(self.get_problem_url())
                time.sleep(2)

            # Look for the problem-title element
            problem_title = self.driver.find_element(
                By.CLASS_NAME, self.problem_title_class
            )

            # Check for solved status icon (check-circle)
            try:
                problem_title.find_element(By.CSS_SELECTOR, self.solved_status_icon)
                return SolvedStatus.SOLVED
            except Exception:
                pass

            # Check for attempted but not solved status icon (minus-circle)
            try:
                problem_title.find_element(By.CSS_SELECTOR, self.unsolved_status_icon)
                return SolvedStatus.UNSOLVED
            except Exception:
                pass

            # If neither icon is found, the problem hasn't been attempted
            return SolvedStatus.NOT_SOLVED

        except Exception as e:
            print(f"❌ Error checking solved status: {str(e)}")
            return SolvedStatus.NOT_SOLVED

    def update_problem_status(self, problem_code: str, status: SolvedStatus):
        """Update the problem status in the database"""
        self.db_manager.update_problem_status(
            problem_code=problem_code,
            platform_id=self.platform_id,
            status=status,
        )

    def process_problems(self, problems_code: list):
        """Process a list of problem codes"""
        processed_count = 0
        success_count = 0
        error_count = 0

        for problem_code in problems_code:
            self.problem_code = problem_code

            # Check initial solved status
            initial_status = self.check_solved_status()
            if initial_status == SolvedStatus.SOLVED:
                print(f"✅ Problem `{problem_code}` already solved")
                # Update database with solved status
                self.update_problem_status(problem_code, SolvedStatus.SOLVED)
                processed_count += 1
                success_count += 1
                continue

            print(f"\n🔄 Processing problem: {problem_code}")
            try:
                # Navigate to problem page
                problem_url = self.get_problem_url()
                self.driver.get(problem_url)
                time.sleep(3)

                # Download problem PDF
                file_name = f"{self.prefix}_{problem_code}.pdf"
                pdf_path = self.download_problem(file_name)

                # Solve problem
                solution_path = self.solver.solve_problem(pdf_path, mode="pdf")

                if solution_path:
                    print(f"✅ Solution generated: {solution_path}")

                    # Submit solution
                    submission_success = self.submit_problem(solution_path)
                    if submission_success:
                        print(f"✅ Problem {problem_code} submitted successfully")

                        # Wait a bit for the submission to be processed
                        time.sleep(5)

                        # Check if the problem is now solved
                        final_status = self.check_solved_status()
                        if final_status == SolvedStatus.SOLVED:
                            print(f"🎉 Problem {problem_code} is now SOLVED!")
                            # Update database with solved status
                            self.update_problem_status(
                                problem_code, SolvedStatus.SOLVED
                            )
                        elif final_status == SolvedStatus.UNSOLVED:
                            print(
                                f"⚠️ Problem {problem_code} was attempted but not solved"
                            )
                            # Update database with unsolved status
                            self.update_problem_status(
                                problem_code, SolvedStatus.UNSOLVED
                            )
                        else:
                            print(f"ℹ️ Problem {problem_code} status unchanged")

                        processed_count += 1
                        success_count += 1
                    else:
                        print(f"❌ Failed to submit solution for {problem_code}")
                        processed_count += 1
                        error_count += 1
                else:
                    print(f"❌ Failed to generate solution for {problem_code}")
                    self.update_problem_status(problem_code, SolvedStatus.ERROR)
                    processed_count += 1
                    error_count += 1

            except Exception as e:
                print(f"❌ Error processing problem {problem_code}: {e}")
                self.update_problem_status(problem_code, SolvedStatus.ERROR)
                processed_count += 1
                error_count += 1
                continue
            except KeyboardInterrupt:
                print("❌ Keyboard interrupt detected. Exiting...")
                self.cleanup()
                break

        # Print summary
        print("\n📊 Processing Summary:")
        print(f"   Total problems: {len(problems_code)}")
        print(f"   Processed: {processed_count}")
        print(f"   Successful: {success_count}")
        print(f"   Errors: {error_count}")

        # Cleanup
        self.cleanup()

        # Return True if at least one problem was processed successfully
        return processed_count > 0

    def check_and_update_problems_status(self, problems_code: list):
        """Check and update the status of multiple problems in the database"""
        print(f"\n🔍 Checking status for {len(problems_code)} problems...")

        for problem_code in problems_code:
            self.problem_code = problem_code
            try:
                # Check current solved status
                status = self.check_solved_status()

                # Update database with current status
                self.update_problem_status(problem_code, status)

                if status == SolvedStatus.SOLVED:
                    print(f"✅ Problem `{problem_code}` is SOLVED")
                elif status == SolvedStatus.UNSOLVED:
                    print(f"⚠️ Problem `{problem_code}` was attempted but not solved")
                else:
                    print(f"❓ Problem `{problem_code}` not attempted yet")

            except Exception as e:
                print(f"❌ Error checking status for problem {problem_code}: {e}")
                continue

        print("✅ Status check completed!")

    def cleanup(self):
        """Clean up resources and data"""
        if self.driver:
            self.driver.quit()

        # Only cleanup temporary profiles (not the base profile)
        if self.chrome_profile and "chrome_profile_temp" in self.chrome_profile:
            try:
                shutil.rmtree(self.chrome_profile)
                print(f"🧹 Cleaned up temporary profile: {self.chrome_profile}")
            except Exception as e:
                print(f"⚠️ Failed to clean up profile {self.chrome_profile}: {e}")

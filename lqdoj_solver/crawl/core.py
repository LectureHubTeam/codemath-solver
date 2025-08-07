import time

import pandas as pd
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager

from conf import lqdoj_settings

load_dotenv()


class LQDOJCrawler:
    def __init__(self):
        self.problem_page_url = lqdoj_settings.LQDOJ_CRAWLER.get("problem_page_url")
        self.start_page = lqdoj_settings.LQDOJ_CRAWLER.get("config").get("start_page")
        self.end_page = lqdoj_settings.LQDOJ_CRAWLER.get("config").get("end_page")
        self.delay = lqdoj_settings.LQDOJ_CRAWLER.get("config").get("delay")
        self.csv_file = lqdoj_settings.LQDOJ_CSV_FILE
        self.driver = None

    def setup_driver(self):
        """Setup Chrome driver with fixed profile and download options"""
        options = webdriver.ChromeOptions()

        # Specify a fixed user profile directory
        profile_dir = "/Users/NghiaKhang/Coding/Projects/codemath-solver/chrome_profile"
        print(f"🔹 Profile directory: {profile_dir}")
        options.add_argument(f"--user-data-dir={profile_dir}")
        options.add_argument("--profile-directory=Default")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option("useAutomationExtension", False)

        # Disable extensions, infobars, sandbox, and dev shm usage
        options.add_argument("--disable-extensions")
        options.add_argument("--disable-infobars")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")

        # Set download directory and PDF handling
        download_dir = "/Users/NghiaKhang/Coding/Projects/codemath-solver/data"
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
            return True
        except Exception as e:
            print(f"❌ Error creating browser driver: {str(e)}")
            return False

    def fetch_page(self, url):
        try:
            print(f"📡 Fetching content from: {url}")
            self.driver.get(url)

            # Wait for Cloudflare challenge to complete
            time.sleep(5)

            # Check if still on Cloudflare page
            if "Just a moment" in self.driver.page_source:
                print("❌ Still on Cloudflare challenge page, waiting longer...")
                time.sleep(10)

            print(f"✅ Successfully loaded page: {self.driver.title}")
            return self.driver.page_source
        except Exception as e:
            print(f"❌ Error while fetching URL {url}: {e}")
            return None

    def parse_problem_table(self, html_content):
        # Use Selenium to find the table instead of BeautifulSoup
        try:
            # Wait for table to be present
            wait = WebDriverWait(self.driver, 10)
            problem_table = wait.until(
                EC.presence_of_element_located((By.TAG_NAME, "table"))
            )

            # Find all rows in the table
            rows = problem_table.find_elements(By.TAG_NAME, "tr")
            print(f"✅ Found {len(rows)} rows in the table.")
            return rows
        except Exception as e:
            print(f"❌ Error parsing problem table: {e}")
            return []

    def extract_problem_data(self, row):
        try:
            # Get all cells in the row
            cells = row.find_elements(By.TAG_NAME, "td")
            if len(cells) < 7:  # Based on the HTML structure provided
                return None

            # Extract solved status
            solved_cell = cells[0]
            solved_attr = solved_cell.get_attribute("solved")
            # solved_stt = (
            #     "Solved"
            #     if solved_attr == "1"
            #     else "Unsolved"
            #     if solved_attr == "-1"
            #     else "N/A"
            # )

            # Extract problem name and code
            problem_cell = cells[1]
            problem_link = problem_cell.find_element(By.TAG_NAME, "a")
            problem_name = problem_link.text.strip()

            pcode_cell = cells[2]
            pcode_link = pcode_cell.find_element(By.TAG_NAME, "a")
            problem_code = pcode_link.text.strip()

            # Extract category (difficulty)
            category = cells[3].text.strip()

            # Extract points
            points = cells[4].text.strip()

            # Extract AC rate
            ac_rate = cells[5].text.strip()

            # Extract users count
            users_cell = cells[6]
            users_link = users_cell.find_element(By.TAG_NAME, "a")
            users_accepted = users_link.text.strip()

            return {
                "solved": solved_attr,
                "problem-code": problem_code.lower(),
                "problem-name": problem_name,
                "category": category,
                "points": points,
                "ac-rate": ac_rate,
                "users": users_accepted,
            }
        except Exception as e:
            print(f"⚠️ Error processing a problem: {e}")
            return None

    def crawl_problem_list(self, url):
        html_content = self.fetch_page(url)
        if not html_content:
            return []
        rows = self.parse_problem_table(html_content)
        problems_data = []
        for row in rows:
            problem_data = self.extract_problem_data(row)
            if problem_data:
                problems_data.append(problem_data)
        return problems_data

    def crawl_all_pages(self):
        all_problems = []
        for page in range(self.start_page, self.end_page + 1):
            url = self.problem_page_url.format(page=page)
            page_data = self.crawl_problem_list(url)
            all_problems.extend(page_data)
            time.sleep(self.delay)
        return all_problems

    def save_problems_to_csv(self, problems_data):
        if problems_data:
            df = pd.DataFrame(problems_data)
            df.to_csv(self.csv_file, index=False, encoding="utf-8")
            print(
                f"\n🎉 Extraction complete! A total of {len(problems_data)} problems have been saved to '{self.csv_file}'"
            )
        else:
            print("❌ No data to save!")

    def check_login_status(self):
        """
        Check if the user is logged in by visiting the user page
        """
        try:
            url = "https://lqdoj.edu.vn/user"
            self.driver.get(url)
            time.sleep(3)

            # Check if we're redirected to login page or if we can see user info
            if (
                "login" in self.driver.current_url.lower()
                or "Login" in self.driver.page_source
            ):
                print("❌ Not logged in. Please log in to LQDOJ first.")
                return False
            else:
                print("✅ Successfully logged in to LQDOJ")
                return True
        except Exception as e:
            print(f"❌ Error checking login status: {e}")
            return False

    def run(self):
        if not self.setup_driver():
            return

        try:
            if not self.check_login_status():
                return

            all_problems = self.crawl_all_pages()
            self.save_problems_to_csv(all_problems)
        finally:
            if self.driver:
                self.driver.quit()
                print("🔒 Browser driver closed")


if __name__ == "__main__":
    crawler = LQDOJCrawler()
    crawler.run()

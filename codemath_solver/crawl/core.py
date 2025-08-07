import time

import pandas as pd
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv

from conf import codemath_settings

load_dotenv()


class CodeMathCrawler:
    def __init__(self):
        self.cookies = codemath_settings.CODEMATH_CRAWLER.get("cookies")
        self.problem_page_url = codemath_settings.CODEMATH_CRAWLER.get(
            "problem_page_url"
        )
        self.start_page = codemath_settings.CODEMATH_CRAWLER.get("config").get(
            "start_page"
        )
        self.end_page = codemath_settings.CODEMATH_CRAWLER.get("config").get("end_page")
        self.delay = codemath_settings.CODEMATH_CRAWLER.get("config").get("delay")
        self.csv_file = codemath_settings.CODEMATH_CSV_FILE

    def fetch_page(self, url):
        try:
            print(f"📡 Fetching content from: {url}")
            response = requests.get(url, timeout=10, cookies=self.cookies)
            response.raise_for_status()
            response.encoding = "utf-8"
            return response.text
        except requests.exceptions.RequestException as e:
            print(f"❌ Error while fetching URL {url}: {e}")
            return None

    def parse_problem_table(self, html_content):
        soup = BeautifulSoup(html_content, "html.parser")
        problem_table = soup.find("table", id="problem-table")
        if not problem_table:
            print("❌ Problem table with id='problem-table' not found.")
            return []
        tbody = problem_table.find("tbody")
        if not tbody:
            print("❌ tbody not found in the table.")
            return []
        rows = tbody.find_all("tr")
        print(f"✅ Found {len(rows)} problems on the page.")
        return rows

    def extract_problem_data(self, row):
        try:
            solved_stt = row.find("td", class_="solved").get("solved", "N/A")
            problem_code = (
                row.find("td", class_="problem-code").text.strip()
                if row.find("td", class_="problem-code")
                else "N/A"
            )
            problem_name = row.find("td", class_="problem-name") or row.find(
                "td", class_="probles-name"
            )
            problem_name = problem_name.text.strip() if problem_name else "N/A"
            category = (
                row.find("td", class_="category").text.strip()
                if row.find("td", class_="category")
                else "N/A"
            )
            points = (
                row.find("td", class_="p").text.strip()
                if row.find("td", class_="p")
                else "N/A"
            )
            ac_rate = (
                row.find("td", class_="ac-rate").text.strip()
                if row.find("td", class_="ac-rate")
                else "N/A"
            )
            users_accepted = (
                row.find("td", class_="users").text.strip()
                if row.find("td", class_="users")
                else "N/A"
            )
            return {
                "solved": solved_stt,
                "problem-code": problem_code,
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

    def check_cookies_valid(self):
        """
        Check if the provided cookies are valid by fetching the first page and looking for the problem table.
        Returns True if valid, False otherwise.
        """
        url = "https://laptrinh.codemath.vn/user"
        response = requests.get(url, timeout=10, cookies=self.cookies)
        if "Email" not in response.text:
            print(
                """
                  ❌ Aborting: Please check your cookies in the .env file.
                  Follow the instructions below to get the cookies:
                    1. Open your browser and go to https://laptrinh.codemath.vn.
                    2. Log in to your account.
                    3. Open the developer tools (F12) and go to the "Application" tab.
                    4. Find the cookies for the domain "laptrinh.codemath.vn".
                    5. Copy the values and paste them into the .env file as follows:
                       - tk_ai --> CODEMATH_TK_AI
                       - sessionid --> CODEMATH_SESSION_ID
                       - csrftoken --> CODEMATH_CSRF_TOKEN
            """
            )
            return False
        return True

    def run(self):
        if not self.check_cookies_valid():
            return
        all_problems = self.crawl_all_pages()
        self.save_problems_to_csv(all_problems)


if __name__ == "__main__":
    crawler = CodeMathCrawler()
    crawler.run()

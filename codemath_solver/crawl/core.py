import time

import pandas as pd
import requests
from bs4 import BeautifulSoup

from conf import settings


def fetch_page(url):
    """
    Send a GET request to the URL and return the HTML content if successful.
    """
    try:
        print(f"📡 Fetching content from: {url}")
        response = requests.get(
            url, timeout=10, cookies=settings.CRAWLER.get("cookies")
        )
        response.raise_for_status()
        response.encoding = "utf-8"
        return response.text
    except requests.exceptions.RequestException as e:
        print(f"❌ Error while fetching URL {url}: {e}")
        return None


def parse_problem_table(html_content):
    """
    Parse the HTML content to extract problem data from the table.
    """
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


def extract_problem_data(row):
    """
    Extract information from a problem row and return it as a dict.
    """
    cells = row.find_all("td")
    if len(cells) < 7:
        return None

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


def crawl_problem_list(url):
    """
    Extract the problem list from a page.
    """
    html_content = fetch_page(url)
    if not html_content:
        return []

    rows = parse_problem_table(html_content)
    problems_data = []
    for row in rows:
        problem_data = extract_problem_data(row)
        if problem_data:
            problems_data.append(problem_data)

    return problems_data


def crawl_all_pages():
    start_page = settings.CRAWLER.get("config").get("start_page")
    end_page = settings.CRAWLER.get("config").get("end_page")
    delay = settings.CRAWLER.get("config").get("delay")

    all_problems = []
    for page in range(start_page, end_page):
        url = settings.CRAWLER.get("problem_page_url").format(page=page)
        page_data = crawl_problem_list(url)
        all_problems.extend(page_data)
        time.sleep(delay)
    return all_problems


def save_problems_to_csv(problems_data):
    """
    Save the list of problems to a CSV file.
    """
    filename = settings.CSV_FILE
    if problems_data:
        df = pd.DataFrame(problems_data)
        df.to_csv(filename, index=False, encoding="utf-8")
        print(
            f"\n🎉 Extraction complete! A total of {len(problems_data)} problems have been saved to '{filename}'"
        )
    else:
        print("❌ No data to save!")


# --- Crawl data from multiple pages ---
all_problems = crawl_all_pages()

# --- Save to CSV file ---
save_problems_to_csv(all_problems)

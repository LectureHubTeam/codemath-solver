import os

from dotenv import load_dotenv

load_dotenv()

CSV_FILE = "problems_data.csv"

STREAMLIT = {
    "title": "CodeMath Solver",
    "layout": "wide",
}

CRAWLER = {
    "cookies": {
        "csrftoken": os.getenv("CODEMATH_CSRF_TOKEN"),
        "sessionid": os.getenv("CODEMATH_SESSION_ID"),
        "tk_ai": os.getenv("CODEMATH_TK_AI"),
    },
    "problem_page_url": "https://laptrinh.codemath.vn/problems/?page={page}",
    "config": {
        "start_page": 1,
        "end_page": 13,
        "delay": 0.75,
    },
}

CODEMATH_WEBSITE = {
    "url": "https://laptrinh.codemath.vn",
}

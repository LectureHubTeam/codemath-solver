import os

from dotenv import load_dotenv

load_dotenv()

# Cấu hình chung cho multi-platform
PLATFORMS = {
    "codemath": {
        "name": "CodeMath",
        "module": "codemath_solver",
        "settings": "codemath_settings",
        "csv_file": "problems_data.csv",
    },
    "lqdoj": {
        "name": "LQDOJ",
        "module": "lqdoj_solver",
        "settings": "lqdoj_settings",
        "csv_file": "lqdoj_problems_data.csv",
    },
}

# Cấu hình mặc định
DEFAULT_PLATFORM = "lqdoj"

# Cấu hình chung cho Streamlit
STREAMLIT = {
    "layout": "wide",
}

import os

from dotenv import load_dotenv

load_dotenv()

LQDOJ_CSV_FILE = "lqdoj_problems_data.csv"

LQDOJ_STREAMLIT = {
    "title": "LQDOJ Solver",
    "layout": "wide",
}

LQDOJ_CRAWLER = {
    "cookies": {
        "csrftoken": os.getenv("LQDOJ_CSRF_TOKEN"),
        "sessionid": os.getenv("LQDOJ_SESSION_ID"),
        "tk_ai": os.getenv("LQDOJ_TK_AI"),
    },
    "problem_page_url": "https://lqdoj.edu.vn/problems/?page={page}",
    "config": {
        "start_page": 1,
        "end_page": 67,
        "delay": 1.0,
    },
}

LQDOJ_WEBSITE = {
    "url": "https://lqdoj.edu.vn",
}

LQDOJ_GEMINI_PROMPT_BASE = """
Viết code Python giải bài toán sau trên LQDOJ, hãy cân nhắc và suy nghĩ thật kỹ để đưa ra câu trả lời chính xác và tối ưu nhất.
Tên biến, tên hàm đặt ngắn gọn bằng tiếng anh nhưng comment giải thích bằng tiếng Việt.
Sử dụng hàm input() để nhận dữ liệu đầu vào.

Chỉ cung cấp mã Python hoàn chỉnh trong một khối mã duy nhất được đánh dấu bằng ```python ... ```.
Không thêm bất kỳ lời giải thích, lời chào hoặc văn bản bổ sung nào bên ngoài khối mã.

"""

LQDOJ_GEMINI_PROMPT_TEXT = (
    LQDOJ_GEMINI_PROMPT_BASE
    + """

Mô tả bài toán:
{problem_text}
"""
)

LQDOJ_GEMINI_PROMPT_PDF = (
    LQDOJ_GEMINI_PROMPT_BASE
    + """

Mô tả bài toán trong file PDF đính kèm.
"""
)

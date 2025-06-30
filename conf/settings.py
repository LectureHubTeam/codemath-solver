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

GEMINI_PROMPT_BASE = """
Viết code Python giải bài toán sau, hãy cân nhắc và suy nghĩ thật kỹ để đưa ra câu trả lời chính xác và tối ưu nhất. Tên biến, tên hàm đặt ngắn gọn bằng tiếng anh nhưng comment giải thích bằng tiếng Việt. Sử dụng hàm input() để nhận dữ liệu đầu vào.

Chỉ cung cấp mã Python hoàn chỉnh trong một khối mã duy nhất được đánh dấu bằng ```python ... ```.
Không thêm bất kỳ lời giải thích, lời chào hoặc văn bản bổ sung nào bên ngoài khối mã.

"""

GEMINI_PROMPT_TEXT = (
    GEMINI_PROMPT_BASE
    + """

Mô tả bài toán:
{problem_text}
"""
)

GEMINI_PROMPT_PDF = (
    GEMINI_PROMPT_BASE
    + """

Mô tả bài toán trong file PDF đính kèm.
"""
)

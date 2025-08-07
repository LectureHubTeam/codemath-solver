import os

from dotenv import load_dotenv

load_dotenv()

CODEMATH_CSV_FILE = "problems_data.csv"

CODEMATH_STREAMLIT = {
    "title": "CodeMath Solver",
    "layout": "wide",
}

CODEMATH_CRAWLER = {
    "cookies": {
        "csrftoken": os.getenv("CODEMATH_CSRF_TOKEN"),
        "sessionid": os.getenv("CODEMATH_SESSION_ID"),
        "tk_ai": os.getenv("CODEMATH_TK_AI"),
    },
    "problem_page_url": "https://laptrinh.codemath.vn/problems/?page={page}",
    "config": {
        "start_page": 1,
        "end_page": 14,
        "delay": 0.75,
    },
}

CODEMATH_WEBSITE = {
    "url": "https://laptrinh.codemath.vn",
}

CODEMATH_GEMINI_PROMPT_BASE = """
Viết code Python giải bài toán sau, hãy cân nhắc và suy nghĩ thật kỹ để đưa ra câu trả lời chính xác và tối ưu nhất.
Tên biến, tên hàm đặt ngắn gọn bằng tiếng anh nhưng comment giải thích bằng tiếng Việt.
Sử dụng hàm input() để nhận dữ liệu đầu vào.

Chỉ cung cấp mã Python hoàn chỉnh trong một khối mã duy nhất được đánh dấu bằng ```python ... ```.
Không thêm bất kỳ lời giải thích, lời chào hoặc văn bản bổ sung nào bên ngoài khối mã.

"""

CODEMATH_GEMINI_PROMPT_TEXT = (
    CODEMATH_GEMINI_PROMPT_BASE
    + """

Mô tả bài toán:
{problem_text}
"""
)

CODEMATH_GEMINI_PROMPT_PDF = (
    CODEMATH_GEMINI_PROMPT_BASE
    + """

Mô tả bài toán trong file PDF đính kèm.
"""
)

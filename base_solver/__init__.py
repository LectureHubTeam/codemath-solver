"""
Base solver module containing shared base classes and utilities
for both codemath_solver and lqdoj_solver modules.
"""

from .base_agent import BaseAgent
from .base_explainer import BaseCodeExplainer
from .base_llm import BaseGeminiSolver
from .shared_utils import (
    clear_data,
    extract_pdf_data,
    extract_python_code,
    format_data,
    process_ocr,
    read_text_from_file,
    save_code_to_file,
    save_data,
)

__all__ = [
    "BaseGeminiSolver",
    "BaseCodeExplainer",
    "BaseAgent",
    "clear_data",
    "extract_pdf_data",
    "save_data",
    "process_ocr",
    "format_data",
    "read_text_from_file",
    "save_code_to_file",
    "extract_python_code",
]

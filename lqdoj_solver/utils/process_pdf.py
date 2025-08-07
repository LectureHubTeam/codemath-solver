"""
LQDOJ PDF processing utilities.
Uses shared utilities from base_solver for common functionality.
"""

from base_solver.shared_utils import extract_pdf_data as shared_extract_pdf_data
from base_solver.shared_utils import format_data as shared_format_data
from base_solver.shared_utils import process_ocr as shared_process_ocr
from base_solver.shared_utils import save_data as shared_save_data


def format_data_lqdoj(text):
    """Format data specifically for LQDOJ platform"""
    return shared_format_data(text, platform_name="LQDOJ")


def extract_pdf_data_lqdoj(file_name: str):
    """Extract PDF data using shared utility"""
    return shared_extract_pdf_data(file_name)


def save_data_lqdoj(file_name: str, formatted_text: str):
    """Save data using shared utility"""
    return shared_save_data(file_name, formatted_text)


def process_ocr_lqdoj(file_name: str):
    """Process OCR specifically for LQDOJ platform"""
    return shared_process_ocr(file_name, platform_name="LQDOJ")


# For backward compatibility
def format_data(text):
    return format_data_lqdoj(text)


def extract_pdf_data(file_name: str):
    return extract_pdf_data_lqdoj(file_name)


def save_data(file_name: str, formatted_text: str):
    return save_data_lqdoj(file_name, formatted_text)


def process_ocr(file_name: str):
    return process_ocr_lqdoj(file_name)

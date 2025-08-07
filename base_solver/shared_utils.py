"""
Shared utilities for both codemath_solver and lqdoj_solver modules.
Contains common functions that can be reused across different solvers.
"""

import os
import re
import shutil
from typing import Optional

import pymupdf4llm


def clear_data(folder_path: str = "data"):
    """
    Clear all files in the specified folder.

    Args:
        folder_path: Path to the folder to clear
    """
    for file in os.listdir(folder_path):
        file_path = os.path.join(folder_path, file)
        try:
            if os.path.isfile(file_path):
                os.remove(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print(f"Error deleting {file_path}: {e}")


def extract_pdf_data(file_name: str) -> str:
    """
    Extract text data from PDF file using pymupdf4llm.

    Args:
        file_name: Path to the PDF file

    Returns:
        Extracted text as markdown
    """
    return pymupdf4llm.to_markdown(file_name)


def save_data(file_name: str, formatted_text: str) -> str:
    """
    Save formatted text to a file.

    Args:
        file_name: Original file name (PDF)
        formatted_text: Text content to save

    Returns:
        Path to the saved text file
    """
    output_file = file_name.replace(".pdf", ".txt")
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(formatted_text)
    return output_file


def format_data(text: str, platform_name: str = "CMOJ") -> str:
    """
    Format extracted text data with platform-specific rules.

    Args:
        text: Raw extracted text
        platform_name: Name of the platform (CMOJ, LQDOJ, etc.)

    Returns:
        Formatted text
    """
    # Remove header with platform name
    text = re.sub(rf"^.*?- {platform_name}:.*?\n", "", text)
    text = re.sub(r"\nhttps?://\S+ \d+/\d+", "", text)

    # Format section headers
    text = re.sub(r"\*\*Time limit:\*\*", "\n## Yêu cầu\nTime limit:", text)
    text = re.sub(r"\*\*Dữ liệu\*\*", "\n## Dữ liệu\n", text)
    text = re.sub(r"\*\*Kết quả\*\*", "\n## Kết quả\n", text)
    text = re.sub(r"\*\*Sample Input\*\*", "\n## Sample input\n", text)
    text = re.sub(r"\*\*Sample Output\*\*", "\n## Sample output\n", text)
    text = re.sub(r"\*\*Note\*\*", "\n## Note\n", text)

    # Number sample sections
    text = re.sub(r"## Sample input", "## Sample input 1", text, count=1)
    text = re.sub(r"## Sample output", "## Sample output 1", text, count=1)

    # Clean up formatting
    text = re.sub(r"```", "", text)
    text = re.sub(r"--*", "", text)

    return text.strip()


def process_ocr(file_name: str, platform_name: str = "CMOJ") -> str:
    """
    Process PDF file with OCR and format the extracted text.

    Args:
        file_name: Path to the PDF file
        platform_name: Name of the platform for formatting

    Returns:
        Path to the processed text file
    """
    pdf_data = extract_pdf_data(file_name)
    formatted_text = format_data(pdf_data, platform_name)
    return save_data(file_name, formatted_text)


def read_text_from_file(file_path: str) -> Optional[str]:
    """
    Read text content from a file.

    Args:
        file_path: Path to the text file

    Returns:
        File content or None if error
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            text = f.read()
        print(f"✅ Successfully read content from file: {file_path}")
        return text
    except FileNotFoundError:
        print(f"❌ Error: File '{file_path}' not found.")
        return None
    except Exception as e:
        print(f"❌ Error reading file '{file_path}': {e}")
        return None


def save_code_to_file(code: str, output_path: str) -> bool:
    """
    Save Python code to a file.

    Args:
        code: Python code to save
        output_path: Path to save the code

    Returns:
        True if successful, False otherwise
    """
    if not code:
        print("❌ No code to save.")
        return False

    try:
        output_dir = os.path.dirname(output_path)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir, exist_ok=True)
            print(f"✅ Created directory: {output_dir}")

        with open(output_path, "w", encoding="utf-8") as f:
            f.write(code)
        print(f"✅ Successfully saved code to file: {output_path}")
        return True
    except Exception as e:
        print(f"❌ Error saving file '{output_path}': {e}")
        return False


def extract_python_code(response_text: str) -> Optional[str]:
    """
    Extract Python code from Gemini response text.

    Args:
        response_text: Response text from Gemini API

    Returns:
        Extracted Python code or None if not found
    """
    if not response_text:
        return None

    # Try to find Python code block first
    match = re.search(
        r"```python\s*\n(.*?)\n```", response_text, re.DOTALL | re.IGNORECASE
    )
    if match:
        print("✅ Found Python code block.")
        return match.group(1).strip()
    else:
        # Try generic code block
        match = re.search(r"```\s*\n(.*?)\n```", response_text, re.DOTALL)
        if match:
            print(
                "⚠️ Warning: Found a generic code block (```...```), assuming it is Python code."
            )
            return match.group(1).strip()
        else:
            print("❌ No Python code block (```python ... ```) found in the response.")
            print("Full response from Gemini (may not contain expected code):\n---")
            print(response_text)
            print("---\nCannot extract code.")
            return None

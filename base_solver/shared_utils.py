"""
Shared utilities for both codemath_solver and lqdoj_solver modules.
Contains common functions that can be reused across different solvers.
"""

import math
import os
import random
import re
import shutil
from pathlib import Path
from typing import List, Optional, Tuple

import pyautogui
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


def find_project_root(marker_file=".git"):
    """
    Find the project root directory by traversing up from the current working directory
    until a marker file (e.g., .git or pyproject.toml) is found.
    """
    current = Path.cwd().resolve()
    for parent in [current] + list(current.parents):
        if (parent / marker_file).exists():
            return parent
    raise FileNotFoundError(f"Could not find project root containing {marker_file}")


def chunk_list(lst: list, n: int) -> List[List]:
    """
    Split list into n nearly equal parts.

    Args:
        lst: List to split
        n: Number of parts to split into

    Returns:
        List of sublists
    """
    chunk_size = math.ceil(len(lst) / n)
    return [lst[i : i + chunk_size] for i in range(0, len(lst), chunk_size)]


def calculate_window_layout(
    num_workers: int, screen_width: int = 1920, screen_height: int = 1080
) -> List[Tuple[int, int, int, int]]:
    """
    Calculate window layout for Chrome windows based on number of workers.

    Args:
        num_workers: Number of workers (windows)
        screen_width: Screen width
        screen_height: Screen height

    Returns:
        List of tuples (x, y, width, height) for each window
    """
    # Default window size
    window_width = 800
    window_height = 600

    # Calculate layout based on number of workers
    if num_workers <= 2:
        # 2 windows: side by side
        cols = 2
        rows = 1
    elif num_workers <= 4:
        # 3-4 windows: 2x2 grid
        cols = 2
        rows = 2
    elif num_workers <= 6:
        # 5-6 windows: 3x2 grid
        cols = 3
        rows = 2
    else:
        # 7+ windows: 3x3 grid (maximum 9 windows)
        cols = 3
        rows = 3

    # Calculate distance between windows
    margin_x = 50
    margin_y = 50

    # Calculate actual window size
    available_width = screen_width - (cols + 1) * margin_x
    available_height = screen_height - (rows + 1) * margin_y

    actual_width = min(window_width, available_width // cols)
    actual_height = min(window_height, available_height // rows)

    # Create layout for each window
    layouts = []
    for i in range(min(num_workers, cols * rows)):
        row = i // cols
        col = i % cols

        x = margin_x + col * (actual_width + margin_x)
        y = margin_y + row * (actual_height + margin_y)

        # Ensure windows don't go off-screen
        x = max(0, min(x, screen_width - actual_width))
        y = max(0, min(y, screen_height - actual_height))

        layouts.append((x, y, actual_width, actual_height))

    return layouts


def create_temp_profile() -> str:
    """
    Create a temporary profile directory for each process by duplicating from base profile.

    Returns:
        Path to temporary profile directory
    """

    # Get project root
    project_root = find_project_root()
    base_profile_dir = os.path.join(project_root, "chrome_profile")

    # Create temp directory
    temp_dir = os.path.join(
        project_root,
        "chrome_profile_temp",
        f"chrome_profile_{random.randint(100000, 999999)}",
    )

    # Check if base profile exists and duplicate it
    if os.path.exists(base_profile_dir):
        print(f"📋 Duplicating base profile from: {base_profile_dir}")
        print(f"📋 To temporary profile: {temp_dir}")
        shutil.copytree(base_profile_dir, temp_dir)
    else:
        print(f"⚠️ Base chrome profile not found at: {base_profile_dir}")
        print("🔧 Creating new chrome profile...")
        os.makedirs(temp_dir, exist_ok=True)

    print(f"🔄 Created temporary profile: {temp_dir}")
    return temp_dir


def cleanup_temp_profile(profile_dir: str) -> None:
    """
    Cleanup temporary profile directory.

    Args:
        profile_dir: Path đến temporary profile directory
    """
    try:
        shutil.rmtree(profile_dir)
        print(f"🧹 Cleaned up temporary profile: {profile_dir}")
    except Exception as e:
        print(f"⚠️ Failed to clean up profile {profile_dir}: {e}")


def get_screen_resolution() -> Tuple[int, int]:
    """
    Get the screen resolution.

    Args:
        None

    Returns:
        Tuple (width, height) of the screen
    """
    return pyautogui.size()

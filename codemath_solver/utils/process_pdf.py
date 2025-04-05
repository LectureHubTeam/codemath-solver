import pathlib
import re

import pymupdf4llm


def format_data(text):
    text = re.sub(r"^.*?- CMOJ:.*?\n", "", text)
    text = re.sub(r"\nhttps?://\S+ \d+/\d+", "", text)

    text = re.sub(r"\*\*Time limit:\*\*", "\n## Yêu cầu\nTime limit:", text)
    text = re.sub(r"\*\*Dữ liệu\*\*", "\n## Dữ liệu\n", text)
    text = re.sub(r"\*\*Kết quá\*\*", "\n## Kết quả\n", text)
    text = re.sub(r"\*\*Sample Input\*\*", "\n## Sample input\n", text)
    text = re.sub(r"\*\*Sample Output\*\*", "\n## Sample output\n", text)
    text = re.sub(r"\*\*Note\*\*", "\n## Note\n", text)

    text = re.sub(r"## Sample input", "## Sample input 1", text, count=1)
    text = re.sub(r"## Sample output", "## Sample output 1", text, count=1)

    text = re.sub(r"```", "", text)
    text = re.sub(r"--*", "", text)

    return text.strip()


def extract_pdf_data(file_name: str):
    return pymupdf4llm.to_markdown(file_name)


def save_data(file_name: str, formatted_text: str):
    output_file = file_name.replace(".pdf", ".txt")
    pathlib.Path(output_file).write_text(formatted_text)
    return output_file


def process_ocr(file_name: str):
    pdf_data = extract_pdf_data(file_name)

    formatted_text = format_data(pdf_data)

    return save_data(file_name, formatted_text)

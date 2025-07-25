import os
import re
import time
from typing import Optional

import google.generativeai as genai
from alive_progress import alive_it
from dotenv import load_dotenv

from conf.prompt import GEMINI_PROMPT_REFACTOR_CODE

load_dotenv()


class CodeRefactorer:
    """
    A class to refactor Python code using the Gemini model.
    """

    def __init__(self):
        """Initialize the CodeRefactorer with Gemini API configuration."""
        self.api_key = os.getenv("GEMINI_API_KEY")
        self.model_name = os.getenv(
            "GEMINI_MODEL_REFACTOR_CODE_NAME", "gemini-2.5-flash-lite-preview-06-17"
        )
        if not self.api_key:
            raise Exception("Error: Gemini API Key not provided.")
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel(self.model_name)

        # Default system prompt for code refactoring
        self.default_system_prompt = GEMINI_PROMPT_REFACTOR_CODE

    def read_python_file(self, file_path: str) -> Optional[str]:
        """
        Read the content of a Python file.

        Args:
            file_path (str): Path to the Python file

        Returns:
            Optional[str]: File content or None if error occurs
        """
        try:
            if not os.path.exists(file_path):
                print(f"❌ Error: File '{file_path}' not found.")
                return None

            if not file_path.endswith(".py"):
                print(f"❌ Error: File '{file_path}' is not a Python file.")
                return None

            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
            return content
        except Exception as e:
            print(f"❌ Error reading file '{file_path}': {e}")
            return None

    def refactor_code_with_gemini(
        self,
        file_path: str,
        system_prompt: Optional[str] = None,
        output_path: Optional[str] = None,
    ) -> Optional[str]:
        """
        Refactor a Python file using the Gemini model.

        Args:
            file_path (str): Path to the Python file to refactor
            system_prompt (Optional[str]): Custom system prompt for refactoring
            output_path (Optional[str]): Path to save the refactored code (optional)

        Returns:
            Optional[str]: Refactored code or None if error occurs
        """
        # Read the original code
        original_code = self.read_python_file(file_path)
        if not original_code:
            return None

        # Prepare the prompt
        prompt = self._build_refactor_prompt(
            original_code,
            system_prompt,
        )

        try:
            print(
                f"\n🔄 Sending code to Gemini API for refactoring with model: {self.model_name} ..."
            )
            response = self.model.generate_content(prompt)
            print("✅ Received refactored code from Gemini.")

            if not response.parts:
                if (
                    hasattr(response, "prompt_feedback")
                    and response.prompt_feedback.block_reason
                ):
                    print(
                        f"❌ Error: Request blocked. Reason: {response.prompt_feedback.block_reason}"
                    )
                    return None
                elif hasattr(response, "text"):
                    refactored_code = response.text
                else:
                    print("❌ Error: Gemini response does not contain expected content.")
                    return None
            else:
                refactored_code = response.text

            # Extract Python code from response
            extracted_code = self._extract_python_code(refactored_code)
            if not extracted_code:
                print("❌ No refactored code extracted from Gemini response.")
                return None

            # Save refactored code if output path is provided
            if output_path:
                success = self._save_refactored_code(extracted_code, output_path)
                if success:
                    print(f"✅ Refactored code saved to: {output_path}")

            return extracted_code

        except Exception as e:
            print(f"❌ Error calling Gemini API for refactoring: {e}")
            return None

    def _build_refactor_prompt(
        self,
        original_code: str,
        system_prompt: Optional[str] = None,
    ) -> str:
        """
        Build the complete prompt for code refactoring.

        Args:
            original_code (str): The original Python code
            system_prompt (Optional[str]): Custom system prompt

        Returns:
            str: Complete prompt for Gemini
        """
        # Use custom system prompt or default
        base_prompt = system_prompt if system_prompt else self.default_system_prompt

        # Build the complete prompt
        prompt = f"{base_prompt}\n\n"

        prompt += f"Đây là code cần refactor:\n```python\n{original_code}\n```\n\n"
        prompt += "Hãy refactor code theo các quy tắc sau đã được cung cấp."

        return prompt

    def _extract_python_code(self, response_text: str) -> Optional[str]:
        """
        Extract Python code from Gemini response.

        Args:
            response_text (str): Response from Gemini

        Returns:
            Optional[str]: Extracted Python code or None
        """
        if not response_text:
            return None

        # Try to find Python code block
        match = re.search(
            r"```python\s*\n(.*?)\n```", response_text, re.DOTALL | re.IGNORECASE
        )

        if match:
            print("✅ Found Python code block in response.")
            return match.group(1).strip()
        else:
            # Try generic code block
            match = re.search(r"```\s*\n(.*?)\n```", response_text, re.DOTALL)
            if match:
                print(
                    "⚠️ Warning: Found generic code block, assuming it's Python code."
                )
                return match.group(1).strip()
            else:
                print("❌ No code block found in the response.")
                print("Full response from Gemini:\n---")
                print(response_text)
                print("---")
                return None

    def _save_refactored_code(self, code: str, output_path: str) -> bool:
        """
        Save refactored code to a file.

        Args:
            code (str): The refactored code
            output_path (str): Path to save the code

        Returns:
            bool: True if successful, False otherwise
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
            print(f"✅ Successfully saved refactored code to: {output_path}")
            return True
        except Exception as e:
            print(f"❌ Error saving refactored code to '{output_path}': {e}")
            return False


def refactor_python_file(
    file_path: str,
    output_path: Optional[str] = None,
    system_prompt: Optional[str] = None,
) -> Optional[str]:
    """
    Convenience function to refactor a Python file.

    Args:
        file_path (str): Path to the Python file to refactor
        system_prompt (Optional[str]): Custom system prompt
        custom_instructions (Optional[str]): Additional instructions
        output_path (Optional[str]): Path to save refactored code
        focus_area (Optional[str]): Specific focus area for refactoring

    Returns:
        Optional[str]: Refactored code or None
    """
    try:
        refactorer = CodeRefactorer()

        return refactorer.refactor_code_with_gemini(
            file_path, system_prompt, output_path
        )
    except Exception as e:
        print(f"❌ Error initializing CodeRefactorer: {e}")
        return None


def refactor_python_folder(input_folder_path: str, output_folder_path: str) -> None:
    """
    Refactor all Python files in a folder.
    """
    os.makedirs(output_folder_path, exist_ok=True)

    file_refactored = os.listdir(output_folder_path)
    file_not_refactored = [
        file for file in os.listdir(input_folder_path) if file not in file_refactored
    ]
    print(f"Refactoring {len(file_not_refactored)} Python files ...")
    for file in alive_it(file_not_refactored, title="Refactoring Python files"):
        if file.endswith(".py"):
            input_file_path = os.path.join(input_folder_path, file)
            output_file_path = os.path.join(output_folder_path, file)
            refactored_code = refactor_python_file(input_file_path, output_file_path)
            if not refactored_code:
                time.sleep(5)


if __name__ == "__main__":
    refactor_python_folder(
        input_folder_path="submissions_codemath",
        output_folder_path="submissions_codemath_refactored",
    )

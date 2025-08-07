import os
import re
from typing import Optional

import google.generativeai as genai
from alive_progress import alive_it
from dotenv import load_dotenv

from conf.prompt import GEMINI_PROMPT_REFACTOR_CODE

load_dotenv()


class LQDOJCodeRefactorer:
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
                    refactored_code = self._extract_python_code(response.text)
                else:
                    print("❌ Error: Gemini response does not contain expected content.")
                    return None
            else:
                refactored_code = self._extract_python_code(response.text)

            if refactored_code:
                if output_path:
                    if self._save_refactored_code(refactored_code, output_path):
                        print(f"✅ Refactored code saved to: {output_path}")
                        return output_path
                    else:
                        return None
                return refactored_code
            else:
                print("❌ Error: Could not extract refactored code from response.")
                return None

        except Exception as e:
            print(f"❌ Error calling Gemini API for refactoring: {e}")
            return None

    def _build_refactor_prompt(
        self,
        original_code: str,
        system_prompt: Optional[str] = None,
    ) -> str:
        """Build the prompt for code refactoring."""
        prompt = system_prompt or self.default_system_prompt
        prompt += f"\n\nOriginal code:\n```python\n{original_code}\n```"
        return prompt

    def _extract_python_code(self, response_text: str) -> Optional[str]:
        """
        Extract Python code from the Gemini response.

        Args:
            response_text (str): Response text from Gemini

        Returns:
            Optional[str]: Extracted Python code or None if not found
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
            # Try to find generic code block
            match = re.search(r"```\s*\n(.*?)\n```", response_text, re.DOTALL)
            if match:
                print(
                    "⚠️ Warning: Found a generic code block, assuming it is Python code."
                )
                return match.group(1).strip()
            else:
                # If no code block found, assume the entire response is code
                print(
                    "⚠️ Warning: No code block found, treating entire response as code."
                )
                return response_text.strip()

    def _save_refactored_code(self, code: str, output_path: str) -> bool:
        """Save the refactored code to a file."""
        try:
            # Ensure the directory exists
            os.makedirs(os.path.dirname(output_path), exist_ok=True)

            with open(output_path, "w", encoding="utf-8") as f:
                f.write(code)
            return True
        except Exception as e:
            print(f"❌ Error saving refactored code: {e}")
            return False


def refactor_python_file(
    file_path: str,
    output_path: Optional[str] = None,
    system_prompt: Optional[str] = None,
) -> Optional[str]:
    """
    Convenience function to refactor a Python file.

    Args:
        file_path: Path to the Python file to refactor
        output_path: Path to save the refactored code (optional)
        system_prompt: Custom system prompt for refactoring

    Returns:
        Refactored code or path to saved file
    """
    try:
        refactorer = LQDOJCodeRefactorer()
        return refactorer.refactor_code_with_gemini(
            file_path, system_prompt, output_path
        )
    except Exception as e:
        print(f"❌ Error creating refactorer: {e}")
        return None


def refactor_python_folder(input_folder_path: str, output_folder_path: str) -> None:
    """
    Refactor all Python files in a folder.

    Args:
        input_folder_path: Folder containing Python files to refactor
        output_folder_path: Folder to save refactored files
    """
    if not os.path.exists(input_folder_path):
        print(f"❌ Error: Input folder '{input_folder_path}' not found.")
        return

    os.makedirs(output_folder_path, exist_ok=True)

    python_files = [f for f in os.listdir(input_folder_path) if f.endswith(".py")]
    print(f"Found {len(python_files)} Python files to refactor.")

    for python_file in alive_it(python_files, title="Refactoring files"):
        print(f"\n🔄 Refactoring: {python_file}")

        input_path = os.path.join(input_folder_path, python_file)
        output_path = os.path.join(output_folder_path, f"refactored_{python_file}")

        result = refactor_python_file(input_path, output_path)

        if result:
            print(f"✅ Refactored {python_file}")
        else:
            print(f"❌ Failed to refactor {python_file}")


if __name__ == "__main__":
    # Example usage
    refactored_code = refactor_python_file(
        "example_solution.py", "refactored_solution.py"
    )
    print(refactored_code)

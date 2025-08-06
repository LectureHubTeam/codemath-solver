"""
Base class for Gemini-based problem solvers.
Contains common functionality for both codemath and lqdoj solvers.
"""

import os
from abc import ABC, abstractmethod
from typing import Optional

import google.generativeai as genai
from dotenv import load_dotenv

from .shared_utils import (
    extract_python_code,
    process_ocr,
    read_text_from_file,
    save_code_to_file,
)

load_dotenv()


class BaseGeminiSolver(ABC):
    """
    Abstract base class for Gemini-based problem solvers.
    Provides common functionality for solving problems using Gemini API.
    """

    def __init__(self, model_name: Optional[str] = None):
        """
        Initialize the base solver with Gemini API configuration.

        Args:
            model_name: Optional custom model name, defaults to env variable
        """
        self.api_key = os.getenv("GEMINI_API_KEY")
        self.model_name = model_name or os.getenv(
            "GEMINI_MODEL_NAME", "gemini-2.5-flash-preview-05-20"
        )

        if not self.api_key:
            raise Exception("Error: Gemini API Key not provided.")

        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel(self.model_name)

    @abstractmethod
    def get_prompt_text(self, problem_text: str) -> str:
        """
        Get the text prompt for the specific solver.
        Must be implemented by subclasses.

        Args:
            problem_text: The problem text to format

        Returns:
            Formatted prompt string
        """
        pass

    @abstractmethod
    def get_prompt_pdf(self) -> str:
        """
        Get the PDF prompt for the specific solver.
        Must be implemented by subclasses.

        Returns:
            PDF prompt string
        """
        pass

    def get_solution_from_gemini(self, problem_text: str) -> Optional[str]:
        """
        Get solution from Gemini API using text input.

        Args:
            problem_text: The problem text to solve

        Returns:
            Gemini response text or None if error
        """
        if not problem_text or problem_text.strip() == "":
            print("❌ Error: No problem text provided for Gemini.")
            return None

        try:
            prompt = self.get_prompt_text(problem_text)
            print(
                f"\n🔄 Sending request to Gemini API with model: {self.model_name} ..."
            )

            response = self.model.generate_content(prompt)
            print("✅ Received response from Gemini.")
            print(response)

            return self._process_gemini_response(response)

        except Exception as e:
            print(f"❌ Error calling Gemini API: {e}")
            return None

    def get_solution_from_gemini_pdf(self, pdf_path: str) -> Optional[str]:
        """
        Get solution from Gemini API using PDF input.

        Args:
            pdf_path: Path to the PDF file

        Returns:
            Gemini response text or None if error
        """
        try:
            with open(pdf_path, "rb") as pdf_file:
                pdf_bytes = pdf_file.read()

            prompt = self.get_prompt_pdf()
            print(f"\n🔄 Sending PDF to Gemini API with model: {self.model_name} ...")

            response = self.model.generate_content(
                [prompt, {"mime_type": "application/pdf", "data": pdf_bytes}]
            )
            print("✅ Received response from Gemini.")
            print(response)

            return self._process_gemini_response(response)

        except Exception as e:
            print(f"❌ Error calling Gemini API with PDF: {e}")
            return None

    def _process_gemini_response(self, response) -> Optional[str]:
        """
        Process Gemini API response and extract text content.

        Args:
            response: Gemini API response object

        Returns:
            Response text or None if error
        """
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
                return response.text
            else:
                print("❌ Error: Gemini response does not contain expected content.")
                return None
        return response.text

    def solve_problem(self, input_path: str, mode: str = "pdf") -> Optional[str]:
        """
        Solve a problem using the appropriate method.

        Args:
            input_path: Path to input file (PDF or text)
            mode: "pdf" or "text"

        Returns:
            Path to output solution file or None if error
        """
        # Determine output path
        output_file = (
            os.path.basename(input_path).replace(".txt", ".py").replace(".pdf", ".py")
        )
        output_path = os.path.join("submission", output_file)

        # Get solution based on mode
        if mode == "pdf":
            gemini_response = self.get_solution_from_gemini_pdf(input_path)
        else:
            input_text = process_ocr(file_name=input_path)
            problem_text = read_text_from_file(input_text)
            if not problem_text:
                print("❌ Cannot read input file content. Terminating program.")
                return None
            gemini_response = self.get_solution_from_gemini(problem_text)

        if not gemini_response:
            print("❌ No valid response received from Gemini. Terminating program.")
            return None

        # Extract and save Python code
        python_code = extract_python_code(gemini_response)
        if python_code:
            if save_code_to_file(python_code, output_path):
                return output_path
            else:
                print("❌ Failed to save code to file.")
                return None
        else:
            print("❌ No code extracted. No file will be saved.")
            return None

import os
import re

import google.generativeai as genai
from dotenv import load_dotenv

from codemath_solver.utils.process_pdf import process_ocr
from conf.settings import GEMINI_PROMPT_PDF, GEMINI_PROMPT_TEXT

load_dotenv()


class GeminiSolver:
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY")
        self.model_name = os.getenv(
            "GEMINI_MODEL_NAME", "gemini-2.5-flash-preview-05-20"
        )
        if not self.api_key:
            raise Exception("Error: Gemini API Key not provided.")
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel(self.model_name)

    def get_solution_from_gemini(self, problem_text):
        if not problem_text or problem_text.strip() == "":
            print("❌ Error: No problem text provided for Gemini.")
            return None
        try:
            prompt = GEMINI_PROMPT_TEXT.format(problem_text=problem_text)
            print(
                f"\n🔄 Sending request to Gemini API with model: {self.model_name} ..."
            )
            response = self.model.generate_content(prompt)
            print("✅ Received response from Gemini.")
            print(response)
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
        except Exception as e:
            print(f"❌ Error calling Gemini API: {e}")
            return None

    def get_solution_from_gemini_pdf(self, pdf_path):
        try:
            with open(pdf_path, "rb") as pdf_file:
                pdf_bytes = pdf_file.read()
            prompt = GEMINI_PROMPT_PDF
            print(f"\n🔄 Sending PDF to Gemini API with model: {self.model_name} ...")
            response = self.model.generate_content(
                [prompt, {"mime_type": "application/pdf", "data": pdf_bytes}]
            )
            print("✅ Received response from Gemini.")
            print(response)
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
        except Exception as e:
            print(f"❌ Error calling Gemini API with PDF: {e}")
            return None

    @staticmethod
    def extract_python_code(response_text):
        if not response_text:
            return None
        match = re.search(
            r"```python\s*\n(.*?)\n```", response_text, re.DOTALL | re.IGNORECASE
        )
        if match:
            print("✅ Found Python code block.")
            return match.group(1).strip()
        else:
            match = re.search(r"```\s*\n(.*?)\n```", response_text, re.DOTALL)
            if match:
                print(
                    "⚠️ Warning: Found a generic code block (```...```), assuming it is Python code."
                )
                return match.group(1).strip()
            else:
                print(
                    "❌ No Python code block (```python ... ```) found in the response."
                )
                print("Full response from Gemini (may not contain expected code):\n---")
                print(response_text)
                print("---\nCannot extract code.")
                return None

    @staticmethod
    def save_code_to_file(code, output_path):
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

    @staticmethod
    def read_text_from_file(file_path):
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

    def solve_problem(self, input_path: str, mode: str = "pdf"):
        output_file = (
            os.path.basename(input_path).replace(".txt", ".py").replace(".pdf", ".py")
        )
        output_path = os.path.join("submission", output_file)
        if mode == "pdf":
            gemini_response = self.get_solution_from_gemini_pdf(input_path)
        else:
            input_text = process_ocr(file_name=input_path)
            problem_text = self.read_text_from_file(input_text)
            if not problem_text:
                print("❌ Cannot read input file content. Terminating program.")
                return
            gemini_response = self.get_solution_from_gemini(problem_text)
        if not gemini_response:
            print("❌ No valid response received from Gemini. Terminating program.")
            return
        python_code = self.extract_python_code(gemini_response)
        if python_code:
            self.save_code_to_file(python_code, output_path)
            return output_path
        else:
            print("❌ No code extracted. No file will be saved.")


if __name__ == "__main__":
    input_file = "data/chiabi.pdf"  # Replace with your input file path
    solver = GeminiSolver()
    solver.solve_problem(input_file, mode="pdf")

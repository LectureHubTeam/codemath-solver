import json
import os
import re
from typing import Optional

import google.generativeai as genai
from dotenv import load_dotenv

from conf.prompt import GEMINI_PROMPT_EXPLANATION_CODE, PROMPT_EXPLANATION_TEMPLATE

load_dotenv()


def get_problem_code(info_json_path: str = "submissions_codemath/info.json") -> list:
    data_json = json.load(open(info_json_path, encoding="utf-8"))
    problem_code = []
    for submission_id, submission_data in data_json.items():
        problem_code.append(submission_data["problem"])
    problem_code = list(set(problem_code))
    print(f"Found {len(problem_code)} problems in {info_json_path}")
    return problem_code


class CodeExplainer:
    """
    A class to generate explanations for Python code solutions using the Gemini model.
    """

    def __init__(self):
        """Initialize the CodeExplainer with Gemini API configuration."""
        self.api_key = os.getenv("GEMINI_API_KEY")
        self.model_name = os.getenv(
            "GEMINI_MODEL_EXPLANATION_NAME", "gemini-2.5-flash-lite-preview-06-17"
        )
        if not self.api_key:
            raise Exception("Error: Gemini API Key not provided.")
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel(self.model_name)

        # Default system prompt for code explanation
        self.default_system_prompt = GEMINI_PROMPT_EXPLANATION_CODE

    def read_code_file(self, file_path: str) -> Optional[str]:
        """
        Read the content of a Python code file.

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
            print(f"✅ Successfully read code file: {file_path}")
            return content
        except Exception as e:
            print(f"❌ Error reading file '{file_path}': {e}")
            return None

    def generate_explanation(
        self,
        code_input: str,
        problem_description: Optional[str] = None,
        system_prompt: Optional[str] = None,
        output_path: Optional[str] = None,
        language: str = "Vietnamese",
    ) -> Optional[str]:
        """
        Generate a markdown explanation for Python code.
        If problem_description is a path to a PDF, send it as a file to Gemini.
        """
        # Determine if input is a file path or code string
        if os.path.exists(code_input) and code_input.endswith(".py"):
            code_content = self.read_code_file(code_input)
            if not code_content:
                return None
        else:
            code_content = code_input

        # Check if problem_description is a PDF file path
        pdf_bytes = None
        if (
            problem_description
            and os.path.exists(problem_description)
            and problem_description.lower().endswith(".pdf")
        ):
            with open(problem_description, "rb") as f:
                pdf_bytes = f.read()
            # Prompt for multimodal input
            prompt = self._build_explanation_prompt(
                code_content,
                None,  # No text description
                system_prompt,
                language,
                pdf_attached=True,
            )
        else:
            prompt = self._build_explanation_prompt(
                code_content, problem_description, system_prompt, language
            )

        try:
            print(
                f"\n🔄 Generating explanation with Gemini model: {self.model_name} ..."
            )
            if pdf_bytes:
                # Multimodal: send prompt and PDF
                response = self.model.generate_content(
                    [prompt, {"mime_type": "application/pdf", "data": pdf_bytes}]
                )
            else:
                response = self.model.generate_content(prompt)
            print("✅ Received explanation from Gemini.")

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
                    explanation = response.text
                else:
                    print("❌ Error: Gemini response does not contain expected content.")
                    return None
            else:
                explanation = response.text

            # Clean up the explanation
            cleaned_explanation = self._clean_explanation(explanation)

            # Save explanation if output path is provided
            if output_path:
                success = self._save_explanation(cleaned_explanation, output_path)
                if success:
                    print(f"✅ Explanation saved to: {output_path}")

            return cleaned_explanation

        except Exception as e:
            print(f"❌ Error calling Gemini API for explanation: {e}")
            return None

    def _build_explanation_prompt(
        self,
        code_content: str,
        problem_description: Optional[str] = None,
        system_prompt: Optional[str] = None,
        language: str = "Vietnamese",
        pdf_attached: bool = False,
    ) -> str:
        """
        Build the complete prompt for code explanation.
        If pdf_attached is True, instruct the model to use the attached PDF as the problem description.
        """
        # Use custom system prompt or default
        base_prompt = system_prompt if system_prompt else self.default_system_prompt

        # Add language instruction
        if language.lower() == "vietnamese":
            base_prompt += "\n\nWrite the explanation in Vietnamese."
        else:
            base_prompt += "\n\nWrite the explanation in English."

        # Build the complete prompt
        prompt = f"{base_prompt}\n\n"
        if pdf_attached:
            prompt += "The problem description is in the attached PDF file.\n\n"
        elif problem_description:
            prompt += f"Problem Description:\n{problem_description}\n\n"

        prompt += f"Python Code to Explain:\n```python\n{code_content}\n```\n\n"
        prompt += "Please provide a comprehensive explanation of this code following the guidelines above."
        return prompt

    def _clean_explanation(self, explanation: str) -> str:
        """
        Clean and format the explanation text.

        Args:
            explanation (str): Raw explanation from Gemini

        Returns:
            str: Cleaned explanation
        """
        if not explanation:
            return ""

        # Remove any markdown code block markers that might wrap the entire response
        explanation = re.sub(r"^```markdown\s*\n", "", explanation)
        explanation = re.sub(r"\n```$", "", explanation)

        # Ensure proper markdown formatting
        explanation = explanation.strip()

        return explanation

    def _save_explanation(self, explanation: str, output_path: str) -> bool:
        """
        Save explanation to a markdown file.

        Args:
            explanation (str): The explanation content
            output_path (str): Path to save the explanation

        Returns:
            bool: True if successful, False otherwise
        """
        if not explanation:
            print("❌ No explanation to save.")
            return False

        try:
            # Ensure output path has .md extension
            if not output_path.endswith(".md"):
                output_path += ".md"

            output_dir = os.path.dirname(output_path)
            if output_dir and not os.path.exists(output_dir):
                os.makedirs(output_dir, exist_ok=True)
                print(f"✅ Created directory: {output_dir}")

            with open(output_path, "w", encoding="utf-8") as f:
                f.write(explanation)
            print(f"✅ Successfully saved explanation to: {output_path}")
            return True
        except Exception as e:
            print(f"❌ Error saving explanation to '{output_path}': {e}")
            return False

    def generate_explanation_with_template(
        self,
        code_input: str,
        template_type: str = "comprehensive",
        problem_description: Optional[str] = None,
        output_path: Optional[str] = None,
        language: str = "Vietnamese",
    ) -> Optional[str]:
        """
        Generate explanation using predefined templates.

        Args:
            code_input (str): Python code to explain
            template_type (str): Type of explanation template
            problem_description (Optional[str]): Problem description
            output_path (Optional[str]): Output file path
            language (str): Language for explanation

        Returns:
            Optional[str]: Generated explanation
        """
        templates = PROMPT_EXPLANATION_TEMPLATE
        assert (
            template_type in templates
        ), f"Unknown template type: {template_type}, it must be in {templates.keys()}"

        custom_prompt = templates[template_type]
        return self.generate_explanation(
            code_input=code_input,
            problem_description=problem_description,
            system_prompt=custom_prompt,
            output_path=output_path,
            language=language,
        )


def generate_code_explanation(
    code_input: str,
    problem_description: Optional[str] = None,
    template_type: str = "comprehensive",
    output_path: Optional[str] = None,
    language: str = "Vietnamese",
) -> Optional[str]:
    """
    Convenience function to generate code explanation.

    Args:
        code_input (str): Python code or file path
        problem_description (Optional[str]): Description of the problem
        template_type (str): Type of explanation template
        output_path (Optional[str]): Path to save explanation
        language (str): Language for explanation

    Returns:
        Optional[str]: Generated explanation or None
    """
    if problem_description.endswith(".pdf") and not os.path.exists(problem_description):
        raise FileNotFoundError(f"❌ Error: File '{problem_description}' not found.")

    try:
        explainer = CodeExplainer()

        if template_type == "custom":
            return explainer.generate_explanation(
                code_input=code_input,
                problem_description=problem_description,
                output_path=output_path,
                language=language,
            )
        else:
            return explainer.generate_explanation_with_template(
                code_input=code_input,
                template_type=template_type,
                problem_description=problem_description,
                output_path=output_path,
                language=language,
            )
    except Exception as e:
        print(f"❌ Error initializing CodeExplainer: {e}")
        return None


def generate_explanations_for_folder(
    input_folder_path: str,
    output_folder_path: str,
    problem_folder_path: str,
    template_type: str = "comprehensive",
    language: str = "Vietnamese",
) -> None:
    """
    Generate explanations for all Python files in a folder.

    Args:
        input_folder_path (str): Path to folder containing Python files
        output_folder_path (str): Path to save explanation files
        template_type (str): Type of explanation template
        language (str): Language for explanations
    """
    try:
        explainer = CodeExplainer()
        problem_code = get_problem_code()

        # Create output directory
        os.makedirs(output_folder_path, exist_ok=True)

        # Get all Python files
        python_files = [f for f in os.listdir(input_folder_path) if f.endswith(".py")]

        print(f"📁 Generating explanations for {len(python_files)} Python files...")

        for i, code in enumerate(problem_code, 1):
            input_file = os.path.join(input_folder_path, code + ".py")
            output_file = os.path.join(output_folder_path, code + ".md")
            problem_description = os.path.join(problem_folder_path, code + ".pdf")
            if os.path.exists(output_file):
                continue

            print(f"\n🔄 [{i}/{len(problem_code)}] Processing: {code}")

            explanation = explainer.generate_explanation_with_template(
                code_input=input_file,
                problem_description=problem_description,
                template_type=template_type,
                output_path=output_file,
                language=language,
            )

            if explanation:
                print(f"✅ Successfully generated explanation for: {code}")
            else:
                print(f"❌ Failed to generate explanation for: {code}")

        print("\n🎉 Explanation generation completed!")
        print(f"📁 Output folder: {output_folder_path}")

    except Exception as e:
        print(f"❌ Error in batch explanation generation: {e}")


if __name__ == "__main__":
    # Generate explanation for code string
    # explanation = generate_code_explanation(
    #     code_input="submissions_codemath_refactored/24702.py",
    #     problem_description="data/xemgio_tb24.pdf",
    #     template_type="comprehensive",
    #     output_path="xemgio_tb24_v2.md",
    #     language="Vietnamese"
    # )

    # if explanation:
    #     print("✅ Explanation generated successfully!")
    # else:
    #     print("❌ Failed to generate explanation.")

    # Example: Generate explanations for a folder
    generate_explanations_for_folder(
        input_folder_path="submissions_codemath_refactored_renamed",
        output_folder_path="explanations",
        problem_folder_path="data",
        template_type="comprehensive",
        language="Vietnamese",
    )

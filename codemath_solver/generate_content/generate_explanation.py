"""
CodeMath code explanation generator.
Inherits from BaseCodeExplainer to provide CodeMath-specific functionality.
"""

import os

from base_solver.base_explainer import BaseCodeExplainer
from conf.prompt import GEMINI_PROMPT_EXPLANATION_CODE, PROMPT_EXPLANATION_TEMPLATE


class CodeExplainer(BaseCodeExplainer):
    """
    CodeMath-specific code explanation generator.
    Inherits common functionality from BaseCodeExplainer.
    """

    def get_default_system_prompt(self) -> str:
        """
        Get the default system prompt for CodeMath code explanation.

        Returns:
            Default system prompt string for CodeMath
        """
        return GEMINI_PROMPT_EXPLANATION_CODE

    def get_info_json_path(self) -> str:
        """
        Get the path to the CodeMath info.json file.

        Returns:
            Path to CodeMath info.json file
        """
        return "submissions_codemath/info.json"

    def get_explanation_templates(self) -> dict:
        """
        Get the explanation templates for CodeMath.

        Returns:
            Dictionary of template types to prompts
        """
        return PROMPT_EXPLANATION_TEMPLATE


def generate_code_explanation(
    code_input: str,
    problem_description=None,
    template_type: str = "comprehensive",
    output_path=None,
    language: str = "Vietnamese",
) -> str:
    """
    Convenience function to generate code explanation.

    Args:
        code_input (str): Python code or file path
        problem_description (Optional[str]): Description of the problem
        template_type (str): Type of explanation template
        output_path (Optional[str]): Path to save explanation
        language (str): Language for explanation

    Returns:
        Generated explanation or None
    """
    if (
        problem_description
        and problem_description.endswith(".pdf")
        and not os.path.exists(problem_description)
    ):
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
        problem_folder_path (str): Path to folder containing problem PDFs
        template_type (str): Type of explanation template
        language (str): Language for explanations
    """
    try:
        explainer = CodeExplainer()
        explainer.generate_explanations_for_folder(
            input_folder_path=input_folder_path,
            output_folder_path=output_folder_path,
            problem_folder_path=problem_folder_path,
            template_type=template_type,
            language=language,
        )
    except Exception as e:
        print(f"❌ Error in batch explanation generation: {e}")


if __name__ == "__main__":
    # Example: Generate explanations for a folder
    generate_explanations_for_folder(
        input_folder_path="submissions_codemath_refactored_renamed",
        output_folder_path="explanations",
        problem_folder_path="data",
        template_type="comprehensive",
        language="Vietnamese",
    )

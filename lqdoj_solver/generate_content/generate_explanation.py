"""
LQDOJ code explanation generator.
Inherits from BaseCodeExplainer to provide LQDOJ-specific functionality.
"""

from base_solver.base_explainer import BaseCodeExplainer
from conf.prompt import GEMINI_PROMPT_EXPLANATION_CODE, PROMPT_EXPLANATION_TEMPLATE


class LQDOJCodeExplainer(BaseCodeExplainer):
    """
    LQDOJ-specific code explanation generator.
    Inherits common functionality from BaseCodeExplainer.
    """

    def get_default_system_prompt(self) -> str:
        """
        Get the default system prompt for LQDOJ code explanation.

        Returns:
            Default system prompt string for LQDOJ
        """
        return GEMINI_PROMPT_EXPLANATION_CODE

    def get_info_json_path(self) -> str:
        """
        Get the path to the LQDOJ info.json file.

        Returns:
            Path to LQDOJ info.json file
        """
        return "submissions_lqdoj/info.json"

    def get_explanation_templates(self) -> dict:
        """
        Get the explanation templates for LQDOJ.

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
        code_input: Path to Python file or code string
        problem_description: Problem description or path to PDF
        template_type: Type of explanation template
        output_path: Path to save the explanation
        language: Language for explanation

    Returns:
        Generated explanation or path to saved file
    """
    try:
        explainer = LQDOJCodeExplainer()
        return explainer.generate_explanation_with_template(
            code_input, template_type, problem_description, output_path, language
        )
    except Exception as e:
        print(f"❌ Error creating explainer: {e}")
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
        input_folder_path: Folder containing Python solution files
        output_folder_path: Folder to save explanations
        problem_folder_path: Folder containing problem PDFs
        template_type: Type of explanation template
        language: Language for explanations
    """
    try:
        explainer = LQDOJCodeExplainer()
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
    # Example usage
    explanation = generate_code_explanation(
        "example_solution.py", "example_problem.pdf", "comprehensive", "explanation.md"
    )
    print(explanation)

"""
Agent configuration settings for LQDOJ and CodeMath solvers.
Contains all initialization parameters for web automation agents.
"""

# LQDOJ Agent Configuration
LQDOJ_AGENT_CONFIG = {
    "url_base": "https://lqdoj.edu.vn",
    "prefix": "lqdoj",
    "solved_status_icon": "i.solved-problem-color.title-state.fa.fa-check-circle",
    "unsolved_status_icon": "i.attempted-problem-color.title-state.fa.fa-minus-circle",
    "select_file_submit": "id_source_file",
    "button_submit": '//*[@id="submit-button"]',
    "problem_title_class": "problem-title",
    "pdf_button_id": "pdf_button",
}

# CodeMath Agent Configuration
CODEMATH_AGENT_CONFIG = {
    "url_base": "https://laptrinh.codemath.vn",
    "prefix": "codemath",
    "solved_status_icon": "i.solved-problem-color.title-state.fa.fa-check-circle",
    "unsolved_status_icon": "i.attempted-problem-color.title-state.fa.fa-frown-o",
    "select_file_submit": "file_select",
    "button_submit": '//*[@id="problem_submit"]/div[2]/input[2]',
    "problem_title_class": "problem-title",
    "pdf_button_id": "pdf_button",
}

# Common Agent Configuration
COMMON_AGENT_CONFIG = {
    "wait_time": 3,
    "download_wait_time": 3,
    "submit_wait_time": 3,
    "navigation_wait_time": 2,
}

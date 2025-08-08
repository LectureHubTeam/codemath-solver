"""
LQDOJ web automation agent.
Inherits from BaseAgent to provide LQDOJ-specific functionality.
"""

import os
import time
from concurrent.futures import ProcessPoolExecutor

from base_solver.base_agent import BaseAgent
from base_solver.shared_utils import (
    calculate_window_layout,
    chunk_list,
    cleanup_temp_profile,
    create_temp_profile,
    get_screen_resolution,
)
from conf.agent_settings import LQDOJ_AGENT_CONFIG
from lqdoj_solver.agent.llm import LQDOJGeminiSolver


class LQDOJAgent(BaseAgent):
    """
    LQDOJ-specific web automation agent.
    Inherits common functionality from BaseAgent.
    """

    def __init__(self, profile_dir=None, window_layout=None):
        super().__init__(
            url_base=LQDOJ_AGENT_CONFIG["url_base"],
            prefix=LQDOJ_AGENT_CONFIG["prefix"],
            solved_status_icon=LQDOJ_AGENT_CONFIG["solved_status_icon"],
            unsolved_status_icon=LQDOJ_AGENT_CONFIG["unsolved_status_icon"],
            select_file_submit=LQDOJ_AGENT_CONFIG["select_file_submit"],
            button_submit=LQDOJ_AGENT_CONFIG["button_submit"],
            problem_title_class=LQDOJ_AGENT_CONFIG["problem_title_class"],
            profile_dir=profile_dir,
            window_layout=window_layout,
        )

    def create_solver(self):
        """
        Create the LQDOJ solver instance.

        Returns:
            LQDOJ solver instance
        """
        return LQDOJGeminiSolver()


def process_problem_batch(
    problem_batch: list, worker_id: int = 0, window_layout: tuple = None
):
    """Process a batch of problems with customized window layout"""
    start_time = time.time()
    process_id = os.getpid()

    print(
        f"🚀 Process {process_id} (Worker {worker_id}) starting batch: {problem_batch}"
    )

    # Create temporary profile for this worker
    profile_dir = create_temp_profile()

    # Use provided window layout or calculate default
    if window_layout is None:
        screen_width, screen_height = get_screen_resolution()
        window_layouts = calculate_window_layout(1, screen_width, screen_height)
        window_layout = window_layouts[0] if window_layouts else (100, 100, 800, 600)

    print(f"🖥️ Worker {worker_id} using window layout: {window_layout}")

    try:
        agent = LQDOJAgent(profile_dir=profile_dir, window_layout=window_layout)
        agent.process_problems(problem_batch)
    finally:
        agent.cleanup()
        cleanup_temp_profile(profile_dir)

    end_time = time.time()
    print(
        f"✅ Process {process_id} (Worker {worker_id}) completed batch in {end_time - start_time:.2f}s"
    )


def run_parallel_processing(problem_ids: list, max_workers: int = 2):
    """
    Run parallel processing for a list of problems.

    Args:
        problem_ids: List of problem IDs to process
        max_workers: Maximum number of workers
    """
    # Split problem_ids into batches
    problem_batches = chunk_list(problem_ids, max_workers)

    print(f"📋 Total problems: {len(problem_ids)}")
    print(f"🔧 Workers: {max_workers}")
    for i, batch in enumerate(problem_batches):
        print(f"   Worker {i + 1}: {batch} ({len(batch)} problems)")

    # Calculate overall window layout
    screen_width, screen_height = get_screen_resolution()
    window_layouts = calculate_window_layout(max_workers, screen_width, screen_height)

    print(f"🖥️ Screen resolution: {screen_width}x{screen_height}")
    for i, layout in enumerate(window_layouts):
        x, y, width, height = layout
        print(f"   Window {i + 1}: position=({x},{y}), size=({width}x{height})")

    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        # Submit tasks with specific window layouts
        futures = []
        for i, batch in enumerate(problem_batches):
            # Get the window layout for this worker
            worker_layout = (
                window_layouts[i] if i < len(window_layouts) else (100, 100, 800, 600)
            )
            future = executor.submit(process_problem_batch, batch, i, worker_layout)
            futures.append(future)

        # Wait for all to complete
        for future in futures:
            future.result()

    print("🎉 All problems processed!")


if __name__ == "__main__":
    problem_ids = ["ktp2a11", "skydef", "mang1cb06", "subseq01", "pig", "coin34"]
    max_workers = 1

    run_parallel_processing(problem_ids, max_workers)

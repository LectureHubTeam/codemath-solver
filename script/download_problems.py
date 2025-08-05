#!/usr/bin/env python3
"""
Script to download all problems from info.json using the download_problem function
"""

import json
import sys
import time
from pathlib import Path
from typing import Dict, List

from codemath_solver.agent.tools import CodeMathAgent

# Add the parent directory to the path to import codemath_solver
sys.path.append(str(Path(__file__).parent.parent))


def load_problems_from_info() -> List[str]:
    """Load all unique problem codes from info.json"""
    info_path = Path(__file__).parent.parent / "submissions_codemath" / "info.json"

    if not info_path.exists():
        raise FileNotFoundError(f"info.json not found at {info_path}")

    with open(info_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Extract unique problem codes
    problem_codes = set()
    for submission_id, submission_data in data.items():
        if "problem" in submission_data:
            problem_codes.add(submission_data["problem"])

    return sorted(list(problem_codes))


def create_agent_with_retry(max_retries: int = 3) -> CodeMathAgent:
    """
    Create a CodeMathAgent with retry logic for ChromeDriver issues
    """
    for attempt in range(max_retries):
        try:
            print(
                f"🔄 Attempting to create Chrome driver (attempt {attempt + 1}/{max_retries})"
            )
            agent = CodeMathAgent()
            print("✅ Chrome driver created successfully")
            return agent
        except Exception as e:
            print(f"❌ Failed to create Chrome driver (attempt {attempt + 1}): {str(e)}")
            if attempt < max_retries - 1:
                print("⏳ Waiting 5 seconds before retry...")
                time.sleep(5)
            else:
                raise Exception(
                    f"Failed to create Chrome driver after {max_retries} attempts: {str(e)}"
                )

    # This should never be reached due to the exception above, but needed for type checking
    raise Exception("Failed to create Chrome driver after all attempts")


def download_problems(
    problem_codes: List[str], batch_size: int = 10
) -> Dict[str, bool]:
    """
    Download problems in batches to avoid overwhelming the system

    Args:
        problem_codes: List of problem codes to download
        batch_size: Number of problems to process before restarting Chrome

    Returns:
        Dictionary mapping problem codes to success status
    """
    print(
        f"🔄 Starting download of {len(problem_codes)} problems in batches of {batch_size}"
    )

    results = {}
    total_batches = (len(problem_codes) + batch_size - 1) // batch_size

    for batch_num in range(total_batches):
        start_idx = batch_num * batch_size
        end_idx = min(start_idx + batch_size, len(problem_codes))
        batch_problems = problem_codes[start_idx:end_idx]

        print(
            f"\n📦 Processing batch {batch_num + 1}/{total_batches} ({len(batch_problems)} problems)"
        )
        print("Problems: " + ", ".join(batch_problems))

        # Create a new agent for each batch with retry logic
        agent = None
        try:
            agent = create_agent_with_retry()

            for i, problem_code in enumerate(batch_problems, 1):
                try:
                    print(f"📥 [{i}/{len(batch_problems)}] Downloading {problem_code}")

                    # Navigate to the problem page
                    url = f"https://laptrinh.codemath.vn/problem/{problem_code}"
                    agent.driver.get(url)
                    time.sleep(3)  # Increased wait time for stability

                    # Download the problem
                    file_name = f"{problem_code}.pdf"
                    agent.download_problem(file_name=file_name)

                    results[problem_code] = True
                    print(f"✅ Successfully downloaded {problem_code}")

                    # Small delay between downloads
                    time.sleep(1)

                except Exception as e:
                    print(f"❌ Error downloading {problem_code}: {str(e)}")
                    results[problem_code] = False

        except Exception as e:
            print(f"❌ Error initializing agent for batch {batch_num + 1}: {str(e)}")
            # Mark all problems in this batch as failed
            for problem_code in batch_problems:
                results[problem_code] = False

        finally:
            if agent and hasattr(agent, "driver"):
                try:
                    agent.driver.quit()
                    print(f"🔒 Closed Chrome driver for batch {batch_num + 1}")
                except Exception:
                    pass

            # Wait between batches to let Chrome stabilize
            if batch_num < total_batches - 1:
                print("⏳ Waiting 5 seconds before next batch...")
                time.sleep(5)

    return results


def check_chrome_debugging():
    """Check if Chrome is running with remote debugging enabled"""
    import subprocess

    try:
        # Check if Chrome is running with remote debugging port 9222
        result = subprocess.run(
            ["pgrep", "-f", "chrome.*remote-debugging-port=9222"],
            capture_output=True,
            text=True,
        )

        if result.returncode == 0:
            print("✅ Chrome is running with remote debugging enabled")
            return True
        else:
            print("❌ Chrome is not running with remote debugging enabled")
            print("Please start Chrome with:")
            print(
                "/Applications/Google\\ Chrome.app/Contents/MacOS/Google\\ Chrome "
                '--remote-debugging-port=9222 --user-data-dir="/tmp/ChromeProfile"'
            )
            return False

    except Exception as e:
        print(f"❌ Error checking Chrome status: {str(e)}")
        return False


def main():
    """Main function to orchestrate the download process"""
    print("🎯 CodeMath Problem Downloader")
    print("=" * 50)

    # Check Chrome debugging status
    if not check_chrome_debugging():
        print("\nPlease start Chrome with remote debugging and run this script again.")
        return

    # Load problem codes from info.json
    try:
        problem_codes = load_problems_from_info()
        print(f"📋 Found {len(problem_codes)} unique problems in info.json")
    except Exception as e:
        print(f"❌ Error loading problems: {str(e)}")
        return

    # Create data directory if it doesn't exist
    data_dir = Path(__file__).parent.parent / "data"
    data_dir.mkdir(exist_ok=True)

    # Ask user for batch size
    print("\n📊 Download Configuration:")
    print(
        "Due to Chrome debugging limitations, downloads will be processed in batches."
    )
    print("Each batch will restart Chrome to ensure stability.")

    batch_size = 10
    while True:
        try:
            user_input = input(f"Batch size (1-20, default {batch_size}): ").strip()
            if not user_input:
                break
            batch_size = int(user_input)
            if 1 <= batch_size <= 20:
                break
            print("Please enter a number between 1 and 20")
        except ValueError:
            print("Please enter a valid number")

    print("\n🚀 Starting download process...")
    start_time = time.time()

    # Download problems
    results = download_problems(problem_codes, batch_size)

    # Calculate statistics
    end_time = time.time()
    duration = end_time - start_time

    successful = sum(1 for success in results.values() if success)
    failed = len(results) - successful

    print("\n" + "=" * 50)
    print("📊 Download Summary")
    print("=" * 50)
    print(f"Total problems: {len(problem_codes)}")
    print(f"Successfully downloaded: {successful}")
    print(f"Failed: {failed}")
    print(f"Success rate: {(successful / len(problem_codes) * 100):.1f}%")
    print(f"Total time: {duration:.2f} seconds")
    print(f"Average time per problem: {duration / len(problem_codes):.2f} seconds")

    # Show failed downloads
    if failed > 0:
        print("\n❌ Failed downloads:")
        for problem_code, success in results.items():
            if not success:
                print(f"  - {problem_code}")

    print(f"\n📁 Downloaded files are saved in: {data_dir.absolute()}")


if __name__ == "__main__":
    main()

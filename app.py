import os
import subprocess  # To call other python scripts

import pandas as pd
import streamlit as st

from codemath_solver.agent.tools import start_process
from codemath_solver.utils.select_problems import get_filtered_problems
from conf import settings

# --- Configuration ---
CSV_FILE = settings.CSV_FILE
CRAWL_SCRIPT = "codemath_solver/crawl/core.py"


def run_script(script_path, args=[]):
    """Executes a Python script using subprocess."""
    try:
        process = subprocess.run(
            ["python", script_path] + args, capture_output=True, text=True, check=True
        )
        st.success(f"Successfully executed {script_path}")
        st.text("Output:")
        st.code(process.stdout)
        if process.stderr:
            st.warning("Stderr:")
            st.code(process.stderr)
        return True
    except subprocess.CalledProcessError as e:
        st.error(f"Error executing {script_path}:")
        st.code(e.stderr)
        return False
    except FileNotFoundError:
        st.error(f"Error: Script not found at {script_path}")
        return False


# --- Streamlit App ---


st.set_page_config(layout=settings.STREAMLIT.get("layout", "wide"))
st.title(settings.STREAMLIT.get("title", "CodeMath Solver"))

# Initialize session state
if "selected_problems" not in st.session_state:
    st.session_state.selected_problems = []
if "data_loaded" not in st.session_state:
    st.session_state.data_loaded = os.path.exists(CSV_FILE)
if "df" not in st.session_state:
    st.session_state.df = None

# --- 1. Crawling Section ---
st.header("1. Crawl Problems")
if st.button("Start Crawling"):
    with st.spinner("Crawling problems... Please wait."):
        if run_script(CRAWL_SCRIPT):
            st.session_state.data_loaded = True
            st.session_state.df = None  # Force reload
            st.rerun()  # Rerun to update UI state after crawling
        else:
            st.error("Crawling failed.")

# --- 2. Problem Selection Section ---
st.header("2. Select Problems")

if not st.session_state.data_loaded:
    st.warning(f"'{CSV_FILE}' not found. Please run the crawling step first.")
else:
    # Load data if not already loaded or if forced reload
    if st.session_state.df is None:
        try:
            df = pd.read_csv(CSV_FILE, skipinitialspace=True)
            df.columns = df.columns.str.strip()
            # Basic cleaning - adjust as needed based on actual crawl output
            if "ac-rate" in df.columns:
                df["ac-rate"] = (
                    df["ac-rate"]
                    .astype(str)
                    .str.strip()
                    .str.replace(",", ".")
                    .str.rstrip("%")
                )
                # Handle potential non-numeric values before converting to float
                df["ac-rate"] = pd.to_numeric(
                    df["ac-rate"], errors="coerce"
                )  # Coerce errors will turn invalid values into NaN
            if "category" in df.columns:
                df["category"] = df["category"].str.strip()
            if "problem-code" in df.columns:
                df["problem-code"] = df["problem-code"].str.strip()
            if "solved" not in df.columns:
                st.warning(
                    (
                        "Column 'solved' not found in CSV. "
                        "Filtering by solved status disabled."
                    )
                )
                df["solved"] = -1  # Add a dummy column if missing
            if "users" not in df.columns:
                st.warning(
                    ("Column 'users' not found in CSV. " "Sorting by users disabled.")
                )
                df["users"] = 0  # Add a dummy column if missing

            st.session_state.df = df
        except Exception as e:
            st.error(f"Error loading or processing {CSV_FILE}: {e}")
            st.session_state.data_loaded = False  # Reset flag if loading fails

    if st.session_state.df is not None:
        df = st.session_state.df
        st.dataframe(df.head())  # Show preview

        categories = [
            "Any",
            "Cơ bản",
            "Nâng cao",
            "Vận dụng linh hoạt",
        ]  # Example categories
        sort_options = ["ac-rate", "users"]
        # Filter out sort options if the column doesn't exist or has issues
        if "ac-rate" not in df.columns or df["ac-rate"].isnull().all():
            if "ac-rate" in sort_options:
                sort_options.remove("ac-rate")
        if "users" not in df.columns:
            if "users" in sort_options:
                sort_options.remove("users")
        if not sort_options:
            st.warning("No valid columns available for sorting.")

        col1, col2, col3 = st.columns(3)
        with col1:
            # Assuming 1=Solved, 0=Unsolved
            solved_options = {"Unsolved": -1, "Unfinished": 0, "Solved": 1}
            # Check if 'solved' column exists and has expected values
            if "solved" in df.columns and set(df["solved"].unique()).issubset(
                {0, 1, -1, None}
            ):
                selected_solved_label = st.radio(
                    "Solved Status:", list(solved_options.keys()), index=0
                )
                filter_solved = solved_options[selected_solved_label]
            else:
                st.info("Filtering by solved status not available.")
                filter_solved = None  # Disable filter

            filter_category = st.selectbox("Category:", categories, index=0)
            if filter_category == "Any":
                filter_category = None

        with col2:
            sort_by = st.selectbox(
                "Sort By:",
                sort_options,
                index=0 if sort_options else -1,
                disabled=not sort_options,
            )
            ascending = (
                st.radio("Sort Order:", ["Ascending", "Descending"], index=0)
                == "Ascending"
            )

        with col3:
            limit = st.number_input("Limit (0 for all):", min_value=0, value=10)

        if st.button("Select Problems"):
            # Only proceed if a valid sort option is available
            if sort_by:
                try:
                    with st.spinner("Filtering and sorting problems..."):
                        # Use the imported function
                        (
                            st.session_state.selected_problems,
                            st.session_state.df,
                        ) = get_filtered_problems(
                            csv_file=CSV_FILE,
                            solved=filter_solved,
                            category=filter_category,
                            sort_by=sort_by,
                            ascending=ascending,
                            limit=limit,
                        )
                    st.success(
                        f"Selected {len(st.session_state.selected_problems)} "
                        "problems."
                    )
                    if st.session_state.selected_problems:
                        st.text("Selected Problem Codes:")
                        st.dataframe(
                            pd.DataFrame(
                                st.session_state.df,
                            )
                        )
                    else:
                        st.info("No problems matched the criteria.")
                except Exception as e:
                    st.error(f"Error during problem selection: {e}")
                    st.session_state.selected_problems = []
            else:
                st.warning("Cannot select problems without a valid sorting column.")


# --- 3. Processing Section ---
st.header("3. Process Selected Problems")

if not st.session_state.selected_problems:
    st.info("No problems selected yet. Please use the selection step above.")
else:
    st.write(
        f"Ready to process {len(st.session_state.selected_problems)} "
        "selected problems:"
    )
    st.dataframe(
        pd.DataFrame(st.session_state.selected_problems, columns=["Problem Code"])
    )

    if st.button("Start Processing"):
        with st.spinner("Processing selected problems... This may take a while."):
            st.warning(
                (
                    "Note: Currently calling main.py without passing selected "
                    "problems directly. Modify main.py to accept problem codes "
                    "as arguments or refactor its logic."
                )
            )

            # Calling without arguments for now:
            if start_process(st.session_state.selected_problems):
                st.success("Processing script finished.")
            else:
                st.error("Processing script failed.")

# Add a way to clear selection if needed
if st.session_state.selected_problems:
    if st.button("Clear Selection"):
        st.session_state.selected_problems = []
        st.rerun()

import os
import time

import pandas as pd
import streamlit as st

from conf import lqdoj_settings
from lqdoj_solver.crawl.core import LQDOJCrawler
from lqdoj_solver.utils.select_problems import get_filtered_problems


class LQDOJSolverApp:
    def __init__(self):
        self.CSV_FILE = lqdoj_settings.LQDOJ_CSV_FILE
        self.crawler = LQDOJCrawler()
        self.agent = None  # Initialize agent lazily when needed
        self.init_session_state()
        # Title is set by the main app

    def init_session_state(self):
        if "selected_problems" not in st.session_state:
            st.session_state.selected_problems = []
        if "data_loaded" not in st.session_state:
            st.session_state.data_loaded = os.path.exists(self.CSV_FILE)
        if "df" not in st.session_state:
            st.session_state.df = None

    def crawl_section(self):
        st.header("1. Crawl Problems")
        if st.button("Start Crawling"):
            with st.spinner("🏃‍♂️ Crawling problems... Please wait."):
                self.crawler.run()
                st.session_state.data_loaded = True
                st.session_state.df = None
                st.rerun()

    def load_data(self):
        try:
            df = pd.read_csv(self.CSV_FILE, skipinitialspace=True)
            df.columns = df.columns.str.strip()
            if "ac-rate" in df.columns:
                df["ac-rate"] = (
                    df["ac-rate"]
                    .astype(str)
                    .str.strip()
                    .str.replace(",", ".")
                    .str.rstrip("%")
                )
                df["ac-rate"] = pd.to_numeric(df["ac-rate"], errors="coerce")

            # LQDOJ có thể có difficulty thay vì category
            if "difficulty" in df.columns:
                df["difficulty"] = df["difficulty"].str.strip()
            elif "category" in df.columns:
                df["category"] = df["category"].str.strip()

            if "problem-code" in df.columns:
                df["problem-code"] = df["problem-code"].str.strip()
            if "solved" not in df.columns:
                st.warning(
                    "Column 'solved' not found in CSV. Filtering by solved status disabled."
                )
                df["solved"] = -1
            if "users" not in df.columns:
                st.warning(
                    "Column 'users' not found in CSV. Sorting by users disabled."
                )
                df["users"] = 0
            st.session_state.df = df
        except Exception as e:
            st.error(f"Error loading or processing {self.CSV_FILE}: {e}")
            st.session_state.data_loaded = False

    def selection_section(self):
        st.header("2. Select Problems")
        if not st.session_state.data_loaded:
            st.warning(
                f"'{self.CSV_FILE}' not found. Please run the crawling step first."
            )
            return
        if st.session_state.df is None:
            self.load_data()
        if st.session_state.df is not None:
            df = st.session_state.df
            st.dataframe(df.head())

            # LQDOJ có thể có difficulty thay vì category
            if "difficulty" in df.columns:
                difficulties = ["Any"] + list(df["difficulty"].unique())
                sort_options = ["ac-rate", "users"]
            elif "category" in df.columns:
                difficulties = ["Any"] + list(df["category"].unique())
                sort_options = ["ac-rate", "users"]
            else:
                difficulties = ["Any"]
                sort_options = []

            if "ac-rate" not in df.columns or df["ac-rate"].isnull().all():
                if "ac-rate" in sort_options:
                    sort_options.remove("ac-rate")
            if "users" not in df.columns:
                if "users" in sort_options:
                    sort_options.remove("users")
            if not sort_options:
                st.warning("No valid columns available for sorting.")
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                solved_options = {"Unsolved": -1, "Unfinished": 0, "Solved": 1}
                if "solved" in df.columns and set(df["solved"].unique()).issubset(
                    {0, 1, -1, None}
                ):
                    selected_solved_label = st.radio(
                        "Solved Status:", list(solved_options.keys()), index=0
                    )
                    filter_solved = solved_options[selected_solved_label]
                else:
                    filter_solved = -1
            with col2:
                # LQDOJ có thể dùng difficulty thay vì category
                if "difficulty" in df.columns:
                    selected_difficulty = st.selectbox("Difficulty:", difficulties)
                    filter_difficulty = (
                        None if selected_difficulty == "Any" else selected_difficulty
                    )
                elif "category" in df.columns:
                    selected_category = st.selectbox("Category:", difficulties)
                    filter_difficulty = (
                        None if selected_category == "Any" else selected_category
                    )
                else:
                    filter_difficulty = None
            with col3:
                if sort_options:
                    selected_sort = st.selectbox("Sort by:", sort_options)
                    sort_ascending = st.checkbox("Ascending", value=True)
                else:
                    selected_sort = "ac-rate"
                    sort_ascending = True
            with col4:
                limit = st.number_input("Limit (0 for all):", min_value=0, value=10)

            if st.button("Apply Filters"):
                problems, filtered_df = get_filtered_problems(
                    self.CSV_FILE,
                    solved=filter_solved,
                    difficulty=filter_difficulty,
                    sort_by=selected_sort,
                    ascending=sort_ascending,
                    limit=limit,
                )
                st.session_state.selected_problems = problems
                st.success(f"Found {len(problems)} problems matching your criteria.")
                st.dataframe(filtered_df)

        # Clear selection button
        if st.session_state.selected_problems:
            if st.button("Clear Selection"):
                st.session_state.selected_problems = []
                st.rerun()

    def processing_section(self):
        st.header("3. Process Selected Problems")
        if not st.session_state.selected_problems:
            st.info("No problems selected yet. Please use the selection step above.")
            return

        st.write(
            f"Ready to process {len(st.session_state.selected_problems)} selected problems:"
        )
        st.dataframe(
            pd.DataFrame(st.session_state.selected_problems, columns=["Problem Code"])
        )

        # Parallel processing options
        col1, col2 = st.columns(2)
        with col1:
            use_parallel = st.checkbox(
                "Use Parallel Processing",
                value=st.session_state.get("parallel_processing", False),
                help="Enable multi-processing for faster execution",
            )

        with col2:
            if use_parallel:
                max_workers = st.slider(
                    "Number of Workers",
                    min_value=1,
                    max_value=4,
                    value=st.session_state.get("max_workers", 2),
                    help="Number of parallel processes",
                )
            else:
                max_workers = 1

        if st.button("Start Processing"):
            with st.spinner("Processing selected problems... This may take a while."):
                try:
                    if use_parallel and max_workers > 1:
                        # Use parallel processing
                        from lqdoj_solver.agent.tools import run_parallel_processing

                        st.info(
                            f"🚀 Starting parallel processing with {max_workers} workers..."
                        )
                        start_time = time.time()

                        run_parallel_processing(
                            st.session_state.selected_problems, max_workers
                        )

                        end_time = time.time()
                        st.success(
                            f"✅ Parallel processing completed in {end_time - start_time:.2f} seconds!"
                        )
                    else:
                        # Use sequential processing
                        if self.agent is None:
                            from lqdoj_solver.agent.tools import LQDOJAgent

                            self.agent = LQDOJAgent()

                        if self.agent.process_problems(
                            st.session_state.selected_problems
                        ):
                            st.success("Processing script finished.")
                        else:
                            st.error("Processing script failed.")

                except Exception as e:
                    st.error(f"Error during processing: {e}")
                    st.exception(e)

    def cleanup(self):
        if self.agent and hasattr(self.agent, "driver"):
            self.agent.driver.quit()

    def run(self):
        try:
            self.crawl_section()
            self.selection_section()
            self.processing_section()
        finally:
            self.cleanup()


if __name__ == "__main__":
    app = LQDOJSolverApp()
    app.run()

import os
import time

import pandas as pd
import streamlit as st

from base_solver.shared_utils import normalize_points
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
        # Use platform-specific session state keys
        platform = "lqdoj"
        data_loaded_key = f"{platform}_data_loaded"
        df_key = f"{platform}_df"
        selected_problems_key = f"{platform}_selected_problems"

        if selected_problems_key not in st.session_state:
            st.session_state[selected_problems_key] = []
        if data_loaded_key not in st.session_state:
            st.session_state[data_loaded_key] = os.path.exists(self.CSV_FILE)
        if df_key not in st.session_state:
            st.session_state[df_key] = None

        # Set current platform's data as active
        st.session_state.selected_problems = st.session_state[selected_problems_key]
        st.session_state.data_loaded = st.session_state[data_loaded_key]
        st.session_state.df = st.session_state[df_key]

    def update_session_state(self):
        """Update platform-specific session state with current values"""
        platform = "lqdoj"
        st.session_state[f"{platform}_data_loaded"] = st.session_state.data_loaded
        st.session_state[f"{platform}_df"] = st.session_state.df
        st.session_state[
            f"{platform}_selected_problems"
        ] = st.session_state.selected_problems

    def crawl_section(self):
        st.header("1. Crawl Problems")

        # Add status indicator
        csv_exists = os.path.exists(self.CSV_FILE)
        if csv_exists:
            st.success(f"✅ CSV file found: {self.CSV_FILE}")
            # Show file info
            file_size = os.path.getsize(self.CSV_FILE) / 1024  # KB
            st.info(f"📁 File size: {file_size:.1f} KB")
        else:
            st.warning(f"⚠️ CSV file not found: {self.CSV_FILE}")

        if st.button("Start Crawling"):
            with st.spinner("🏃‍♂️ Crawling problems... Please wait."):
                # Add progress bar
                progress_bar = st.progress(0)
                status_text = st.empty()

                try:
                    self.crawler.run()
                    progress_bar.progress(100)
                    status_text.text("✅ Crawling completed!")

                    st.session_state.data_loaded = True
                    st.session_state.df = None
                    self.update_session_state()
                    st.success("🎉 Problems crawled successfully!")
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Crawling failed: {e}")
                    progress_bar.empty()
                    status_text.empty()

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
            self.update_session_state()
        except Exception as e:
            st.error(f"Error loading or processing {self.CSV_FILE}: {e}")
            st.session_state.data_loaded = False
            self.update_session_state()

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

            # Add data overview
            st.subheader("📊 Data Overview")
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total Problems", len(df))
            with col2:
                if "solved" in df.columns:
                    solved_count = len(df[df["solved"] == 1])
                    st.metric("Solved", solved_count)
            with col3:
                if "difficulty" in df.columns:
                    unique_difficulties = df["difficulty"].nunique()
                    st.metric("Difficulties", unique_difficulties)
                elif "category" in df.columns:
                    unique_categories = df["category"].nunique()
                    st.metric("Categories", unique_categories)
            with col4:
                if "ac-rate" in df.columns:
                    avg_ac_rate = df["ac-rate"].mean()
                    st.metric("Avg AC Rate", f"{avg_ac_rate:.1f}%")

            # Show sample data
            with st.expander("📋 Sample Data (click to expand)"):
                st.dataframe(df.head(10), use_container_width=True)

            st.subheader("🔍 Filter & Select Problems")

            # Optional database-backed selection as alternative UI in expander
            try:
                from app import (
                    MultiPlatformSolverApp as _AppShim,  # local import to avoid cycles
                )

                _AppShim().database_selection_section("lqdoj", inline=True)
            except Exception:
                pass

            st.dataframe(df.head())

            # LQDOJ có thể có difficulty thay vì category
            if "difficulty" in df.columns:
                difficulties = ["Any"] + list(df["difficulty"].unique())
                sort_options = ["ac-rate", "users", "points"]
            elif "category" in df.columns:
                difficulties = ["Any"] + list(df["category"].unique())
                sort_options = ["ac-rate", "users", "points"]
            else:
                difficulties = ["Any"]
                sort_options = []

            if "ac-rate" not in df.columns or df["ac-rate"].isnull().all():
                if "ac-rate" in sort_options:
                    sort_options.remove("ac-rate")
            if "users" not in df.columns:
                if "users" in sort_options:
                    sort_options.remove("users")
            if "points" not in df.columns:
                if "points" in sort_options:
                    sort_options.remove("points")
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

            # Add filter preview
            if st.button("🔍 Preview Filters"):
                preview_problems, preview_df = get_filtered_problems(
                    self.CSV_FILE,
                    solved=filter_solved,
                    difficulty=filter_difficulty,
                    sort_by=selected_sort,
                    ascending=sort_ascending,
                    limit=limit,
                )
                st.info(f"📋 Filter preview: {len(preview_problems)} problems found")
                st.dataframe(preview_df.head(5), use_container_width=True)

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
                self.update_session_state()
                st.success(f"✅ Found {len(problems)} problems matching your criteria.")
                st.dataframe(filtered_df)

    def processing_section(self):
        st.header("3. Process Selected Problems")
        if not st.session_state.selected_problems:
            st.info("No problems selected yet. Please use the selection step above.")
            return

        # Problem management section
        st.subheader("📋 Selected Problems Management")

        # Display selected problems with better formatting
        col1, col2 = st.columns([2, 1])
        with col1:
            st.write(
                f"**Total selected:** {len(st.session_state.selected_problems)} problems"
            )
            if st.session_state.selected_problems:
                # Create a more detailed dataframe
                problems_df = pd.DataFrame(
                    {
                        "Problem Code": st.session_state.selected_problems,
                        "Status": ["Pending"] * len(st.session_state.selected_problems),
                    }
                )
                st.dataframe(problems_df, use_container_width=True)

        with col2:
            st.write("**Quick Actions:**")

            # Randomize problems
            if st.button(
                "🎲 Randomize Order", help="Shuffle the order of selected problems"
            ):
                import random

                problems = st.session_state.selected_problems.copy()
                random.shuffle(problems)
                st.session_state.selected_problems = problems
                self.update_session_state()
                st.success("Problems randomized!")
                st.rerun()

            # Remove specific problems
            if st.session_state.selected_problems:
                st.write("**Remove problems:**")
                problems_to_remove = st.multiselect(
                    "Select problems to remove:",
                    st.session_state.selected_problems,
                    help="Select problems you want to remove from the list",
                )

                if st.button("🗑️ Remove Selected", disabled=not problems_to_remove):
                    remaining_problems = [
                        p
                        for p in st.session_state.selected_problems
                        if p not in problems_to_remove
                    ]
                    st.session_state.selected_problems = remaining_problems
                    self.update_session_state()
                    st.success(f"Removed {len(problems_to_remove)} problems!")
                    st.rerun()

            # Clear all
            if st.button("❌ Clear All", help="Remove all selected problems"):
                st.session_state.selected_problems = []
                self.update_session_state()
                st.success("All problems cleared!")
                st.rerun()

        # Processing configuration
        st.subheader("⚙️ Processing Configuration")

        # Parallel processing options
        col1, col2, col3 = st.columns(3)
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

        with col3:
            # Add processing mode selection
            processing_mode = st.selectbox(
                "Processing Mode:",
                ["Normal", "Quick Test", "Full Analysis"],
                help=(
                    "Normal: Standard processing\n"
                    "Quick Test: Process first 3 problems only\n"
                    "Full Analysis: Detailed processing"
                ),
            )

        # Add statistics section
        if st.session_state.selected_problems and st.session_state.df is not None:
            st.subheader("📈 Selection Statistics")

            # Get data for selected problems
            selected_df = st.session_state.df[
                st.session_state.df["problem-code"].isin(
                    st.session_state.selected_problems
                )
            ]

            if not selected_df.empty:
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric(
                        "Selected Problems", len(st.session_state.selected_problems)
                    )
                with col2:
                    if "ac-rate" in selected_df.columns:
                        avg_ac_rate = selected_df["ac-rate"].mean()
                        st.metric("Avg AC Rate", f"{avg_ac_rate:.1f}%")
                with col3:
                    if "points" in selected_df.columns:
                        # Normalize points before calculating total
                        normalized_points = selected_df["points"].apply(
                            normalize_points
                        )
                        total_points = normalized_points.sum()
                        st.metric("Total Points", total_points)
                with col4:
                    if "solved" in selected_df.columns:
                        solved_count = len(selected_df[selected_df["solved"] == 1])
                        st.metric("Already Solved", solved_count)

                # Show detailed breakdown
                with st.expander("📊 Detailed Breakdown"):
                    st.dataframe(selected_df, use_container_width=True)

        # Apply processing mode logic
        problems_to_process = st.session_state.selected_problems.copy()
        if processing_mode == "Quick Test":
            problems_to_process = problems_to_process[:3]
            st.info("🔬 Quick Test Mode: Processing only first 3 problems")
        elif processing_mode == "Full Analysis":
            st.info("🔍 Full Analysis Mode: Detailed processing with explanations")

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

                        run_parallel_processing(problems_to_process, max_workers)

                        end_time = time.time()
                        st.success(
                            f"✅ Parallel processing completed in {end_time - start_time:.2f} seconds!"
                        )

                        # Show processing summary
                        with st.expander("📋 Processing Summary"):
                            st.write(
                                "Check the console output above for detailed processing information."
                            )
                            st.write(
                                "The system will automatically update problem status in the database."
                            )
                    else:
                        # Use sequential processing
                        if self.agent is None:
                            from lqdoj_solver.agent.tools import LQDOJAgent

                            self.agent = LQDOJAgent()

                        # Process problems and get result
                        result = self.agent.process_problems(problems_to_process)

                        if result:
                            st.success("✅ Processing completed successfully!")
                            st.info(f"📊 Processed {len(problems_to_process)} problems")

                            # Show processing summary
                            with st.expander("📋 Processing Summary"):
                                st.write(
                                    "Check the console output above for detailed processing information."
                                )
                                st.write(
                                    "The system will automatically update problem status in the database."
                                )
                        else:
                            st.warning("⚠️ Processing completed with some issues")
                            st.info("Check the console output for detailed information")

                            # Show troubleshooting tips
                            with st.expander("🔧 Troubleshooting Tips"):
                                st.write(
                                    """
                                **Common issues and solutions:**
                                1. **Connection errors**: Check your internet connection
                                2. **Browser issues**: Make sure Chrome is properly configured
                                3. **Login problems**: Verify your credentials are correct
                                4. **File access**: Ensure the system has permission to create files
                                """
                                )

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

import os

import pandas as pd
import streamlit as st

from conf.settings import DEFAULT_PLATFORM, PLATFORMS


class MultiPlatformSolverApp:
    def __init__(self):
        self.init_session_state()

    def init_session_state(self):
        if "current_platform" not in st.session_state:
            st.session_state.current_platform = DEFAULT_PLATFORM
        if "parallel_processing" not in st.session_state:
            st.session_state.parallel_processing = False
        if "max_workers" not in st.session_state:
            st.session_state.max_workers = 2

        # Initialize platform-specific session state for current platform
        self.initialize_platform_session_state(st.session_state.current_platform)

    def platform_selector(self):
        st.sidebar.header("Platform Selection")
        platform = st.sidebar.selectbox(
            "Choose Platform:",
            list(PLATFORMS.keys()),
            index=list(PLATFORMS.keys()).index(st.session_state.current_platform),
        )

        if platform != st.session_state.current_platform:
            st.session_state.current_platform = platform
            # Reset platform-specific session state
            self.reset_platform_session_state(platform)
            st.rerun()

    def reset_platform_session_state(self, platform: str):
        """Reset session state variables specific to the selected platform"""
        # Reset general variables
        st.session_state.selected_problems = []
        st.session_state.data_loaded = False
        st.session_state.df = None

        # Reset platform-specific variables
        platform_key = f"{platform}_data_loaded"
        df_key = f"{platform}_df"
        selected_problems_key = f"{platform}_selected_problems"

        # Clear platform-specific session state
        if platform_key in st.session_state:
            del st.session_state[platform_key]
        if df_key in st.session_state:
            del st.session_state[df_key]
        if selected_problems_key in st.session_state:
            del st.session_state[selected_problems_key]

        # Initialize the new platform's session state
        self.initialize_platform_session_state(platform)

    def initialize_platform_session_state(self, platform: str):
        """Initialize platform-specific session state variables"""
        # Get the CSV file path for the platform
        platform_config = PLATFORMS[platform]
        csv_file = platform_config.get("csv_file", f"{platform}_problems_data.csv")

        # Initialize platform-specific keys
        data_loaded_key = f"{platform}_data_loaded"
        df_key = f"{platform}_df"
        selected_problems_key = f"{platform}_selected_problems"

        # Set default values if not already set
        if data_loaded_key not in st.session_state:
            st.session_state[data_loaded_key] = os.path.exists(csv_file)
        if df_key not in st.session_state:
            st.session_state[df_key] = None
        if selected_problems_key not in st.session_state:
            st.session_state[selected_problems_key] = []

        # Set current platform's data as active
        st.session_state.data_loaded = st.session_state[data_loaded_key]
        st.session_state.df = st.session_state[df_key]
        st.session_state.selected_problems = st.session_state[selected_problems_key]

    def parallel_processing_settings(self):
        """Parallel processing configuration"""
        st.sidebar.header("Parallel Processing")

        # Enable/disable parallel processing
        parallel_enabled = st.sidebar.checkbox(
            "Enable Parallel Processing",
            value=st.session_state.parallel_processing,
            help="Enable multi-processing for faster problem solving",
        )

        if parallel_enabled != st.session_state.parallel_processing:
            st.session_state.parallel_processing = parallel_enabled
            st.rerun()

        # Number of workers
        if st.session_state.parallel_processing:
            max_workers = st.sidebar.slider(
                "Number of Workers",
                min_value=1,
                max_value=4,
                value=st.session_state.max_workers,
                help="Number of parallel processes (1-4 recommended)",
            )

            if max_workers != st.session_state.max_workers:
                st.session_state.max_workers = max_workers
                st.rerun()

            # Show window layout preview
            if st.sidebar.checkbox("Show Window Layout Preview"):
                try:
                    from base_solver.shared_utils import (
                        calculate_window_layout,
                        get_screen_resolution,
                    )

                    screen_width, screen_height = get_screen_resolution()
                    layouts = calculate_window_layout(
                        max_workers, screen_width, screen_height
                    )

                    st.sidebar.write("**Window Layout:**")
                    for i, (x, y, w, h) in enumerate(layouts):
                        st.sidebar.write(f"Worker {i+1}: ({x},{y}) {w}×{h}")
                except Exception as e:
                    st.sidebar.error(f"Error calculating layout: {e}")

    def _get_platform_id(self, platform_key: str) -> int:
        if platform_key == "codemath":
            return 1
        elif platform_key == "lqdoj":
            return 2
        else:
            raise ValueError(f"Unknown platform: {platform_key}")

    def database_selection_section(self, platform_key: str, inline: bool = False):
        platform_id = self._get_platform_id(platform_key)
        from database.manager import DatabaseManager

        db = DatabaseManager()

        container = (
            st.expander("Alternative: Select Problems from Database", expanded=False)
            if inline
            else st.container()
        )
        with container:
            if not inline:
                st.header("2. Select Problems (Database)")

            # Filters
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                solved_map = {"All": None, "Unsolved": -1, "Unfinished": 0, "Solved": 1}
                solved_label = st.selectbox(
                    "Solved Status",
                    list(solved_map.keys()),
                    index=0,
                    key=f"db_solved_{platform_key}",
                )
                solved_value = solved_map[solved_label]
            with col2:
                search_text = st.text_input(
                    "Search code/name contains", "", key=f"db_search_{platform_key}"
                )
            with col3:
                sort_by = st.selectbox(
                    "Sort by",
                    ["created_at", "ac_rate", "users_solved", "points"],
                    index=0,
                    key=f"db_sort_{platform_key}",
                )
            with col4:
                ascending = st.checkbox(
                    "Ascending", value=False, key=f"db_asc_{platform_key}"
                )

            limit = st.number_input(
                "Limit (0 for all)",
                min_value=0,
                value=20,
                key=f"db_limit_{platform_key}",
            )

            # Build query
            where_clauses = ["platform = :platform"]
            params = {"platform": platform_id}
            if solved_value is not None:
                where_clauses.append("solved_status = :solved_status")
                params["solved_status"] = solved_value
            if search_text:
                where_clauses.append("(problem_code LIKE :q OR problem_name LIKE :q)")
                params["q"] = f"%{search_text}%"
            where_sql = " AND ".join(where_clauses)
            order_sql = f"ORDER BY {sort_by} {'ASC' if ascending else 'DESC'}"
            limit_sql = "" if limit == 0 else "LIMIT :limit"
            if limit != 0:
                params["limit"] = int(limit)

            query = f"""
                SELECT problem_code, problem_name, category, difficulty, points, ac_rate, users_solved, solved_status, created_at
                FROM problems
                WHERE {where_sql}
                {order_sql}
                {limit_sql}
            """  # noqa: E501

            with db.get_connection() as conn:
                df = pd.read_sql_query(query, conn, params=params)

            # Fix data type issues for Streamlit display
            if not df.empty:
                # Convert difficulty column to handle empty strings and ensure proper type
                if "difficulty" in df.columns:
                    # Replace empty strings with None/null values
                    df["difficulty"] = df["difficulty"].replace("", None)
                    # Convert to numeric, coercing errors to NaN
                    df["difficulty"] = pd.to_numeric(df["difficulty"], errors="coerce")

                # Ensure other numeric columns are properly typed
                numeric_columns = ["points", "ac_rate", "users_solved", "solved_status"]
                for col in numeric_columns:
                    if col in df.columns:
                        df[col] = pd.to_numeric(df[col], errors="coerce")

            st.subheader("📊 Preview")
            st.dataframe(df, use_container_width=True)

            # Selection summary and options
            current_count = len(st.session_state.get("selected_problems", []))
            st.caption(f"Currently selected: {current_count} problems")
            shuffle_before_apply = st.checkbox(
                "Shuffle results before apply",
                value=False,
                key=f"db_shuffle_{platform_key}",
                help="Randomize the order of the problems returned from database before applying",
            )

            # Apply controls
            apply_col1, apply_col2 = st.columns([1, 1])
            with apply_col1:
                if st.button(
                    "Add to Selected (Database)",
                    key=f"db_add_{platform_key}",
                    use_container_width=True,
                ):
                    import random

                    new_codes = df["problem_code"].tolist()
                    if shuffle_before_apply:
                        random.shuffle(new_codes)
                    # Add without duplicates, preserve existing order
                    existing = st.session_state.get("selected_problems", [])
                    combined = existing + [c for c in new_codes if c not in existing]
                    st.session_state.selected_problems = combined
                    st.success(
                        f"✅ Added {len(new_codes)} problems from database (total now {len(combined)})"
                    )
            with apply_col2:
                if st.button(
                    "Replace Selected (Database)",
                    key=f"db_replace_{platform_key}",
                    use_container_width=True,
                ):
                    import random

                    new_codes = df["problem_code"].tolist()
                    if shuffle_before_apply:
                        random.shuffle(new_codes)
                    st.session_state.selected_problems = new_codes
                    st.success(
                        f"✅ Replaced selection with {len(new_codes)} problems from database"
                    )

    def run(self):
        st.set_page_config(layout="wide")
        self.platform_selector()
        self.parallel_processing_settings()
        platform_key = st.session_state.current_platform
        platform_config = PLATFORMS[platform_key]
        st.title(f"{platform_config['name']} Solver")

        # Import và chạy app tương ứng
        try:
            if platform_key == "codemath":
                from codemath_app import CodeMathSolverApp

                app = CodeMathSolverApp()
                app.crawl_section()
                # Always use original UI/UX selection from platform app
                app.selection_section()
                # Optional: add database selection as an alternative button within selection section? (kept out to preserve UI)
                app.processing_section()
            elif platform_key == "lqdoj":
                from lqdoj_app import LQDOJSolverApp

                app = LQDOJSolverApp()
                app.crawl_section()
                # Always use original UI/UX selection from platform app
                app.selection_section()
                app.processing_section()
        finally:
            # Cleanup
            if "app" in locals():
                app.cleanup()


if __name__ == "__main__":
    app = MultiPlatformSolverApp()
    app.run()

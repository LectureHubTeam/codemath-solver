import os

import pandas as pd
import streamlit as st

from codemath_solver.agent.tools import CodeMathAgent
from codemath_solver.crawl.core import CodeMathCrawler
from codemath_solver.utils.select_problems import get_filtered_problems
from conf import settings


class CodeMathSolverApp:
    def __init__(self):
        self.CSV_FILE = settings.CSV_FILE
        self.crawler = CodeMathCrawler()
        self.agent = CodeMathAgent()
        self.init_session_state()
        st.set_page_config(layout=settings.STREAMLIT.get("layout", "wide"))
        st.title(settings.STREAMLIT.get("title", "CodeMath Solver"))

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
            if "category" in df.columns:
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
            categories = ["Any", "Cơ bản", "Nâng cao", "Vận dụng linh hoạt"]
            sort_options = ["ac-rate", "users"]
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
                solved_options = {"Unsolved": -1, "Unfinished": 0, "Solved": 1}
                if "solved" in df.columns and set(df["solved"].unique()).issubset(
                    {0, 1, -1, None}
                ):
                    selected_solved_label = st.radio(
                        "Solved Status:", list(solved_options.keys()), index=0
                    )
                    filter_solved = solved_options[selected_solved_label]
                else:
                    st.info("Filtering by solved status not available.")
                    filter_solved = None
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
                if sort_by:
                    try:
                        with st.spinner("Filtering and sorting problems..."):
                            (
                                st.session_state.selected_problems,
                                st.session_state.df,
                            ) = get_filtered_problems(
                                csv_file=self.CSV_FILE,
                                solved=filter_solved,
                                category=filter_category,
                                sort_by=sort_by,
                                ascending=ascending,
                                limit=limit,
                            )
                        st.success(
                            f"Selected {len(st.session_state.selected_problems)} problems."
                        )
                        if st.session_state.selected_problems:
                            st.text("Selected Problem Codes:")
                            st.dataframe(pd.DataFrame(st.session_state.df))
                        else:
                            st.info("No problems matched the criteria.")
                    except Exception as e:
                        st.error(f"Error during problem selection: {e}")
                        st.session_state.selected_problems = []
                else:
                    st.warning("Cannot select problems without a valid sorting column.")

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
        if st.button("Start Processing"):
            with st.spinner("Processing selected problems... This may take a while."):
                if self.agent.process_problems(st.session_state.selected_problems):
                    st.success("Processing script finished.")
                else:
                    st.error("Processing script failed.")
        if st.session_state.selected_problems:
            if st.button("Clear Selection"):
                st.session_state.selected_problems = []
                st.rerun()

    def run(self):
        self.crawl_section()
        self.selection_section()
        self.processing_section()


if __name__ == "__main__":
    app = CodeMathSolverApp()
    app.run()

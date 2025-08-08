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

    def platform_selector(self):
        st.sidebar.header("Platform Selection")
        platform = st.sidebar.selectbox(
            "Choose Platform:",
            list(PLATFORMS.keys()),
            index=list(PLATFORMS.keys()).index(st.session_state.current_platform),
        )

        if platform != st.session_state.current_platform:
            st.session_state.current_platform = platform
            st.session_state.selected_problems = []
            st.session_state.data_loaded = False
            st.session_state.df = None
            st.rerun()

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

    def run(self):
        st.set_page_config(layout="wide")
        self.platform_selector()
        self.parallel_processing_settings()

        platform_config = PLATFORMS[st.session_state.current_platform]
        st.title(f"{platform_config['name']} Solver")

        # Import và chạy app tương ứng
        try:
            if st.session_state.current_platform == "codemath":
                from codemath_app import CodeMathSolverApp

                app = CodeMathSolverApp()
                app.crawl_section()
                app.selection_section()
                app.processing_section()
            elif st.session_state.current_platform == "lqdoj":
                from lqdoj_app import LQDOJSolverApp

                app = LQDOJSolverApp()
                app.crawl_section()
                app.selection_section()
                app.processing_section()
        finally:
            # Cleanup
            if "app" in locals():
                app.cleanup()


if __name__ == "__main__":
    app = MultiPlatformSolverApp()
    app.run()

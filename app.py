import streamlit as st

from conf.settings import DEFAULT_PLATFORM, PLATFORMS


class MultiPlatformSolverApp:
    def __init__(self):
        self.init_session_state()

    def init_session_state(self):
        if "current_platform" not in st.session_state:
            st.session_state.current_platform = DEFAULT_PLATFORM

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

    def run(self):
        st.set_page_config(layout="wide")
        self.platform_selector()

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

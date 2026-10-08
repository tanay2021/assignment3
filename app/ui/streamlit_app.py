"""Minimal Streamlit entry point (placeholder, not the final UI).

Run with: streamlit run app/ui/streamlit_app.py
Streamlit is imported only inside ``main`` so this module imports cleanly in
environments without it. All logic lives in services; this file only displays.
"""

from __future__ import annotations

from app.bootstrap import ApplicationContext, initialize_application

#: The intended user flow. Each stage becomes a screen in a later prompt.
WORKFLOW_STAGES = (
    "Loan Package",
    "Documents",
    "Intelligence",
    "Policy Assistant",
    "Underwriting Summary",
)


def main() -> None:
    try:
        import streamlit as st
    except ImportError as exc:  # pragma: no cover - depends on the environment
        raise SystemExit(
            "Streamlit is not installed. It is added with the UI work; see docs/implementation_roadmap.md."
        ) from exc

    st.set_page_config(page_title="Intelligent Loan Underwriting Assistant")

    if "context" not in st.session_state:
        st.session_state["context"] = initialize_application()
    context: ApplicationContext = st.session_state["context"]

    st.title("Intelligent Loan Underwriting Assistant")
    st.caption("AI-assisted. The underwriter makes the final decision.")
    st.write("Foundation ready. Screens for each stage arrive in later development stages:")
    for stage in WORKFLOW_STAGES:
        st.write(f"- {stage}")
    st.caption(f"Environment: {context.settings.app_env}")


if __name__ == "__main__":  # pragma: no cover
    main()

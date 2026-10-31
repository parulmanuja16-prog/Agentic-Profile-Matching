"""Streamlit chat interface for the resume-matching agent."""

import streamlit as st

from agents.matching_agent import run_agent
from tools.rag_tools import count_resumes


def _start_conversation():
    """Create empty UI history and agent state for a new conversation."""
    st.session_state.chat_history = []
    st.session_state.agent_state = None


def _show_sidebar():
    """Show resume count, example questions, and a reset button."""
    with st.sidebar:
        st.header("Resume collection")
        st.metric("Supported resumes", count_resumes())
        st.caption("PDF, TXT, and DOCX files in `data/resumes/`.")
        st.divider()
        st.subheader("Try asking")
        st.markdown(
            "- Find React candidates with 3+ years experience\n"
            "- Compare the top 3 matches\n"
            "- Why did Alice rank higher than Bob?\n"
            "- Prioritize Python\n"
            "- Create screening questions\n"
            "- Run deep analysis\n"
            "- Give final hire/no-hire recommendations"
        )
        if st.button("Start a new conversation", use_container_width=True):
            _start_conversation()
            st.rerun()


def _show_chat_history():
    """Render saved user and assistant messages in chronological order."""
    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])


def _process_user_message(message):
    """Run one user turn and save the agent response for the chat display."""
    st.session_state.chat_history.append(
        {"role": "user", "content": message}
    )
    with st.chat_message("user"):
        st.markdown(message)

    with st.chat_message("assistant"):
        with st.spinner("Searching resumes and preparing a response..."):
            result = run_agent(message, st.session_state.agent_state)
        st.markdown(result["final_report"])

    st.session_state.agent_state = result
    st.session_state.chat_history.append(
        {"role": "assistant", "content": result["final_report"]}
    )


def main():
    """Display the chat interface and handle submitted messages."""
    st.set_page_config(
        page_title="Agentic Profile Matching",
        page_icon="👥",
        layout="wide",
    )
    st.title("Agentic Profile Matching")
    st.write(
        "Search resumes, refine the criteria, compare candidates, "
        "and review explainable screening reports."
    )

    if "chat_history" not in st.session_state:
        _start_conversation()

    _show_sidebar()
    _show_chat_history()

    prompt = st.chat_input(
        "Describe the role or ask a follow-up about the current shortlist"
    )
    if prompt:
        _process_user_message(prompt.strip())


if __name__ == "__main__":
    main()

import streamlit as st
from typing import List, Dict
from services.ai_service_alt import AIService
from services.plan_service import PlanService


def display_chat_page(username: str, plan_service: PlanService, ai_service: AIService):
    """Display a simple chat interface using Streamlit."""
    st.subheader("\U0001F4AC Chat")

    # Ensure conversation history exists for this user
    if "conversations" not in st.session_state:
        st.session_state.conversations = {}
    if username not in st.session_state.conversations:
        st.session_state.conversations[username] = []

    messages: List[Dict[str, str]] = st.session_state.conversations[username]

    # Show previous messages
    for msg in messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # Input box for the next user message
    prompt = st.chat_input("Type your message")
    if prompt:
        messages.append({"role": "user", "content": prompt})

        # Build context from latest plan and journal summary
        journal_summary = plan_service.get_journal_summary(username)
        latest_plan = plan_service.get_latest_plan(username)
        plan_text = latest_plan.plan if latest_plan else "No plan available."
        context = f"Latest Plan:\n{plan_text}\n\nRecent Journal Summary:\n{journal_summary}"

        try:
            reply = ai_service.chat_with_user(messages, context)
            messages.append({"role": "assistant", "content": reply})
        except Exception as e:
            st.error(f"Chat error: {e}")

        st.rerun()

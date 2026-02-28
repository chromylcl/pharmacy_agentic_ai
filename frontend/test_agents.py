"""
test_agent_display.py
----------------------
Standalone test for components/agent_display.py
Run with: streamlit run test_agent_display.py
Place in frontend/ root folder. Delete after testing.
"""

import streamlit as st
import sys, os
sys.path.insert(0, os.path.dirname(__file__))

from components.agent_display import run_all_agents

st.set_page_config(
    page_title="Agent Display Test — Atharva",
    page_icon="🤖",
    layout="centered",
)

# Minimal session state setup
if "consultation_summary" not in st.session_state:
    st.session_state.consultation_summary = []

st.title("🧪 agent_display.py — Component Test")
st.caption("No backend needed. All agent responses are mocked.")
st.divider()

user_input = st.text_input(
    "Simulate a user message:",
    value="I have a headache and mild fever. What can I take?",
)

if st.button("▶️ Run All Agents"):
    st.markdown("---")
    agent_logs = run_all_agents(user_input)

    st.divider()
    st.success(f"✅ All agents done. {len(agent_logs)} logs collected.")

    st.subheader("Returned agent_logs (what gets stored in messages):")
    for log in agent_logs:
        st.markdown(f"**{log['agent']}**")
        st.code(log["log"])

    st.subheader("consultation_summary (what goes into the PDF receipt):")
    st.json(st.session_state.consultation_summary)
"""
test_langfuse.py
-----------------
Standalone test for services/langfuse_client.py
Run with: streamlit run test_langfuse.py
Place in frontend/ root. Delete after testing.

What this tests:
- Langfuse connection using your .env keys
- start_trace() creates a real trace
- log_span() logs 3 agent spans
- end_trace() flushes to dashboard

After running, go to https://cloud.langfuse.com and check
Traces — you should see a new entry called "pharmacy-assistant-interaction"
with 3 nested spans inside it.
"""

import streamlit as st
import time
import sys, os
sys.path.insert(0, os.path.dirname(__file__))

from services.langfuse_client import start_trace, log_span, end_trace

st.set_page_config(
    page_title="Langfuse Test — Atharva",
    page_icon="📡",
    layout="centered",
)

st.title("📡 langfuse_client.py — Connection Test")
st.caption("Tests your Langfuse keys and sends a real trace to the dashboard.")
st.divider()

# Show key status
public_key = os.getenv("LANGFUSE_PUBLIC_KEY", "NOT SET")
secret_key = os.getenv("LANGFUSE_SECRET_KEY", "NOT SET")

st.markdown("**Environment variables:**")
st.markdown(f"- `LANGFUSE_PUBLIC_KEY`: `{public_key[:12]}...`" if public_key != "NOT SET" else "- ❌ LANGFUSE_PUBLIC_KEY not set")
st.markdown(f"- `LANGFUSE_SECRET_KEY`: `{secret_key[:12]}...`" if secret_key != "NOT SET" else "- ❌ LANGFUSE_SECRET_KEY not set")

st.divider()

user_input = st.text_input(
    "Test message to trace:",
    value="I have a headache and mild fever. What can I take?",
)

if st.button("🚀 Send Test Trace to Langfuse", use_container_width=True):

    with st.status("Sending trace to Langfuse...", expanded=True) as status:

        # Step 1 — start trace
        st.write("Starting trace...")
        trace = start_trace(user_input, patient_name="Test Patient")
        st.write("✅ Trace started")

        # Step 2 — log 3 agent spans
        agents = [
            ("🩺 Pharmacist Agent",         "Paracetamol 500mg recommended. OTC available."),
            ("🛡️ Safety & Compliance Agent", "No interactions detected. Safe at standard dose."),
            ("📦 Fulfillment Agent",         "In stock. PDC score N/A. 3-day supply available."),
        ]

        for agent_name, dummy_output in agents:
            st.write(f"Logging span: {agent_name}...")
            start = time.time()
            time.sleep(0.3)   # simulate latency
            latency = time.time() - start
            log_span(trace, agent_name, user_input, dummy_output, latency)
            st.write(f"✅ Span logged for {agent_name} ({round(latency, 2)}s)")

        # Step 3 — end trace
        st.write("Flushing trace to dashboard...")
        end_trace(trace, final_response="Based on your symptoms, paracetamol 500mg is recommended.")
        st.write("✅ Trace flushed")

        status.update(label="✅ All done!", state="complete", expanded=False)

    st.success("Trace sent! Go to https://cloud.langfuse.com → Traces to verify.")
    st.info("Look for a trace called **pharmacy-assistant-interaction** with 3 nested spans.")
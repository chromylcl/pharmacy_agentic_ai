import streamlit as st
import uuid
def init_session():

    
    """Initializes all global state variables exactly once per session."""
    
    # 1. User & UI State
    
        
    if "ui_phase" not in st.session_state:
        st.session_state.ui_phase = "onboarding"

    if "patient_name" not in st.session_state:
        st.session_state.patient_name = "Guest"

    if "patient_age" not in st.session_state:
        st.session_state.patient_age = None              # ← ADD THIS LINE

    if "cart" not in st.session_state:
        st.session_state.cart = []   
        
    if "payment_link" not in st.session_state:
        st.session_state.payment_link = None                    # ← ADD THIS LINE (needed for storefront later)


        
    if "is_first_message" not in st.session_state:
        st.session_state.is_first_message = True
    # 2. Chat Memory
    if "messages" not in st.session_state:
        st.session_state.messages = [
            # Pre-load a friendly greeting from the assistant
            {"role": "assistant", "content": "Hi! I'm Pharmacy Assistant, your AI Pharmacy Assistant. How can I help you today?"}
        ]
    # 3. Workflow Memory (For restricted drugs & uploads)
    if "pending_prescription" not in st.session_state:
        st.session_state.pending_prescription = None
    # 4. Observability (Langfuse)
    if "langfuse_trace_id" not in st.session_state:
        # Generates a unique ID ONCE so the whole session links to a single trace tree
        st.session_state.langfuse_trace_id = str(uuid.uuid4())
    # 5. Data Collection for the PDF Receipt
    if "consultation_summary" not in st.session_state:
        st.session_state.consultation_summary = []

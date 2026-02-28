# components/onboarding.py
# AI Pharmacy Assistant — Patient Onboarding Gate
# REBUILT: Simple, clean, only verified-safe Streamlit CSS
# NO BACKEND CALLS — pure session state management.

import streamlit as st


def render_onboarding():

    st.markdown("""
        <style>
        header[data-testid="stHeader"]   { display: none !important; }
        section[data-testid="stSidebar"] { display: none !important; }
        footer                           { display: none !important; }
        .block-container {
            max-width: 460px !important;
            margin: 0 auto !important;
            padding-top: 3rem !important;
        }
        div[data-testid="stFormSubmitButton"] > button {
            width: 100% !important;
            background: linear-gradient(135deg, #7C3AED, #5B21B6) !important;
            color: white !important;
            border: none !important;
            border-radius: 12px !important;
            padding: 0.7rem !important;
            font-size: 0.95rem !important;
            font-weight: 700 !important;
            margin-top: 0.5rem !important;
            box-shadow: 0 4px 20px rgba(124,58,237,0.4) !important;
        }
        div[data-testid="stFormSubmitButton"] > button:hover {
            box-shadow: 0 6px 28px rgba(124,58,237,0.6) !important;
        }
        </style>
    """, unsafe_allow_html=True)

    # ── LOGO + TITLE (inline styles only — safe) ───────────────────────────────
    st.markdown("""
        <div style="text-align:center; padding: 1rem 0 1.5rem 0;">
            <div style="font-size:3rem; margin-bottom:0.8rem;">💊</div>
            <h2 style="color:#a78bfa; font-weight:700; margin:0 0 0.3rem 0; font-size:1.7rem;">
                AI Pharmacy Assistant
            </h2>
            <p style="color:#6b7280; font-size:0.85rem; margin:0;">
                Intelligent · Safe · Personalised
            </p>
            <div style="width:50px; height:2px; background:#7C3AED;
                        margin:0.8rem auto 0; border-radius:2px; opacity:0.7;">
            </div>
        </div>
    """, unsafe_allow_html=True)

    # ── FORM ───────────────────────────────────────────────────────────────────
    with st.form("onboarding_form", clear_on_submit=False):

        st.markdown(
            "<p style='color:#6b7280; font-size:0.83rem; text-align:center; margin:0 0 1.2rem 0;'>"
            "Enter your details for safe, personalised recommendations"
            "</p>",
            unsafe_allow_html=True
        )

        col1, col2 = st.columns(2)
        with col1:
            first_name = st.text_input("First Name", placeholder="Sarah", max_chars=50)
        with col2:
            last_name = st.text_input("Last Name", placeholder="Connor", max_chars=50)

        age = st.number_input(
            "Your Age",
            min_value=1, max_value=120,
            value=None, step=1,
            placeholder="e.g. 28",
            help="Used to calculate safe dosage thresholds."
        )

        # Age-aware banners
        if age is not None:
            if age < 18:
                st.info("👶 Pediatric mode — dosage recommendations will be adjusted. Please consult a guardian.", icon="⚠️")
            elif age >= 65:
                st.info("🧓 Senior mode — enhanced drug interaction screening will be applied.", icon="ℹ️")

        st.markdown("<div style='height:0.2rem'></div>", unsafe_allow_html=True)

        agreed = st.checkbox(
            "I understand this is an AI assistant — not a substitute for professional medical advice."
        )

        submitted = st.form_submit_button("Enter the Pharmacy →")

    # ── VALIDATION ─────────────────────────────────────────────────────────────
    if submitted:
        errors = []
        if not first_name.strip():    errors.append("First name is required.")
        if not last_name.strip():     errors.append("Last name is required.")
        if age is None:               errors.append("Age is required.")
        if age and not (1<=age<=120): errors.append("Age must be between 1 and 120.")
        if not agreed:                errors.append("Please acknowledge the advisory notice.")

        if errors:
            for err in errors:
                st.error(err)
        else:
            st.session_state.patient_name = f"{first_name.strip()} {last_name.strip()}"
            st.session_state.patient_age  = int(age)
            st.session_state.ui_phase     = "chatting"
            _update_greeting_message(st.session_state.patient_name, int(age))
            st.rerun()


def _update_greeting_message(name: str, age: int) -> None:
    """
    Personalises messages[0] with patient name + age note.
    # SWAP THIS — currently session state only
    # When /patient/register is live:
    #   from services.api_client import register_patient
    #   register_patient(name, age)
    """
    age_note = ""
    if age < 18:
        age_note = " I'll ensure all recommendations are safe for your age."
    elif age >= 65:
        age_note = " I'll apply enhanced drug interaction screening for older adults."

    personalised_greeting = (
        f"Hello {name}! 👋 Welcome to AI Pharmacy Assistant.\n\n"
        f"I'm here to help you with medication queries, drug safety checks, "
        f"and finding the right OTC products.{age_note}\n\n"
        f"What can I help you with today?"
    )

    if st.session_state.messages:
        st.session_state.messages[0] = {
            "role": "assistant",
            "content": personalised_greeting
        }
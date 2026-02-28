"""
components/receipt.py
----------------------
Renders the consultation receipt at the end of every session.
Shows a summary of all agent findings and provides a PDF download button.

Rules:
    - Reads from st.session_state.consultation_summary only
    - No API calls
    - No session_state writes

Usage in app.py:
    from components.receipt import render_receipt
    render_receipt()
"""

import io
import time
import streamlit as st
from datetime import datetime

# 🔌 SWAP THIS — PDF generation uses fpdf2 (pure Python, no backend needed).
# Install it: pip install fpdf2
# Add to requirements.txt: fpdf2
# This never needs a backend swap — PDF is always generated client-side.
try:
    from fpdf import FPDF
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False


# ══════════════════════════════════════════════════════════════════════════════
# 📄 PDF GENERATOR
# ══════════════════════════════════════════════════════════════════════════════
def _sanitize_for_pdf(text: str) -> str:
    """Quick fix to replace Unicode characters that crash FPDF."""
    if not text:
        return ""
        
    replacements = {
        "–": "-",   # en-dash
        "—": "--",  # em-dash
        "‘": "'",   # smart single quotes
        "’": "'",
        "“": '"',   # smart double quotes
        "”": '"',
        "•": "*",   # bullet points
        "…": "...", # ellipsis
    }
    
    for bad_char, good_char in replacements.items():
        text = text.replace(bad_char, good_char)
        
    # Brutal fallback: force it to ascii, replacing anything else weird with '?'
    return text.encode('ascii', 'replace').decode('ascii')


def _generate_pdf(
    patient_name: str,
    summary: list,
    messages: list,
) -> bytes | None:
    """
    Generates a PDF consultation receipt.
    Returns PDF as bytes, or None if fpdf2 is not installed.

    Args:
        patient_name: from st.session_state.patient_name
        summary:      from st.session_state.consultation_summary
        messages:     from st.session_state.messages

    # 🔌 SWAP THIS — currently generates PDF entirely on the frontend.
    # If your backend later exposes a PDF generation endpoint:
    #   from services.api_client import generate_receipt_pdf
    #   return generate_receipt_pdf(patient_name, summary, messages)
    # For now, frontend generation is fine and preferred (no backend dependency).
    """
    if not PDF_AVAILABLE:
        return None

    pdf = FPDF()
    pdf.add_page()
    pdf.set_margins(15, 15, 15)

    # ── Header ────────────────────────────────────────────────────────────────
    pdf.set_font("Helvetica", "B", 20)
    pdf.set_text_color(124, 58, 237)   # purple
    pdf.cell(0, 12, "Atharva Pharmacy Assistant", ln=True, align="C")

    pdf.set_font("Helvetica", "", 11)
    pdf.set_text_color(100, 100, 100)
    pdf.cell(0, 7, "AI-Powered Consultation Receipt", ln=True, align="C")
    pdf.ln(4)

    # ── Divider ───────────────────────────────────────────────────────────────
    pdf.set_draw_color(124, 58, 237)
    pdf.set_line_width(0.5)
    pdf.line(15, pdf.get_y(), 195, pdf.get_y())
    pdf.ln(6)

    # ── Patient & session info ────────────────────────────────────────────────
    pdf.set_font("Helvetica", "B", 11)
    pdf.set_text_color(30, 30, 30)
    pdf.cell(0, 7, "Patient Information", ln=True)
    pdf.set_font("Helvetica", "", 10)
    pdf.set_text_color(60, 60, 60)
    pdf.cell(0, 6, f"Patient Name : {patient_name}", ln=True)
    pdf.cell(0, 6, f"Date         : {datetime.now().strftime('%B %d, %Y')}", ln=True)
    pdf.cell(0, 6, f"Time         : {datetime.now().strftime('%I:%M %p')}", ln=True)
    pdf.ln(4)

    # ── Agent findings ────────────────────────────────────────────────────────
    if summary:
        pdf.set_font("Helvetica", "B", 11)
        pdf.set_text_color(30, 30, 30)
        pdf.cell(0, 7, "Agent Findings", ln=True)
        pdf.set_line_width(0.3)
        pdf.line(15, pdf.get_y(), 195, pdf.get_y())
        pdf.ln(3)

        for entry in summary:
            # Agent label
            pdf.set_font("Helvetica", "B", 10)
            pdf.set_text_color(124, 58, 237)
            raw_agent = entry.get('agent', 'Agent')
            clean_agent = raw_agent.replace('🩺', '').replace('🛡️', '').replace('📦', '').strip()
            pdf.cell(0, 6, f"{clean_agent}  [{entry.get('timestamp', '')}]", ln=True)

            # Finding text — handle long lines
            pdf.set_font("Helvetica", "", 9)
            pdf.set_text_color(60, 60, 60)
            finding = entry.get("finding", "No finding recorded.")
            # fpdf2 multi_cell handles word wrap
            clean_finding = _sanitize_for_pdf(finding)
            pdf.multi_cell(0, 5, clean_finding)
            pdf.ln(3)

    # ── Conversation summary ──────────────────────────────────────────────────
    user_messages = [m for m in messages if m.get("role") == "user"]
    if user_messages:
        pdf.set_font("Helvetica", "B", 11)
        pdf.set_text_color(30, 30, 30)
        pdf.cell(0, 7, "Questions Asked", ln=True)
        pdf.set_line_width(0.3)
        pdf.line(15, pdf.get_y(), 195, pdf.get_y())
        pdf.ln(3)

        pdf.set_font("Helvetica", "", 9)
        pdf.set_text_color(60, 60, 60)
        for i, msg in enumerate(user_messages, 1):
            pdf.multi_cell(0, 5, f"{i}. {msg.get('content', '')}")
            pdf.ln(1)

    # ── Footer ────────────────────────────────────────────────────────────────
    pdf.ln(6)
    pdf.set_draw_color(200, 200, 200)
    pdf.set_line_width(0.3)
    pdf.line(15, pdf.get_y(), 195, pdf.get_y())
    pdf.ln(4)
    pdf.set_font("Helvetica", "I", 8)
    pdf.set_text_color(150, 150, 150)
    pdf.multi_cell(
        0, 5,
        "This receipt is generated by Atharva AI Pharmacy Assistant. "
        "It is not a substitute for professional medical advice. "
        "Always consult a licensed healthcare provider before taking any medication.",
        align="C"
    )

    return bytes(pdf.output())


# ══════════════════════════════════════════════════════════════════════════════
# 🚀 MAIN PUBLIC FUNCTION
# ══════════════════════════════════════════════════════════════════════════════

def render_receipt() -> None:
    """
    Renders the consultation receipt UI with a PDF download button.
    Only shows if there are agent findings in consultation_summary.

    Reads:
        st.session_state.consultation_summary
        st.session_state.messages
        st.session_state.patient_name

    Usage in app.py:
        from components.receipt import render_receipt
        render_receipt()
    """
    summary      = st.session_state.get("consultation_summary", [])
    messages     = st.session_state.get("messages", [])
    patient_name = st.session_state.get("patient_name", "Guest Patient")

    # Only show after at least one agent has run
    if not summary:
        return

    st.markdown("<div style='margin-top: 24px;'></div>", unsafe_allow_html=True)
    st.markdown(
        "<p style='font-size:0.75rem; color:#6B7280;'>CONSULTATION RECEIPT</p>",
        unsafe_allow_html=True,
    )

    with st.expander("📋 View & Download Consultation Receipt", expanded=False):

        # ── Receipt preview ───────────────────────────────────────────────────
        st.markdown(
            f"""
            <div style="
                background: #1a0a2e;
                border: 1px solid #2d1a4e;
                border-radius: 10px;
                padding: 16px 20px;
                margin-bottom: 16px;
            ">
                <div style="
                    font-size: 1rem;
                    font-weight: 700;
                    color: #7C3AED;
                    margin-bottom: 2px;
                ">💊 Atharva Pharmacy Assistant</div>
                <div style="font-size: 0.75rem; color: #6B7280; margin-bottom: 12px;">
                    Consultation Receipt
                </div>
                <div style="font-size: 0.82rem; color: #94a3b8; line-height: 1.8;">
                    👤 Patient &nbsp;: <span style="color:#e2e8f0;">{patient_name}</span><br>
                    📅 Date &nbsp;&nbsp;&nbsp;&nbsp;: <span style="color:#e2e8f0;">
                        {datetime.now().strftime("%B %d, %Y")}
                    </span><br>
                    🕐 Time &nbsp;&nbsp;&nbsp;&nbsp;: <span style="color:#e2e8f0;">
                        {datetime.now().strftime("%I:%M %p")}
                    </span>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # ── Agent findings preview ────────────────────────────────────────────
        for entry in summary:
            agent     = entry.get("agent", "Agent")
            finding   = entry.get("finding", "")
            timestamp = entry.get("timestamp", "")

            # Pick colour based on agent name
            if "Pharmacist" in agent:
                color = "#7C3AED"
            elif "Safety" in agent:
                color = "#DC2626"
            elif "Fulfillment" in agent:
                color = "#059669"
            else:
                color = "#6B7280"

            st.markdown(
                f"""
                <div style="
                    border-left: 3px solid {color};
                    padding: 8px 14px;
                    margin-bottom: 10px;
                    background: #0a0a1a;
                    border-radius: 0 6px 6px 0;
                ">
                    <div style="
                        font-size: 0.78rem;
                        color: {color};
                        font-weight: 600;
                        margin-bottom: 4px;
                    ">{agent} &nbsp;·&nbsp; {timestamp}</div>
                    <div style="
                        font-size: 0.80rem;
                        color: #94a3b8;
                        white-space: pre-wrap;
                        line-height: 1.6;
                    ">{finding}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        st.markdown("<div style='margin-top: 8px;'></div>", unsafe_allow_html=True)

        # ── PDF download button ───────────────────────────────────────────────
        if PDF_AVAILABLE:
            pdf_bytes = _generate_pdf(patient_name, summary, messages)
            if pdf_bytes:
                filename = f"atharva_receipt_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
                st.download_button(
                    label     = "⬇️ Download PDF Receipt",
                    data      = pdf_bytes,
                    file_name = filename,
                    mime      = "application/pdf",
                    use_container_width=True,
                )
        else:
            # ⚠️ DEMO SAFETY: if fpdf2 not installed, show install instruction
            st.warning(
                "PDF download unavailable. Run: `pip install fpdf2` then restart."
            )
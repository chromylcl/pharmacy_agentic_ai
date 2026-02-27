"""
components/prescription_upload.py
-----------------------------------
Renders the prescription upload gate screen.
Shown when a restricted drug is detected — blocks chat until
a prescription file is uploaded and verified.

Rules:
    - Writes to st.session_state.ui_phase only (to return to chat)
    - No direct agent calls
    - File verification is currently a dummy check — swap point marked below

Usage in app.py:
    from components.prescription_upload import render_prescription_upload
    if st.session_state.ui_phase == "prescription_upload":
        render_prescription_upload()
        st.stop()
"""

import streamlit as st
import time


def render_prescription_upload() -> None:
    """
    Renders the full prescription upload gate UI.
    Blocks the chat flow until a file is uploaded and accepted.

    Reads:
        st.session_state.pending_prescription  → drug name to display
    Writes:
        st.session_state.ui_phase              → sets back to "chatting" on success
    """

    drug_name = st.session_state.get("pending_prescription", "this medication")

    # ── Header ────────────────────────────────────────────────────────────────
    st.markdown(
        f"""
        <div style="
            background: linear-gradient(135deg, #1a0a2e, #2d1a4e);
            border: 1px solid #7C3AED;
            border-radius: 12px;
            padding: 24px;
            text-align: center;
            margin-bottom: 24px;
            box-shadow: 0 4px 24px rgba(124,58,237,0.25);
        ">
            <div style="font-size: 2.5rem;">📋</div>
            <div style="
                font-size: 1.3rem;
                font-weight: 700;
                color: #ffffff;
                margin: 10px 0 6px 0;
            ">Prescription Required</div>
            <div style="
                font-size: 0.88rem;
                color: #a78bfa;
            ">
                <strong style="color:#ffffff;">{drug_name.title()}</strong>
                is a restricted medication that requires a valid prescription.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ── Instructions ─────────────────────────────────────────────────────────
    st.markdown(
        """
        <div style="
            background: #1a0a2e;
            border-left: 3px solid #7C3AED;
            border-radius: 0 8px 8px 0;
            padding: 12px 16px;
            margin-bottom: 20px;
            font-size: 0.83rem;
            line-height: 1.8;
            color: #94a3b8;
        ">
            <strong style="color:#e2e8f0;">Accepted documents:</strong><br>
            • Doctor's prescription (PDF or image)<br>
            • Hospital discharge letter mentioning the medication<br>
            • Pharmacy refill authorization
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ── File uploader ─────────────────────────────────────────────────────────
    uploaded_file = st.file_uploader(
        label="Upload your prescription",
        type=["pdf", "png", "jpg", "jpeg"],
        help="Accepted: PDF, PNG, JPG, JPEG — max 10MB",
        key="prescription_file_uploader",
    )

    # ── Verify button ─────────────────────────────────────────────────────────
    if uploaded_file is not None:
        st.markdown(
            f"""
            <div style="
                background: #052e16;
                border: 1px solid #059669;
                border-radius: 8px;
                padding: 10px 14px;
                margin: 12px 0;
                font-size: 0.83rem;
                color: #6ee7b7;
            ">
                ✅ &nbsp; File received: <strong>{uploaded_file.name}</strong>
                ({round(uploaded_file.size / 1024, 1)} KB)
            </div>
            """,
            unsafe_allow_html=True,
        )

        if st.button("🔍 Verify Prescription", use_container_width=True):
            _verify_prescription(uploaded_file, drug_name)

    # ── Back to chat ──────────────────────────────────────────────────────────
    st.markdown("<div style='margin-top: 16px;'></div>", unsafe_allow_html=True)
    if st.button("← Ask about a different medication", use_container_width=False):
        st.session_state.ui_phase             = "chatting"
        st.session_state.pending_prescription = None
        st.rerun()


# ══════════════════════════════════════════════════════════════════════════════
# 🔍 PRESCRIPTION VERIFICATION
# ══════════════════════════════════════════════════════════════════════════════

def _verify_prescription(uploaded_file, drug_name: str) -> None:
    """
    Verifies the uploaded prescription file.
    Currently uses a dummy check — swap point below for real backend call.
    """

    with st.spinner("Verifying prescription..."):

        # 🔌 SWAP THIS — currently just checks file size > 1KB as a fake "valid" check.
        # When backend is ready, replace this entire block with:
        #
        #   from services.api_client import verify_prescription
        #   file_bytes = uploaded_file.read()
        #   result = verify_prescription(
        #       file_bytes=file_bytes,
        #       filename=uploaded_file.name,
        #       drug_name=drug_name
        #   )
        #   is_valid = result.get("valid", False)
        #   reason   = result.get("reason", "Unknown error")
        #
        # The backend endpoint for this would be POST /prescription/verify
        # It should return: { "valid": true/false, "reason": "string" }
        #
        # Delete everything below this comment block when doing the swap:

        time.sleep(2)   # 🔌 SWAP THIS — remove this sleep when using real API
        is_valid = uploaded_file.size > 1024   # dummy: any file > 1KB is "valid"
        reason   = "Prescription verified successfully." if is_valid else "File too small — invalid prescription."

    # ── Show result ───────────────────────────────────────────────────────────
    if is_valid:
        st.success(f"✅ {reason}")
        st.balloons()

        # Unlock chat flow
        st.session_state.ui_phase             = "chatting"
        st.session_state.pending_prescription = None

        st.markdown(
            f"""
            <div style="
                background: #052e16;
                border: 1px solid #059669;
                border-radius: 8px;
                padding: 12px 16px;
                margin-top: 12px;
                font-size: 0.85rem;
                color: #6ee7b7;
            ">
                🎉 Prescription accepted for <strong>{drug_name.title()}</strong>.
                Returning to chat in a moment...
            </div>
            """,
            unsafe_allow_html=True,
        )

        time.sleep(1.5)
        st.rerun()

    else:
        st.error(f"❌ {reason} Please upload a valid prescription document.")
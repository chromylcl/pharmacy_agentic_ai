import streamlit as st

def inject_global_css():
    st.markdown("""
        <style>
        /* Background */
        .stApp {
            background:
                radial-gradient(ellipse at 20% 50%, #3b0764 0%, transparent 50%),
                radial-gradient(ellipse at 80% 20%, #1e1b4b 0%, transparent 50%),
                #06030f !important;
        }

        /* Sidebar — glass */
        section[data-testid="stSidebar"] {
            background: rgba(124,58,237,0.08) !important;
            border-right: 1px solid rgba(124,58,237,0.2) !important;
        }

        /* Chat messages — glass */
        [data-testid="stChatMessage"] {
            background: rgba(255,255,255,0.04) !important;
            border: 1px solid rgba(124,58,237,0.15) !important;
            border-radius: 16px !important;
            box-shadow: 0 4px 24px rgba(0,0,0,0.3) !important;
        }

        /* Buttons — glass */
        .stButton > button {
            background: rgba(124,58,237,0.15) !important;
            border: 1px solid rgba(124,58,237,0.4) !important;
            border-radius: 10px !important;
            color: #c084fc !important;
            font-weight: 600 !important;
        }
        .stButton > button:hover {
            background: rgba(124,58,237,0.3) !important;
            border-color: #7C3AED !important;
            color: #fff !important;
            box-shadow: 0 4px 20px rgba(124,58,237,0.4) !important;
        }

        /* Expanders — glass */
        [data-testid="stExpander"] {
            background: rgba(255,255,255,0.03) !important;
            border: 1px solid rgba(124,58,237,0.15) !important;
            border-radius: 14px !important;
        }

        /* Everything else — transparent */
        .block-container,
        [data-testid="stVerticalBlock"],
        [data-testid="stHorizontalBlock"] {
            background: transparent !important;
        }

        /* Form card — glass */
        [data-testid="stForm"] {
            background: rgba(255,255,255,0.04) !important;
            border: 1px solid rgba(124,58,237,0.25) !important;
            border-radius: 20px !important;
            box-shadow: 0 8px 40px rgba(0,0,0,0.4) !important;
        }
        </style>
    """, unsafe_allow_html=True)
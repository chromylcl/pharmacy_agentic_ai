# test_storefront.py
import streamlit as st
from utils.session import init_session
from components.storefront import render_storefront

st.set_page_config(layout="wide")
init_session()
st.session_state.patient_age = 25 # Mock age for testing

render_storefront()
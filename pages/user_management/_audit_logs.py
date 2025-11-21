from db_connect import get_connection  # DB connection
import pandas as pd                   # Data handling
import streamlit as st                # Streamlit UI
from datetime import datetime         # Timestamp
from fpdf import FPDF                 # PDF export
from io import BytesIO                # PDF buffer



def load_css():
    with open("app/static/style.css") as f:
        css = f"<style>{f.read()}</style>"
        st.markdown(css, unsafe_allow_html=True)

#==================================================================
#Style Page 
#==================================================================
def render_page():
    st.title("🛺 Audit Log")
    st.caption("System Roles and Permissions")
    st.write("Role Manager Page Loaded...")


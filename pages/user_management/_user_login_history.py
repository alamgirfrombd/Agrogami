# ===========================================================
# User Login History Page
# Compatible with your existing Home.py routing
# File: pages/user_management/_user_login_history.py
# ===========================================================

import os
import pandas as pd
import streamlit as st
from datetime import datetime, date
from db_connect import get_connection
from fpdf import FPDF
from io import BytesIO


# ===========================================================
# LOAD CUSTOM CSS
# ===========================================================
def load_css(file_name="style.css"):
    """Load external CSS from app/static automatically."""
    current = os.path.abspath(__file__)

    while True:
        current = os.path.dirname(current)
        if "app" in os.listdir(current):
            css_path = os.path.join(current, "app", "static", file_name)
            break

    if os.path.exists(css_path):
        with open(css_path, "r", encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    else:
        st.warning(f"⚠ CSS not found at: {css_path}")


# ===========================================================
# LOAD LOGIN HISTORY DATA
# ===========================================================
def load_login_history():
    try:
        conn = get_connection()
        df = pd.read_sql("""
            SELECT 
                lh.LoginID,
                lh.UserID,
                u.UserName,
                u.FullName,
                lh.LoginTime,
                lh.LogoutTime,
                lh.IPAddress,
                lh.DeviceInfo,
                lh.Status
            FROM UserLoginHistory lh
            LEFT JOIN Users u ON lh.UserID = u.UserID
            ORDER BY lh.LoginID DESC
        """, conn)
        conn.close()
        return df

    except Exception as e:
        st.error(f"❌ Database Error: {e}")
        return pd.DataFrame()


# ===========================================================
# PDF EXPORT FUNCTION
# ===========================================================
def export_pdf(df):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 10, "User Login History Report", ln=True, align="C")
    pdf.ln(5)

    pdf.set_font("Arial", size=10)

    # Table Header
    header = ["UserName", "LoginTime", "LogoutTime", "IP", "Device", "Status"]
    for col in header:
        pdf.cell(32, 10, col, border=1)
    pdf.ln()

    # Table Rows
    for _, row in df.iterrows():
        pdf.cell(32, 8, str(row["UserName"]), border=1)
        pdf.cell(32, 8, str(row["LoginTime"]), border=1)
        pdf.cell(32, 8, str(row["LogoutTime"]), border=1)
        pdf.cell(32, 8, str(row["IPAddress"]), border=1)
        pdf.cell(32, 8, str(row["DeviceInfo"])[:18], border=1)
        pdf.cell(32, 8, str(row["Status"]), border=1)
        pdf.ln()

    # FIX: Get PDF as bytes
    pdf_bytes = pdf.output(dest="S").encode("latin-1")

    # Return as BytesIO buffer
    return BytesIO(pdf_bytes)



# ===========================================================
# MAIN RENDER FUNCTION
# ===========================================================
def render_page():

    st.set_page_config(page_title="User Login History", page_icon="📅", layout="wide")
    load_css()

    st.markdown("<h1 class='page-title'>📅 User Login History</h1>", unsafe_allow_html=True)

    df = load_login_history()

    if df.empty:
        st.warning("⚠ No login history found.")
        return

    # -------------------------------------------------------
    # SEARCH / FILTER AREA
    # -------------------------------------------------------
    st.subheader("🔍 Filter Login History")

    col1, col2, col3 = st.columns(3)

    # Filter 1: User
    user_filter = col1.selectbox(
        "Filter by User", 
        ["All"] + sorted(df["UserName"].dropna().unique().tolist())
    )

    # Filter 2: Status
    status_filter = col2.selectbox(
        "Filter by Status",
        ["All", "Success", "Failed"]
    )

    # Filter 3: Date Range
    default_start = df["LoginTime"].min().date()
    default_end = df["LoginTime"].max().date()

    date_range = col3.date_input(
        "Login Date Range",
        value=[default_start, default_end]
    )

    # Apply filters
    filtered_df = df.copy()

    if user_filter != "All":
        filtered_df = filtered_df[filtered_df["UserName"] == user_filter]

    if status_filter != "All":
        filtered_df = filtered_df[filtered_df["Status"] == status_filter]

    if len(date_range) == 2:
        start, end = date_range
        filtered_df = filtered_df[
            (filtered_df["LoginTime"].dt.date >= start) &
            (filtered_df["LoginTime"].dt.date <= end)
        ]

    # -------------------------------------------------------
    # EXPORT BUTTONS
    # -------------------------------------------------------
    st.divider()
    colA, colB = st.columns([1, 1])

    with colA:
        st.download_button(
            "📥 Export CSV",
            filtered_df.to_csv(index=False),
            file_name=f"user_login_history_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
            mime="text/csv"
        )

    with colB:
        pdf_data = export_pdf(filtered_df)
        st.download_button(
            "📄 Export PDF",
            pdf_data,
            file_name="login_history.pdf",
            mime="application/pdf"
        )

    # -------------------------------------------------------
    #📌 TABLE DISPLAY
    # -------------------------------------------------------
    st.subheader("📊 Login History Records")

    st.dataframe(
        filtered_df,
        use_container_width=True,
        hide_index=True
    )

    # -------------------------------------------------------
    # VIEW DETAILS SECTION
    # -------------------------------------------------------
    st.markdown("### 🔍 View Login Details")

    for _, row in filtered_df.iterrows():
        with st.expander(f"{row['UserName']} — {row['LoginTime']}"):
            st.write(f"**User:** {row['FullName']} ({row['UserName']})")
            st.write(f"**Login Time:** {row['LoginTime']}")
            st.write(f"**Logout Time:** {row['LogoutTime']}")
            st.write(f"**IP Address:** {row['IPAddress']}")
            st.write(f"**Device Info:** {row['DeviceInfo']}")
            st.write(f"**Status:** {row['Status']}")
# ==================================================
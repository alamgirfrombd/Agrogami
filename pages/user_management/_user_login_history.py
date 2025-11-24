# ===========================================================
# User Login History Page (Corrected Case Based on Query)
# ===========================================================

import os
import pandas as pd
import streamlit as st
from datetime import datetime
from db_connect import get_connection
from fpdf import FPDF
from io import BytesIO


# ===========================================================
# LOAD CSS
# ===========================================================
def load_css(file_name="style.css"):
    current = os.path.abspath(__file__)

    while True:
        current = os.path.dirname(current)
        if "app" in os.listdir(current):
            css_path = os.path.join(current, "app", "static", file_name)
            break

    if os.path.exists(css_path):
        with open(css_path, "r", encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


# ===========================================================
# LOAD LOGIN HISTORY (MATCHING QUERY)
# ===========================================================
def load_login_history():
    try:
        conn = get_connection()
        df = pd.read_sql("""
            SELECT 
                loginid,
                userid,
                logintime,
                logouttime,
                ipaddress,
                deviceinfo,
                status
            FROM public.userloginhistory
            ORDER BY loginid DESC
        """, conn)
        conn.close()

        df.columns = df.columns.str.lower()
        return df

    except Exception as e:
        st.error(f"❌ Database Error: {e}")
        return pd.DataFrame()


# ===========================================================
# PDF EXPORT
# ===========================================================
def export_pdf(df):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 10, "User Login History Report", ln=True, align="C")
    pdf.ln(5)

    pdf.set_font("Arial", size=10)

    header = ["UserID", "LoginTime", "LogoutTime", "IP", "Device", "Status"]
    for col in header:
        pdf.cell(32, 10, col, border=1)
    pdf.ln()

    for _, row in df.iterrows():
        pdf.cell(32, 8, str(row["userid"]), border=1)
        pdf.cell(32, 8, str(row["logintime"]), border=1)
        pdf.cell(32, 8, str(row["logouttime"]), border=1)
        pdf.cell(32, 8, str(row["ipaddress"]), border=1)
        pdf.cell(32, 8, str(row["deviceinfo"])[:18], border=1)
        pdf.cell(32, 8, str(row["status"]), border=1)
        pdf.ln()

    pdf_bytes = pdf.output(dest="S").encode("latin-1")
    return BytesIO(pdf_bytes)


# ===========================================================
# MAIN
# ===========================================================
def render_page():

    load_css()

    st.markdown("<h1 class='page-title'>📅 User Login History</h1>", unsafe_allow_html=True)

    df = load_login_history()

    if df.empty:
        st.warning("⚠ No login history found.")
        return

    # -------------------------------------------------------
    # FILTERS
    # -------------------------------------------------------
    st.subheader("🔍 Filter Login History")

    col1, col2, col3 = st.columns(3)

    user_filter = col1.selectbox(
        "Filter by User",
        ["All"] + sorted(df["userid"].astype(str).unique().tolist())
    )

    status_filter = col2.selectbox(
        "Filter by Status",
        ["All"] + sorted(df["status"].dropna().unique().tolist())
    )

    default_start = df["logintime"].min().date()
    default_end = df["logintime"].max().date()

    date_range = col3.date_input(
        "Login Date Range",
        value=[default_start, default_end]
    )

    filtered_df = df.copy()

    if user_filter != "All":
        filtered_df = filtered_df[filtered_df["userid"].astype(str) == user_filter]

    if status_filter != "All":
        filtered_df = filtered_df[filtered_df["status"] == status_filter]

    if len(date_range) == 2:
        start, end = date_range
        filtered_df = filtered_df[
            (filtered_df["logintime"].dt.date >= start) &
            (filtered_df["logintime"].dt.date <= end)
        ]

    # -------------------------------------------------------
    # EXPORT
    # -------------------------------------------------------
    st.divider()

    colA, colB = st.columns(2)

    with colA:
        st.download_button(
            "📥 Export CSV",
            filtered_df.to_csv(index=False),
            file_name=f"user_login_history_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
            mime="text/csv"
        )

    with colB:
        st.download_button(
            "📄 Export PDF",
            export_pdf(filtered_df),
            file_name="login_history.pdf",
            mime="application/pdf"
        )

    # -------------------------------------------------------
    # TABLE
    # -------------------------------------------------------
    st.subheader("📊 Login History Records")

    st.dataframe(
        filtered_df,
        use_container_width=True,
        hide_index=True
    )

    # -------------------------------------------------------
    # DETAILS VIEW
    # -------------------------------------------------------
    st.markdown("### 🔍 View Login Details")

    for _, row in filtered_df.iterrows():
        with st.expander(f"{row['userid']} — {row['logintime']}"):
            st.write(f"**User ID:** {row['userid']}")
            st.write(f"**Login Time:** {row['logintime']}")
            st.write(f"**Logout Time:** {row['logouttime']}")
            st.write(f"**IP Address:** {row['ipaddress']}")
            st.write(f"**Device Info:** {row['deviceinfo']}")
            st.write(f"**Status:** {row['status']}")

import streamlit as st

def show_header(title=None):
    # 👉 Only show header if a title is actually provided
    if title:
        st.markdown(
            f"""
            <div style="
                background:#1f2937;
                color:white;
                padding:6px 10px;  
                border-radius:6px;
                margin-bottom:6px; 
                font-size:17px;
                font-weight:600;
            ">
                {title}
            </div>
            """,
            unsafe_allow_html=True
        )

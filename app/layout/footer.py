import streamlit as st

def show_footer():
    st.markdown(
        """
        <br><br>
        <div style="position:fixed; left:0; bottom:0; width:100%; 
            background:#1f2937; color:white; text-align:center; 
            padding:8px; font-size:14px;">
            © 2025 AgrogamiPH — All rights reserved.
        </div>
        """,
        unsafe_allow_html=True
    )

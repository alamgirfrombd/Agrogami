import streamlit as st
from pathlib import Path
import sys

# =====================================================
# Project Setup
# =====================================================
current_file = Path(__file__)
project_root = current_file.parent
sys.path.insert(0, str(project_root))

# =====================================================
# Page Config
# =====================================================
st.set_page_config(
    page_title="Agrogami Power House - Login",
    page_icon="🌾",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# =====================================================
# Hide Streamlit System UI + Sidebar Completely
# =====================================================
st.markdown("""
<style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}

/* Fully hide sidebar */
section[data-testid="stSidebar"] {
    display: none !important;
}

/* Expand content */
div[data-testid="stAppViewContainer"] {
    margin-left: 0 !important;
    padding-left: 0 !important;
}
</style>
""", unsafe_allow_html=True)


# =====================================================
# Authentication Function
# =====================================================
def authenticate_user(username, password):
    users = {
        "admin":       {"password": "Admin123@", "role_id": 1, "name": "Admin User"},
        "shop.user":   {"password": "Shop123@", "role_id": 2, "name": "Shop User"},
        "superadmin":  {"password": "Superadmin123@", "role_id": 0, "name": "Super Admin"},
    }

    user = users.get(username)
    if user and user["password"] == password:
        return user
    return None


# =====================================================
# LOAD EXTERNAL CSS
# =====================================================
css_path = Path(project_root, "static/style.css")
if css_path.exists():
    st.markdown(f"<style>{css_path.read_text()}</style>", unsafe_allow_html=True)


# =====================================================
# Login Page UI
# =====================================================
st.markdown('<div class="login-wrapper">', unsafe_allow_html=True)


st.markdown("""
    <div class="login-title">
        🌾 Agrogami Power Housec
    </div>
""", unsafe_allow_html=True)

with st.form("login_form"):
    username = st.text_input("Username", placeholder="Enter your username")
    password = st.text_input("Password", type="password", placeholder="Enter your password")

    login_btn = st.form_submit_button("Sign In")

    if login_btn:
        user = authenticate_user(username.strip(), password)
        if user:
            st.session_state.logged_in = True
            st.session_state.user = user

            if user["role_id"] == 0:
                st.switch_page("pages/admin_dashboard.py")
            elif user["role_id"] == 1:
                st.switch_page("pages/home.py")
            elif user["role_id"] == 2:
                st.switch_page("pages/shop_dashboard.py")
        else:
            st.markdown('<div class="error-box">❌ Invalid username or password</div>', unsafe_allow_html=True)

st.markdown("</div>", unsafe_allow_html=True)

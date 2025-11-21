import streamlit as st

st.set_page_config(
    page_title="Admin Dashboard - Agrogami Power House",
    page_icon="👨‍💼",
    layout="wide"
)

# ---------------------------------------------------------
# AUTHENTICATION CHECK
# ---------------------------------------------------------
if 'user' not in st.session_state or not st.session_state.get("logged_in"):
    st.error("🔐 Please log in to access this page")

    # login.py is in ROOT — NOT inside pages
    if st.button("🔐 Go to Login"):
        st.switch_page("login.py")

    st.stop()


# ---------------------------------------------------------
# ROLE CHECK FOR ADMIN
# ---------------------------------------------------------
if st.session_state.user.get("role_id") != 1:
    st.error("🚫 Unauthorized access. Admin privileges required.")

    # Normal user should be redirected to shop dashboard
    if st.button("👨‍🌾 Go to User Dashboard"):
        st.switch_page("shop_dashboard.py")  # this file is inside pages/

    st.stop()


# ---------------------------------------------------------
# PAGE CONTENT
# ---------------------------------------------------------
st.title("👨‍💼 Admin Dashboard")
st.success(f"Welcome, {st.session_state.user.get('name', 'Admin')}!")


# ---------------------------------------------------------
# PAGE NAVIGATION BUTTONS
# ---------------------------------------------------------
col1, col2 = st.columns(2)

with col1:
    if st.button("🏠 Go to Home Page"):
        st.switch_page("home.py")              # pages/home.py

with col2:
    if st.button("👨‍🌾 User View"):
        st.switch_page("shop_dashboard.py")    # pages/shop_dashboard.py


# ---------------------------------------------------------
# LOGOUT BUTTON
# ---------------------------------------------------------
st.markdown("---")
if st.button("🚪 Logout"):
    for key in list(st.session_state.keys()):
        del st.session_state[key]

    st.switch_page("login.py")  # login.py is in ROOT

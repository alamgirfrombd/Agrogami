import streamlit as st

st.set_page_config(
    page_title="User Dashboard - AgrogamiPH",
    page_icon="👨‍🌾",
    layout="wide"
)

# Check if user is logged in
if 'user' not in st.session_state or not st.session_state.get('logged_in'):
    st.error("🔐 Please log in to access this page")
    st.page_link("login.py", label="Go to Login", icon="🔐")
    st.stop()

st.title("👨‍🌾 User Dashboard")
st.success(f"Welcome, {st.session_state.user.get('name', 'User')}!")

# User content
col1, col2 = st.columns(2)
with col1:
    st.metric("My Farms", "12")
    st.metric("Crop Health", "94%")
with col2:
    st.metric("Yield Forecast", "8.2T")
    st.metric("Weather", "Optimal")

# Navigation
st.page_link("main.py", label="🏠 Home", icon="🏠")

if st.session_state.user.get('role_id') == 1:
    st.page_link("pages/admin_dashboard.py", label="👨‍💼 Admin Dashboard", icon="👨‍💼")

if st.button("🚪 Logout"):
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.rerun()
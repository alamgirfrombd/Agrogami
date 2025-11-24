import streamlit as st
from app.layout.header import show_header
from app.layout.footer import show_footer
from pages.user_management._role_manager import render_page

# ---------------------------
# Page config + hide default multipage nav
# ---------------------------
st.set_page_config(page_title="AgrogamiPH", page_icon="🌾", layout="wide")
st.markdown(
    """
    <style>
    [data-testid="stSidebarNav"] { display: none !important; }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------------------------
# Redirect to login if logged out
# ---------------------------
if st.session_state.get("logged_out"):
    st.switch_page("login.py")

# ---------------------------
# helper: on_change callback for radios (NO rerun call here)
# ---------------------------
def _on_radio_change(group_name: str, key: str):
    """
    Store main_menu/sub_menu into session_state when a radio changes.
    Do NOT call experimental_rerun() — Streamlit will auto-rerun the script
    when the widget value changes, so this callback just updates the session.
    """
    selected = st.session_state.get(key)
    if selected:
        st.session_state["main_menu"] = group_name
        st.session_state["sub_menu"] = selected
    else:
        st.session_state.pop("main_menu", None)
        st.session_state.pop("sub_menu", None)
    # no explicit rerun call here (compatibility for different streamlit versions)



# ---------------------------
# Sidebar: Collapsible grouped radios + TOP LOGOUT BUTTON
# ---------------------------
with st.sidebar:

    # ---- Small ICON ONLY Logout Button ----
    st.markdown("""
        <style>
        .logout-btn button {
            background: transparent !important;
            color: #333 !important;
            border: none !important;
            padding: 2px !important;
            font-size: 20px !important;
            width: auto !important;
            height: auto !important;
            box-shadow: none !important;
        }
        .logout-btn button:hover {
            color: red !important;
            background: transparent !important;
        }
        </style>
    """, unsafe_allow_html=True)

    if st.button("🚪 Logout", key="logout_icon", help="Logout"):
        for key in ["logged_in", "user", "main_menu", "sub_menu"]:
            if key in st.session_state:
                del st.session_state[key]

        st.session_state["logged_out"] = True
        st.switch_page("login.py")

    st.write("")   # small gap


    # Title
    st.markdown("<h4>🌾 Agrogami Power House</h4>", unsafe_allow_html=True)
    st.write("---")

    # ensure keys exist in session_state (avoid KeyError)
    for key, default_value in {
        # Keys for the sub-page logic (based on your previous error)
        "page_mode": "list", # e.g., "list", "view", "edit", "add"
        "view_id": None,     # ID of the item being viewed/edited
        # Keys used by the routing logic
        "main_menu": None,
        "sub_menu": None,
        "logged_in": True,   # Assuming login.py sets this, but setting a default prevents errors
    }.items():
        if key not in st.session_state:
            st.session_state[key] = default_value

    # USER MANAGEMENT GROUP
    with st.expander("👤 User Management", expanded=False):
        st.radio(
            "User Management Pages",
            [
                "Role Manager",
                "Users",
                "User Profiles",
                "User Permissions",
                "User Login History",
                "Audit Logs",
            ],
            key="radio_user_mgmt",
            on_change=_on_radio_change,
            args=("User Management", "radio_user_mgmt"),
            label_visibility="collapsed",
        )

    # INVENTORY GROUP
    with st.expander("📦 Inventory Management", expanded=False):
        st.radio(
            "Inventory Pages",
            [
                "Categories",
                "Products",
                "Warehouse",
                "Inventory Stock",
            ],
            key="radio_inventory",
            on_change=_on_radio_change,
            args=("Inventory Management", "radio_inventory"),
            label_visibility="collapsed",
        )

    # SALES GROUP
    with st.expander("💰 Sales Management", expanded=False):
        st.radio(
            "Sales Pages",
            [
                "Customers",
                "Orders",
                "Order Details",
                "Payments",
            ],
            key="radio_sales",
            on_change=_on_radio_change,
            args=("Sales Management", "radio_sales"),
            label_visibility="collapsed",
        )

    # PROFILE GROUP
    with st.expander("🙍 Profile", expanded=False):
        st.radio(
            "Profile Pages",
            ["My Profile"],
            key="radio_profile",
            on_change=_on_radio_change,
            args=("Profile", "radio_profile"),
            label_visibility="collapsed",
        )

# ---------------------------
# Header + routing
# ---------------------------
main_menu = st.session_state.get("main_menu")
sub_menu = st.session_state.get("sub_menu")
# show_header(main_menu)



# ---------------------------
# Routing
# ---------------------------
if main_menu is None:
    st.markdown(
        "<h4 style='margin-top:0;'>🏠 Agrogami Power House</h4>",
        unsafe_allow_html=True
    )


# 2️⃣ USER MANAGEMENT ROUTING
elif main_menu == "User Management":

    if sub_menu == "Role Manager":
        from pages.user_management._role_manager import render_page
        render_page()

    elif sub_menu == "Users":
        from pages.user_management._users import render_page
        render_page()

    elif sub_menu == "User Profiles":
        from pages.user_management._user_profiles import render_page
        render_page()

    elif sub_menu == "User Permissions":
        from pages.user_management._user_permissions import render_page
        render_page()

    elif sub_menu == "User Login History":
        from pages.user_management._user_login_history import render_page
        render_page()

    elif sub_menu == "Audit Logs":
        from pages.user_management._audit_logs import render_page
        render_page()
        

# 3️⃣ INVENTORY MANAGEMENT ROUTING
elif main_menu == "Inventory Management":

    if sub_menu == "Categories":
        from pages.inventory_management.categories_page import render_page
        render_page()

    elif sub_menu == "Products":
        from pages.inventory_management.products_page import render_page
        render_page()

    elif sub_menu == "Warehouse":
        from pages.inventory_management.warehouse_page import render_page
        render_page()

    elif sub_menu == "Inventory Stock":
        from pages.inventory_management.inventory_page import render_page
        render_page()

# 4️⃣ SALES MANAGEMENT ROUTING
elif main_menu == "Sales Management":

    if sub_menu == "Customers":
        from pages.sales_management.customers_page import render_page
        render_page()

    elif sub_menu == "Orders":
        from pages.sales_management.orders_page import render_page
        render_page()

    elif sub_menu == "Order Details":
        from pages.sales_management.order_details_page import render_page
        render_page()

    elif sub_menu == "Payments":
        from pages.sales_management.payments_page import render_page
        render_page()

# 5️⃣ PROFILE ROUTING
elif main_menu == "Profile":
    from pages.user_management._user_profiles import render_page
    render_page()

# Footer
show_footer()

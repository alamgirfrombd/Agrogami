import streamlit as st

def _on_radio_change(group_name: str, key: str):
    selected = st.session_state.get(key)
    if selected:
        st.session_state["main_menu"] = group_name
        st.session_state["sub_menu"] = selected
    else:
        st.session_state["main_menu"] = None
        st.session_state["sub_menu"] = None


def render_sidebar():

    with st.sidebar:

        st.markdown("""
            <style>
            [data-testid="stSidebarNav"] { display: none !important; }

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
                st.session_state.pop(key, None)

            st.session_state["logged_out"] = True
            st.switch_page("login.py")

        st.markdown("<h4>🌾 Agrogami Power House</h4>", unsafe_allow_html=True)
        st.write("---")

        for key, default_value in {
            "page_mode": "list",
            "view_id": None,
            "main_menu": None,
            "sub_menu": None,
            "logged_in": True,
        }.items():
            st.session_state.setdefault(key, default_value)

        # USER MANAGEMENT
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

        # INVENTORY MANAGEMENT
        with st.expander("📦 Inventory Management", expanded=False):
            st.radio(
                "Inventory Pages",
                [
                    "Categories",
                    "Products",
                    "Warehouse",
                    "Inventory Stock",
                    "IMEI Units",
                ],
                key="radio_inventory",
                on_change=_on_radio_change,
                args=("Inventory Management", "radio_inventory"),
                label_visibility="collapsed",
            )

        # PURCHASE MANAGEMENT
        with st.expander("🛒 Purchase Management", expanded=False):
            st.radio(
                "Purchase Pages",
                [
                    "Suppliers",
                    "Purchase Orders",
                    "Purchase Items",
                ],
                key="radio_purchase",
                on_change=_on_radio_change,
                args=("Purchase Management", "radio_purchase"),
                label_visibility="collapsed",
            )

        # SALES MANAGEMENT
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

        # SERVICE & WARRANTY
        with st.expander("🛠 Service & Warranty", expanded=False):
            st.radio(
                "Service Pages",
                [
                    "Warranty Claims",
                    "Service Jobs",
                    "Service Parts Used",
                ],
                key="radio_service",
                on_change=_on_radio_change,
                args=("Service & Warranty", "radio_service"),
                label_visibility="collapsed",
            )


         # ACCOUNTING
# ACCOUNTING
    with st.expander("💵 Accounting", expanded=False):
        st.radio(
            "",
            [
                "Chart of Accounts",
                "Voucher Entry",
                "Voucher List",
                "Ledger",
                "Cash Book",
                "Bank Book",
                "Trial Balance",
                "Income Statement",
                "Balance Sheet",
            ],
            key="radio_accounting",
            on_change=_on_radio_change,
            args=("Accounting", "radio_accounting"),
            label_visibility="collapsed",
        )


        # PROFILE
        with st.expander("🙍 Profile", expanded=False):
            st.radio(
                "Profile Pages",
                ["My Profile"],
                key="radio_profile",
                on_change=_on_radio_change,
                args=("Profile", "radio_profile"),
                label_visibility="collapsed",
            )

    return (
        st.session_state.get("main_menu"),
        st.session_state.get("sub_menu"),
    )

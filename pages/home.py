import streamlit as st
from app.layout.header import show_header
from app.layout.footer import show_footer

st.set_page_config(page_title="AgrogamiPH", page_icon="🌾", layout="wide")
st.markdown(
    """
    <style>
    [data-testid="stSidebarNav"] { display: none !important; }
    </style>
    """,
    unsafe_allow_html=True,
)

if st.session_state.get("logged_out"):
    st.switch_page("login.py")


def _on_radio_change(group_name: str, key: str):
    selected = st.session_state.get(key)
    if selected:
        st.session_state["main_menu"] = group_name
        st.session_state["sub_menu"] = selected
    else:
        st.session_state.pop("main_menu", None)
        st.session_state.pop("sub_menu", None)


with st.sidebar:

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
            "",
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
        )

    # INVENTORY
    with st.expander("📦 Inventory Management", expanded=False):
        st.radio(
            "",
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
        )

    # PURCHASE
    with st.expander("🛒 Purchase Management", expanded=False):
        st.radio(
            "",
            [
                "Suppliers",
                "Purchase Orders",
                "Purchase Items",
            ],
            key="radio_purchase",
            on_change=_on_radio_change,
            args=("Purchase Management", "radio_purchase"),
        )

    # SALES
    with st.expander("💰 Sales Management", expanded=False):
        st.radio(
            "",
            [
                "Customers",
                "Orders",
                "Order Details",
                "Payments",
            ],
            key="radio_sales",
            on_change=_on_radio_change,
            args=("Sales Management", "radio_sales"),
        )

    # SERVICE & WARRANTY
    with st.expander("🛠 Service & Warranty", expanded=False):
        st.radio(
            "",
            [
                "Warranty Claims",
                "Service Jobs",
                "Service Parts Used",
            ],
            key="radio_service",
            on_change=_on_radio_change,
            args=("Service & Warranty", "radio_service"),
        )

    # ACCOUNTING
    with st.expander("💵 Accounting", expanded=False):
        st.radio(
            "",
            [
                "Chart of Accounts",
                "Voucher Entry",
                
            ],
            key="radio_accounting",
            on_change=_on_radio_change,
            args=("Accounting", "radio_accounting"),
        )

    # PROFILE
    with st.expander("🙍 Profile", expanded=False):
        st.radio(
            "",
            ["My Profile"],
            key="radio_profile",
            on_change=_on_radio_change,
            args=("Profile", "radio_profile"),
        )


main_menu = st.session_state.get("main_menu")
sub_menu = st.session_state.get("sub_menu")

if main_menu is None:
    st.markdown(
        "<h4 style='margin-top:0;'>🏠 Agrogami Power House</h4>",
        unsafe_allow_html=True
    )

# USER MANAGEMENT
elif main_menu == "User Management":
    if sub_menu == "Role Manager":
        from pages.user_management._role_manager import render_page
    elif sub_menu == "Users":
        from pages.user_management._users import render_page
    elif sub_menu == "User Profiles":
        from pages.user_management._user_profiles import render_page
    elif sub_menu == "User Permissions":
        from pages.user_management._user_permissions import render_page
    elif sub_menu == "User Login History":
        from pages.user_management._user_login_history import render_page
    elif sub_menu == "Audit Logs":
        from pages.user_management._audit_logs import render_page
    render_page()

# INVENTORY
elif main_menu == "Inventory Management":
    if sub_menu == "Categories":
        from pages.inventory_management.categories_page import render_page
    elif sub_menu == "Products":
        from pages.inventory_management.products_page import render_page
    elif sub_menu == "Warehouse":
        from pages.inventory_management.warehouse_page import render_page
    elif sub_menu == "Inventory Stock":
        from pages.inventory_management.inventory_page import render_page
    elif sub_menu == "IMEI Units":
        from pages.inventory_management.imei_units_page import render_page
    render_page()

# PURCHASE
elif main_menu == "Purchase Management":
    if sub_menu == "Suppliers":
        from pages.purchase_management.suppliers_page import render_page
    elif sub_menu == "Purchase Orders":
        from pages.purchase_management.purchase_orders_page import render_page
    elif sub_menu == "Purchase Items":
        from pages.purchase_management.purchase_items_page import render_page
    render_page()

# SALES
elif main_menu == "Sales Management":
    if sub_menu == "Customers":
        from pages.sales_management.customers_page import render_page
    elif sub_menu == "Orders":
        from pages.sales_management.orders_page import render_page
    elif sub_menu == "Order Details":
        from pages.sales_management.order_details_page import render_page
    elif sub_menu == "Payments":
        from pages.sales_management.payments_page import render_page
    render_page()

# SERVICE & WARRANTY
elif main_menu == "Service & Warranty":
    if sub_menu == "Warranty Claims":
        from pages.service_management.warranty_claims_page import render_page
    elif sub_menu == "Service Jobs":
        from pages.service_management.service_jobs_page import render_page
    elif sub_menu == "Service Parts Used":
        from pages.service_management.service_parts_used_page import render_page
    render_page()

# ACCOUNTING
elif main_menu == "Accounting":
    if sub_menu == "Chart of Accounts":
        from pages.accounting.chart_of_accounts_page import render_page
    elif sub_menu == "Voucher Entry":
        from pages.accounting.voucher_entry_page import render_page
    elif sub_menu == "Voucher List":
        from pages.accounting.voucher_list_page import render_page
    elif sub_menu == "Ledger":
        from pages.accounting.ledger_page import render_page
    elif sub_menu == "Cash Book":
        from pages.accounting.cash_book_page import render_page
    elif sub_menu == "Bank Book":
        from pages.accounting.bank_book_page import render_page
    elif sub_menu == "Trial Balance":
        from pages.accounting.trial_balance_page import render_page
    elif sub_menu == "Income Statement":
        from pages.accounting.income_statement_page import render_page
    elif sub_menu == "Balance Sheet":
        from pages.accounting.balance_sheet_page import render_page
    render_page()

show_footer()

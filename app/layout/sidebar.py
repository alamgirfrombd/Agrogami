import streamlit as st

def sidebar_menu():

    # ========== BRANDING ==========
    with st.sidebar:
        st.image("app/static/logo.png", width=120)
        st.markdown(
            """
            <h3 style="margin-bottom:6px;">🌾 Agrogami Power House</h3>
            <hr style="margin-top:0;">
            """,
            unsafe_allow_html=True,
        )

        # Prepare return variables
        main_menu = None
        sub_menu = None

        # ========== MAIN MENU ==========
        main_menu = st.radio(
            "",
            [
                "Dashboard",
                "User Management",
                "Inventory Management",
                "Sales Management",
                "Profile"
            ],
            label_visibility="collapsed",
            key="main_menu_radio"
        )

        # ========== SUB MENUS ==========
        # USER MANAGEMENT
        if main_menu == "User Management":
            st.markdown("#### 👤 User Management")
            sub_menu = st.radio(
                "",
                [
                    "Role Manager",
                    "Users",
                    "User Profiles",
                    "User Permissions",
                    "User Login History",
                    "Audit Logs",
                ],
                label_visibility="collapsed",
                key="sub_user_mgmt"
            )

        # INVENTORY
        elif main_menu == "Inventory Management":
            st.markdown("#### 📦 Inventory Management")
            sub_menu = st.radio(
                "",
                [
                    "Categories",
                    "Products",
                    "Warehouse",
                    "Inventory Stock",
                ],
                label_visibility="collapsed",
                key="sub_inventory"
            )

        # SALES MANAGEMENT
        elif main_menu == "Sales Management":
            st.markdown("#### 💰 Sales Management")
            sub_menu = st.radio(
                "",
                [
                    "Customers",
                    "Orders",
                    "Order Details",
                    "Payments",
                ],
                label_visibility="collapsed",
                key="sub_sales"
            )

        # PROFILE
        elif main_menu == "Profile":
            st.markdown("#### 🙍 Profile")
            sub_menu = st.radio(
                "",
                ["My Profile"],
                label_visibility="collapsed",
                key="sub_profile"
            )




    return main_menu, sub_menu

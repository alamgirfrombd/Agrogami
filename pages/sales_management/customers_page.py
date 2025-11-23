import streamlit as st
import pandas as pd
from datetime import datetime
from typing import Optional
from db_connect import get_connection # Assumes this is correctly set up

# =========================================================================================
# I. UTILITIES & DATABASE OPERATIONS
# =========================================================================================

def generate_customer_code() -> str:
    """Generates a unique customer code based on the current max ID."""
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT COALESCE(MAX(customerid), 0) FROM public.customers;")
            last_id = cur.fetchone()[0]
            return f"CUST-{last_id + 1:06d}"

@st.cache_data(ttl=60)  # Refresh every 60 seconds
def get_customers() -> pd.DataFrame:
    """Fetches all customers from the database."""
    with get_connection() as conn:
        df = pd.read_sql("""
            SELECT customerid, customercode, fullname, contactphone,
                   email, city, nid, isactive, createddate
            FROM public.customers
            ORDER BY customerid DESC
        """, conn)
        df.columns = ["ID", "Code", "Full Name", "Phone", "Email", "City", "NID", "Active", "Created"]
        return df


def get_customer_by_id(cid: int) -> Optional[dict]:
    """Fetches a single customer's details by ID."""
    with get_connection() as conn:
        df = pd.read_sql("""
            SELECT customerid, customercode, fullname, contactphone,
                   email, city, nid, isactive
            FROM public.customers WHERE customerid = %s
        """, conn, params=[cid])
        if df.empty:
            return None
        row = df.iloc[0]
        return {
            "ID": row.customerid,
            "Code": row.customercode,
            "Full Name": row.fullname,
            "Phone": row.contactphone or "",
            "Email": row.email or "",
            "City": row.city or "",
            "NID": row.nid or "",
            "Active": row.isactive
        }


def create_customer(data: dict):
    """Inserts a new customer record into the database."""
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO public.customers
                (customercode, fullname, contactphone, email, city, nid, isactive, createddate)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                data["Code"], data["Full Name"], data["Phone"], data["Email"],
                data["City"], data["NID"], data["Active"], datetime.utcnow()
            ))
            conn.commit()
    st.success("Customer created successfully!")
    st.cache_data.clear()
    st.rerun()


def update_customer(cid: int, data: dict):
    """Updates an existing customer record."""
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                UPDATE public.customers SET
                    fullname=%s, contactphone=%s, email=%s, city=%s,
                    nid=%s, isactive=%s, updateddate=%s
                WHERE customerid=%s
            """, (
                data["Full Name"], data["Phone"], data["Email"], data["City"],
                data["NID"], data["Active"], datetime.utcnow(), cid
            ))
            conn.commit()
    st.success("Customer updated successfully!")
    st.cache_data.clear()
    st.rerun()


def delete_customer(cid: int):
    """Deletes a customer if they are not linked to any orders."""
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) FROM public.orders WHERE customerid=%s", (cid,))
            if cur.fetchone()[0] > 0:
                st.error("Cannot delete: Customer is used in existing orders.")
                return
            cur.execute("DELETE FROM public.customers WHERE customerid=%s", (cid,))
            conn.commit()
    st.success("Customer deleted.")
    st.cache_data.clear()
    st.rerun()


# =========================================================================================
# II. MODALS/DIALOG FUNCTIONS
# =========================================================================================

def view_customer_dialog():
    """Renders the View Customer detail dialog content."""
    if not st.session_state.get("selected_customer"):
        return
    customer = get_customer_by_id(st.session_state.selected_customer)
    if not customer:
        st.error("Customer not found.")
        return

    st.markdown(f"### 👁 Customer: **{customer['Full Name']}**")
    st.markdown(f"**Code:** `{customer['Code']}`")
    st.markdown(f"**Phone:** {customer['Phone'] or '-'}")
    st.markdown(f"**Email:** {customer['Email'] or '-'}")
    st.markdown(f"**City:** {customer['City'] or '-'}")
    st.markdown(f"**NID:** {customer['NID'] or '-'}")
    st.markdown(f"**Status:** {'🟢 Active' if customer['Active'] else '🔴 Inactive'}")

    if st.button("Close", type="primary", use_container_width=True):
        st.session_state.show_view = False
        st.rerun()


def edit_customer_dialog(is_add_mode: bool = False):
    """Renders the Add or Edit Customer form dialog content."""
    title = "➕ Add New Customer" if is_add_mode else "✏️ Edit Customer"
    customer = None
    if not is_add_mode:
        if not st.session_state.get("selected_customer"):
             st.error("No customer selected for editing.")
             return
        customer = get_customer_by_id(st.session_state.selected_customer)
        if not customer:
            st.error("Customer not found.")
            return

    with st.form(title, clear_on_submit=is_add_mode):
        st.markdown(f"### {title}")

        code = generate_customer_code() if is_add_mode else customer["Code"]
        if is_add_mode:
            st.text_input("Customer Code", value=code, disabled=True)
        else:
            st.text_input("Customer Code", value=code, disabled=True)

        fullname = st.text_input("Full Name *", value="" if is_add_mode else customer["Full Name"])
        phone = st.text_input("Phone", value="" if is_add_mode else customer["Phone"])
        email = st.text_input("Email", value="" if is_add_mode else customer["Email"])
        city = st.text_input("City", value="" if is_add_mode else customer["City"])
        nid = st.text_input("NID / Passport", value="" if is_add_mode else customer["NID"])
        active = st.checkbox("Active", value=True if is_add_mode else customer["Active"])

        col1, col2 = st.columns(2)
        with col1:
            if st.form_submit_button("💾 Save", type="primary", use_container_width=True):
                if not fullname.strip():
                    st.error("Full Name is required.")
                    return

                data = {
                    "Code": code,
                    "Full Name": fullname.strip(),
                    "Phone": phone or None,
                    "Email": email or None,
                    "City": city or None,
                    "NID": nid or None,
                    "Active": active
                }

                if is_add_mode:
                    create_customer(data)
                else:
                    update_customer(customer["ID"], data)

        with col2:
            if st.form_submit_button("❌ Cancel", use_container_width=True):
                st.session_state.show_edit = False
                st.session_state.show_add = False
                st.rerun()


# =========================================================================================
# III. MAIN PAGE RENDER FUNCTION (Exported to home.py)
# =========================================================================================

def render_page():
    """Renders the main Customer Management UI."""
    st.title("👥 Customers Management")

    # Custom CSS remains for dialogs and general styling
    st.markdown("""
    <style>
        .stButton>button[kind="secondary"] { width: 100%; }
        /* Re-added original card styling for backward compatibility */
        .customer-card { 
            padding: 1rem; 
            border-radius: 0.5rem; 
            border: 1px solid #3333; 
            margin-bottom: 10px; /* Added spacing */
        }
        .header-row { 
            background-color: #f0f2f6; 
            padding: 0.75rem; 
            border-radius: 0.5rem; 
            font-weight: 600; 
            margin-top: 10px;
        }
        .status-active { color: #2e8b57; font-weight: bold; }
        .status-inactive { color: #dc143c; font-weight: bold; }
        
        /* Smaller button sizes for the card actions */
        div.stButton button {
            padding: 0px 4px; /* Reduced padding */
            min-height: 20px; /* Reduced height */
            line-height: 1; /* Aligns text */
            font-size: 10px;
        }
    </style>
    """, unsafe_allow_html=True)

    # Session State Initialization (Ensures keys exist before use)
    for key, value in {
        "selected_customer": None,
        "show_view": False,
        "show_edit": False,
        "show_add": False,
        "search_term": "",
        "filter_active": "All"
    }.items():
        if key not in st.session_state:
            st.session_state[key] = value

    # --- Header and Search Controls ---
    col1, col2 = st.columns([1, 1])
    with col1:
        st.button("➕ Add New Customer", type="primary", use_container_width=True,
                  on_click=lambda: st.session_state.update({"show_add": True, "selected_customer": None}))

    with col2:
        search = st.text_input("🔍 Search customers...", value=st.session_state.search_term,
                               placeholder="Name, phone, code, city...")
        st.session_state.search_term = search
        
    # Load and filter data
    df = get_customers()

    if search:
        # Filter logic to search across all columns
        mask = df.astype(str).apply(lambda x: x.str.contains(search, case=False, na=False)).any(axis=1)
        df = df[mask]

    if st.session_state.filter_active != "All":
        active_bool = st.session_state.filter_active == "Active"
        df = df[df["Active"] == active_bool]
    
    # --- Display Customer List in Card/Loop Format (Revert) ---
    st.markdown("## Customer Records")
    
    if df.empty:
        st.info("No customers found matching your criteria.")
    else:
        # Header (re-added for visual separation)
        st.markdown("<div class='header-row'>Customers List</div>", unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)

        # Customer cards loop (reverted to original robust logic)
        for _, row in df.iterrows():
            with st.container():
                # Use st.columns directly on the row level to avoid complex HTML/CSS interactions
                col_left, col_right = st.columns([5, 2])
                
                # Container for the card look
                col_left.markdown("<div class='customer-card' style='margin-bottom: -15px;'>", unsafe_allow_html=True)
                col_right.markdown("<div class='customer-card' style='margin-bottom: -15px; padding: 0.5rem;'>", unsafe_allow_html=True)


                with col_left:
                    st.markdown(f"**{row['Full Name']}**")
                    st.caption(
                        f"{row['Code']} • {row['Phone'] or '-'} • {row['City'] or '-'} • "
                        f"{'🟢 Active' if row['Active'] else '🔴 Inactive'}"
                    )

                with col_right:
                    b1, b2, b3 = st.columns(3)
                    with b1:
                        if st.button("👁", key=f"view_{row['ID']}", help="View Details"):
                            st.session_state.selected_customer = row['ID']
                            st.session_state.show_view = True
                    with b2:
                        if st.button("✏️", key=f"edit_{row['ID']}", help="Edit"):
                            st.session_state.selected_customer = row['ID']
                            st.session_state.show_edit = True
                    with b3:
                        if st.button("🗑️", key=f"del_{row['ID']}", help="Delete"):
                            delete_customer(row['ID'])
                
                # Use a horizontal rule for better separation
                st.markdown("---")


    # --- Dialog Rendering ---
    try:
        # Streamlit >=1.31 supports st.dialog
        if st.session_state.show_view:
            with st.dialog("Customer Details"):
                view_customer_dialog()

        if st.session_state.show_edit:
            with st.dialog("Edit Customer"):
                edit_customer_dialog(is_add_mode=False)

        if st.session_state.show_add:
            with st.dialog("Add New Customer"):
                edit_customer_dialog(is_add_mode=True)

    except AttributeError:
        # Fallback for older Streamlit versions
        if st.session_state.show_view:
            view_customer_dialog()
            if st.button("Close View", key="close_view"):
                st.session_state.show_view = False
                st.rerun()

        if st.session_state.show_edit or st.session_state.show_add:
            edit_customer_dialog(is_add_mode=st.session_state.show_add)


# =========================================================================================
# IV. ENTRY POINT (Runs only if the script is executed directly)
# =========================================================================================
if __name__ == "__main__":
    render_page()
import streamlit as st
import pandas as pd
from datetime import datetime
from typing import Optional
from db_connect import get_connection

# =========================================================================================
# I. SESSION STATE MANAGEMENT
# =========================================================================================

def init_session_state():
    """Initializes session state variables for modal control."""
    for key, value in {
        "show_order_details": False,
        "show_order_form": False,
        "selected_order_id": None
    }.items():
        if key not in st.session_state:
            st.session_state[key] = value

def open_details(order_id: int):
    """Opens the order details modal."""
    st.session_state.selected_order_id = order_id
    st.session_state.show_order_details = True
    st.session_state.show_order_form = False

def open_form(order_id: Optional[int] = None):
    """Opens the order form modal (Add or Edit)."""
    st.session_state.selected_order_id = order_id
    st.session_state.show_order_form = True
    st.session_state.show_order_details = False
    
def close_modals():
    """Closes all modals."""
    st.session_state.show_order_details = False
    st.session_state.show_order_form = False
    st.rerun()

# =========================================================================================
# II. DATABASE FUNCTIONS
# =========================================================================================

@st.cache_data(ttl=60) # Added caching for efficiency
def get_orders() -> pd.DataFrame:
    conn = get_connection()
    query = """
        SELECT 
            O.orderid       AS "OrderId",
            O.ordernumber   AS "OrderNumber",
            C.fullname      AS "CustomerName",
            O.orderdate     AS "OrderDate",
            O.status        AS "Status",
            O.subtotal      AS "SubTotal",
            O.discount      AS "Discount",
            O.tax           AS "Tax",
            O.totalamount   AS "TotalAmount"
        FROM public.orders O
        JOIN public.customers C ON O.customerid = C.customerid
        ORDER BY O.orderdate DESC;
    """
    df = pd.read_sql(query, conn)
    conn.close()
    return df

@st.cache_data(ttl=300) # Added caching for efficiency
def get_customers() -> pd.DataFrame:
    conn = get_connection()
    df = pd.read_sql("""
        SELECT 
            customerid   AS "CustomerId",
            fullname     AS "FullName"
        FROM public.customers
        WHERE isactive = TRUE
    """, conn)
    conn.close()
    return df


def get_order_by_id(order_id: int):
    conn = get_connection()
    df = pd.read_sql("""
        SELECT 
            orderid      AS "OrderId",
            ordernumber  AS "OrderNumber",
            customerid   AS "CustomerID",
            orderdate    AS "OrderDate",
            status       AS "Status",
            subtotal     AS "SubTotal",
            discount     AS "Discount",
            tax          AS "Tax",
            totalamount  AS "TotalAmount"
        FROM public.orders
        WHERE orderid = %s
    """, conn, params=[order_id])
    conn.close()
    return df.iloc[0] if not df.empty else None


def insert_order(data: dict):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO public.orders 
        (ordernumber, customerid, orderdate, status, subtotal, discount, tax, totalamount)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """, tuple(data.values()))
    conn.commit()
    conn.close()
    st.cache_data.clear() # Clear cache on write

def update_order(order_id: int, data: dict):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE public.orders SET
            ordernumber=%s, customerid=%s, orderdate=%s, status=%s,
            subtotal=%s, discount=%s, tax=%s, totalamount=%s
        WHERE orderid=%s
    """, (*data.values(), order_id))
    conn.commit()
    conn.close()
    st.cache_data.clear() # Clear cache on write

def delete_order(order_id: int) -> tuple[bool, str]:
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT COUNT(*) FROM public.orderdetails WHERE orderid=%s", (order_id,))
        detail_count = cursor.fetchone()[0]

        if detail_count > 0:
            return False, "⚠ Cannot delete. This order has order items."

        cursor.execute("DELETE FROM public.orders WHERE orderid=%s", (order_id,))
        conn.commit()
        st.cache_data.clear() # Clear cache on write
        return True, "✅ Order deleted successfully."

    except Exception as e:
        return False, f"❌ Error deleting order: {str(e)}"

    finally:
        conn.close()


# =========================================================================================
# III. AUTO-GENERATE ORDER NUMBER
# =========================================================================================
def generate_order_number():
    conn = get_connection()
    today = datetime.now().strftime("%Y%m%d")

    df = pd.read_sql("""
        SELECT ordernumber 
        FROM public.orders
        WHERE ordernumber LIKE %s
        ORDER BY ordernumber DESC
        LIMIT 1
    """, conn, params=[f"{today}-%"])

    conn.close()

    if df.empty:
        return f"{today}-0001"

    last_seq_str = df.iloc[0]["OrderNumber"].split("-")[1]
    last_seq = int(last_seq_str)
    return f"{today}-{str(last_seq + 1).zfill(4)}"


# =========================================================================================
# IV. MODAL RENDERING FUNCTIONS (Replacing @st.dialog)
# =========================================================================================
def render_order_details_modal(order_id: int):
    """Renders the Order Details content in a classic container/modal style."""
    st.subheader("📄 Order Details")
    row = get_order_by_id(order_id)
    if row is None:
        st.error("Order not found.")
        return

    st.markdown(f"### Order: **{row['OrderNumber']}**")
    st.markdown(f"**Customer ID:** {row['CustomerID']}")
    st.markdown(f"**Order Date:** {str(row['OrderDate']).split()[0]}")
    
    st.divider()

    col_data = st.columns(4)
    col_data[0].metric("Subtotal", f"{row['SubTotal']:,.2f}")
    col_data[1].metric("Discount", f"{row['Discount']:,.2f}")
    col_data[2].metric("Tax", f"{row['Tax']:,.2f}")
    col_data[3].metric("Total", f"{row['TotalAmount']:,.2f}")

    if st.button("Close", type="primary", use_container_width=True):
        close_modals()


def render_order_form_modal(order_id: Optional[int] = None):
    """Renders the Add/Edit Order Form content in a classic container/modal style."""
    is_edit = order_id is not None
    title = "📝 Edit Order" if is_edit else "➕ Add New Order"

    customers = get_customers()
    customer_map = customers.set_index("CustomerId")["FullName"].to_dict()

    row = get_order_by_id(order_id) if is_edit else None

    with st.form(title, clear_on_submit=not is_edit):
        st.markdown(f"### {title}")
        
        # --- Form Fields ---
        order_number = row["OrderNumber"] if is_edit else generate_order_number()
        order_number = st.text_input("Order Number", order_number, disabled=True)
        
        # Calculate index for selectbox
        customer_index = 0
        if is_edit and row["CustomerID"] in customer_map:
            try:
                customer_index = list(customer_map.keys()).index(row["CustomerID"])
            except ValueError:
                # Fallback if customer ID exists but isn't in the active list keys
                customer_index = 0 

        customer_id = st.selectbox(
            "Customer",
            list(customer_map.keys()),
            index=customer_index,
            format_func=lambda x: customer_map.get(x, "Unknown Customer"),
        )

        order_date_value = row["OrderDate"] if is_edit else datetime.now().date()
        order_date = st.date_input("Order Date", value=order_date_value)

        status_list = ["New", "Pending", "Shipped", "Completed", "Cancelled"]
        status_index = status_list.index(row["Status"]) if is_edit and row["Status"] in status_list else 0
        status = st.selectbox("Status", status_list, index=status_index)

        c1, c2, c3, c4 = st.columns(4)
        subtotal = c1.number_input("SubTotal", min_value=0.0, value=float(row["SubTotal"]) if is_edit else 0.0, step=0.01)
        discount = c2.number_input("Discount", min_value=0.0, value=float(row["Discount"]) if is_edit else 0.0, step=0.01)
        tax = c3.number_input("Tax", min_value=0.0, value=float(row["Tax"]) if is_edit else 0.0, step=0.01)
        total = round(subtotal - discount + tax, 2)
        c4.number_input("Total Amount", value=total, disabled=True, format="%.2f")

        
        # --- Form Actions ---
        col_save, col_cancel = st.columns(2)

        with col_save:
            if st.form_submit_button("💾 Save Order", type="primary", use_container_width=True):
                data = {
                    "OrderNumber": order_number,
                    "CustomerID": customer_id,
                    "OrderDate": order_date,
                    "Status": status,
                    "SubTotal": subtotal,
                    "Discount": discount,
                    "Tax": tax,
                    "TotalAmount": total
                }

                if is_edit:
                    update_order(order_id, data)
                    st.success("Order updated.")
                else:
                    insert_order(data)
                    st.success("Order created.")
                
                close_modals() # Close and rerun
        
        with col_cancel:
            if st.form_submit_button("❌ Cancel", use_container_width=True):
                close_modals() # Close and rerun


# =========================================================================================
# V. MAIN PAGE UI
# =========================================================================================
def main():
    init_session_state()

    st.title("🛒 Orders Management")
    st.button("➕ Add New Order", type="primary", on_click=lambda: open_form(), use_container_width=True)

    df = get_orders()
    
    # Apply status-based styling
    def status_style(status):
        if status == 'Completed':
            return 'background-color: #e6ffe6; color: green; font-weight: bold;'
        elif status == 'Cancelled':
            return 'background-color: #ffe6e6; color: red; font-weight: bold;'
        elif status == 'Pending':
            return 'background-color: #fffbe6; color: orange;'
        return ''
    
    # --- Orders List Display ---
    st.markdown("### Orders List")
    if df.empty:
        st.warning("No Orders Found")
        return

    # Use st.dataframe for a world-class, searchable/sortable list (The Data Table)
    st.dataframe(
        df.style.applymap(status_style, subset=["Status"]),
        use_container_width=True,
        hide_index=True,
        column_order=["OrderNumber", "CustomerName", "OrderDate", "Status", "TotalAmount"],
        column_config={
            "OrderId": None,
            "SubTotal": None,
            "Discount": None,
            "Tax": None,
            "OrderDate": st.column_config.DatetimeColumn("Date", format="YYYY-MM-DD"),
            "TotalAmount": st.column_config.NumberColumn("Total", format="R$ %.2f"),
        }
    )
    st.divider()

    # --- Actions List (Manual buttons to trigger modals) ---
    st.markdown("### Record Actions")
    
    # Header for the manual list
    header_cols = st.columns([1, 2, 2, 2, 1.5, 0.5, 0.5, 0.5])
    header_cols[0].write("**ID**")
    header_cols[1].write("**Order No**")
    header_cols[2].write("**Customer**")
    header_cols[3].write("**Date**")
    header_cols[4].write("**Total**")


    for _, r in df.iterrows():
        with st.container(border=True):
            cols = st.columns([1, 2, 2, 2, 1.5, 0.5, 0.5, 0.5])

            cols[0].write(r["OrderId"])
            cols[1].write(r["OrderNumber"])
            cols[2].write(r["CustomerName"])
            cols[3].write(str(r["OrderDate"]).split()[0]) # Show date only
            cols[4].write(f"R$ {r['TotalAmount']:,.2f}") # Format total amount

            if cols[5].button("👁", key=f"view{r['OrderId']}", help="View Details", on_click=open_details, args=(int(r["OrderId"]),)):
                pass # Action handled by on_click

            if cols[6].button("✏️", key=f"edit{r['OrderId']}", help="Edit", on_click=open_form, args=(int(r["OrderId"]),)):
                pass # Action handled by on_click

            if cols[7].button("🗑️", key=f"del{r['OrderId']}", help="Delete"):
                success, msg = delete_order(int(r["OrderId"]))
                if success:
                    st.success(msg)
                    st.rerun()
                else:
                    st.error(msg)
    
    
    # --- MODAL RENDERING (Conditional Logic) ---
    # This block replaces the @st.dialog decorator logic

    if st.session_state.show_order_details and st.session_state.selected_order_id is not None:
        with st.container():
            st.warning("--- Order Details Modal ---") # Visual cue that this is a modal/popup
            render_order_details_modal(st.session_state.selected_order_id)
            st.warning("-------------------------")

    if st.session_state.show_order_form:
        with st.container():
            st.info("--- Order Form Modal ---") # Visual cue that this is a modal/popup
            render_order_form_modal(st.session_state.selected_order_id)
            st.info("------------------------")


# =========================================================================================
# VI. MULTIPAGE HOOK
# =========================================================================================
def render_page():
    main()


if __name__ == "__main__":
    main()
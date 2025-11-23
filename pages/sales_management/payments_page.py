import streamlit as st
import pandas as pd
from datetime import datetime
from typing import Optional
# Assuming db_connect is available
from db_connect import get_connection 

# =========================================================================================
# I. PAGE CONFIG (REMOVED)
# =========================================================================================
# st.set_page_config(page_title="Payments Management", page_icon="💳", layout="wide") # REMOVED

# =========================================================================================
# II. SESSION STATE & MODAL MANAGEMENT (New)
# =========================================================================================

def init_session_state():
    """Initializes session state variables for modal control."""
    for key, value in {
        "show_payment_view": False,
        "show_payment_form": False,
        "active_payment_id": None
    }.items():
        if key not in st.session_state:
            st.session_state[key] = value

def open_view(payment_id: int):
    """Opens the payment view modal."""
    st.session_state.active_payment_id = payment_id
    st.session_state.show_payment_view = True
    st.session_state.show_payment_form = False

def open_form(payment_id: Optional[int] = None):
    """Opens the add/edit form modal."""
    st.session_state.active_payment_id = payment_id
    st.session_state.show_payment_form = True
    st.session_state.show_payment_view = False
    
def close_modals():
    """Closes all modals and reruns the app to refresh."""
    st.session_state.show_payment_view = False
    st.session_state.show_payment_form = False
    st.rerun()

# =========================================================================================
# III. DATABASE FUNCTIONS — PostgreSQL FIXED (Added caching)
# =========================================================================================

@st.cache_data(ttl=300)
def get_orders_dropdown():
    conn = get_connection()
    df = pd.read_sql("""
        SELECT 
            orderid     AS "OrderId",
            ordernumber AS "OrderNumber"
        FROM public.orders
        ORDER BY orderid DESC
    """, conn)
    conn.close()
    return df

@st.cache_data(ttl=60)
def get_payments() -> pd.DataFrame:
    conn = get_connection()
    df = pd.read_sql("""
        SELECT 
            p.paymentid      AS "PaymentID",
            p.orderid        AS "OrderID",
            o.ordernumber    AS "OrderNumber",
            p.paymentdate    AS "PaymentDate",
            p.amount         AS "Amount",
            p.paymentmethod  AS "PaymentMethod",
            p.transactionref AS "TransactionRef"
        FROM public.payments p
        JOIN public.orders o ON p.orderid = o.orderid
        ORDER BY p.paymentid DESC
    """, conn)
    conn.close()
    return df


def get_payment_by_id(payment_id: int):
    conn = get_connection()
    df = pd.read_sql("""
        SELECT 
            p.paymentid      AS "PaymentID",
            p.orderid        AS "OrderID",
            o.ordernumber    AS "OrderNumber",
            p.paymentdate    AS "PaymentDate",
            p.amount         AS "Amount",
            p.paymentmethod  AS "PaymentMethod",
            p.transactionref AS "TransactionRef"
        FROM public.payments p
        JOIN public.orders o ON p.orderid = o.orderid
        WHERE p.paymentid = %s
    """, conn, params=[payment_id])
    conn.close()
    return df.iloc[0] if not df.empty else None


def insert_payment(data: dict):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO public.payments (orderid, paymentdate, amount, paymentmethod, transactionref)
        VALUES (%s, %s, %s, %s, %s)
    """, (data["OrderID"], data["PaymentDate"], data["Amount"], data["PaymentMethod"], data["TransactionRef"]))
    conn.commit()
    conn.close()
    st.cache_data.clear() # Clear cache on write


def update_payment(payment_id: int, data: dict):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE public.payments 
        SET orderid=%s, paymentdate=%s, amount=%s, paymentmethod=%s, transactionref=%s
        WHERE paymentid=%s
    """, (data["OrderID"], data["PaymentDate"], data["Amount"], data["PaymentMethod"], data["TransactionRef"], payment_id))
    conn.commit()
    conn.close()
    st.cache_data.clear() # Clear cache on write


def delete_payment(payment_id: int):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM public.payments WHERE paymentid=%s", (payment_id,))
    conn.commit()
    conn.close()
    st.cache_data.clear() # Clear cache on write


# =========================================================================================
# IV. MODAL CONTENT FUNCTIONS (Replacing @st.dialog)
# =========================================================================================

def render_view_payment_modal(payment_id: int):
    """Renders the Payment Details content."""
    st.header("📄 Payment Details")
    row = get_payment_by_id(payment_id)
    if row is None:
        st.error("Payment not found.")
        return

    st.text_input("Payment ID", value=row["PaymentID"], disabled=True)
    st.text_input("Order ID", value=row["OrderID"], disabled=True)
    st.text_input("Order Number", value=row["OrderNumber"], disabled=True)
    st.text_input("Payment Date", value=str(row["PaymentDate"]).split()[0], disabled=True)
    st.text_input("Amount", value=f"R$ {float(row['Amount']):,.2f}", disabled=True)
    st.text_input("Method", value=row["PaymentMethod"], disabled=True)
    st.text_input("Transaction Ref", value=row["TransactionRef"], disabled=True)

    if st.button("Close View", use_container_width=True):
        close_modals()


def render_payment_form_modal(payment_id: Optional[int] = None):
    """Renders the Add / Edit Payment form."""

    orders = get_orders_dropdown()
    order_map = orders.set_index("OrderId")["OrderNumber"].to_dict()
    order_ids = list(order_map.keys())

    row = get_payment_by_id(payment_id) if payment_id else None
    is_edit = row is not None

    with st.form("payment_form", clear_on_submit=not is_edit):
        st.subheader("Edit Payment" if is_edit else "Add Payment")
        st.markdown("---")

        # Set default index for Order ID
        order_index = 0
        if is_edit:
            try:
                order_index = order_ids.index(row["OrderID"])
            except ValueError:
                pass # Default to 0 if order is not found in dropdown list

        order_id = st.selectbox(
            "Order",
            options=order_ids,
            index=order_index,
            format_func=lambda x: f"{order_map[x]} (ID: {x})",
            key="order_select"
        )

        payment_date_value = row["PaymentDate"] if is_edit else datetime.now().date()
        payment_date = st.date_input(
            "Payment Date", value=payment_date_value, key="payment_date"
        )

        default_amount = float(row["Amount"]) if is_edit else 0.0
        amount = st.number_input(
            "Amount", min_value=0.0, value=default_amount, format="%.2f", step=0.01, key="amount_input"
        )

        method_list = ["Cash", "Card", "Mobile Banking", "Bank Transfer", "Cheque", "Other"]
        method_index = method_list.index(row["PaymentMethod"]) if is_edit and row["PaymentMethod"] in method_list else 0
        method = st.selectbox(
            "Payment Method",
            method_list,
            index=method_index,
            key="method_select"
        )

        ref = st.text_input("Transaction Reference", value=row["TransactionRef"] if is_edit else "", key="ref_input")
        
        col_save, col_cancel = st.columns(2)

        with col_save:
            if st.form_submit_button("💾 Save Payment", type="primary", use_container_width=True):

                data = {
                    "OrderID": order_id,
                    "PaymentDate": payment_date,
                    "Amount": amount,
                    "PaymentMethod": method,
                    "TransactionRef": ref,
                }

                if is_edit:
                    update_payment(payment_id, data)
                    st.success("Payment updated successfully!")
                else:
                    insert_payment(data)
                    st.success("Payment added successfully!")

                close_modals() # Close and rerun
        
        with col_cancel:
            if st.form_submit_button("❌ Cancel", use_container_width=True):
                close_modals() # Close and rerun


# =========================================================================================
# V. MAIN PAGE — Payments List
# =========================================================================================
def main():
    init_session_state()

    st.title("💳 Payments Management")

    st.button("➕ Add Payment", on_click=open_form, type="primary", use_container_width=True)
    st.markdown("---")

    df = get_payments()

    if df.empty:
        st.info("No payments recorded yet.")
        return

    # Header Row
    header_cols = st.columns([1, 2, 2, 1.5, 1.5, 2, 0.8, 0.8, 0.8])
    header_cols[0].markdown("**ID**")
    header_cols[1].markdown("**Order No**")
    header_cols[2].markdown("**Date**")
    header_cols[3].markdown("**Amount**")
    header_cols[4].markdown("**Method**")
    header_cols[5].markdown("**Ref.**")
    
    # Data Rows
    for _, r in df.iterrows():
        with st.container(border=True):
            cols = st.columns([1, 2, 2, 1.5, 1.5, 2, 0.8, 0.8, 0.8])

            payment_id = int(r["PaymentID"])
            
            cols[0].write(payment_id)
            cols[1].write(r["OrderNumber"])
            cols[2].write(str(r["PaymentDate"]).split()[0])
            cols[3].write(f"R$ {float(r['Amount']):,.2f}")
            cols[4].write(r["PaymentMethod"])
            cols[5].write(r["TransactionRef"])

            if cols[6].button("👁", key=f"view{payment_id}", help="View Details", on_click=open_view, args=(payment_id,)):
                pass # Handled by on_click

            if cols[7].button("✏️", key=f"edit{payment_id}", help="Edit", on_click=open_form, args=(payment_id,)):
                pass # Handled by on_click

            if cols[8].button("🗑️", key=f"del{payment_id}", help="Delete"):
                delete_payment(payment_id)
                st.success("Deleted Successfully")
                st.rerun()

    # =================================================================
    # VI. MODAL RENDERING (Conditional Logic)
    # =================================================================
    if st.session_state.show_payment_view and st.session_state.active_payment_id is not None:
        st.markdown("## 📄 Payment Details (Popup)")
        with st.container(border=True):
            render_view_payment_modal(st.session_state.active_payment_id)
            
    if st.session_state.show_payment_form:
        st.markdown(f"## 💳 {'Edit Payment' if st.session_state.active_payment_id else 'Add Payment'} (Popup)")
        with st.container(border=True):
            render_payment_form_modal(st.session_state.active_payment_id)


# =========================================================================================
# VII. MULTIPAGE HOOK
# =========================================================================================
def render_page():
    main()


if __name__ == "__main__":
    main()
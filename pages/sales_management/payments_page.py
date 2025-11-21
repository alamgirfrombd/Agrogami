import streamlit as st
import pandas as pd
from datetime import datetime
from typing import Optional
from db_connect import get_connection

# =========================================================================================
# PAGE CONFIG
# =========================================================================================
st.set_page_config(page_title="Payments Management", page_icon="💳", layout="wide")


# =========================================================================================
# DATABASE FUNCTIONS — PostgreSQL FIXED
# =========================================================================================

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


def delete_payment(payment_id: int):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM public.payments WHERE paymentid=%s", (payment_id,))
    conn.commit()
    conn.close()


# =========================================================================================
# POPUP: VIEW PAYMENT
# =========================================================================================
@st.dialog("📄 Payment Details", width="large")
def view_payment_dialog(payment_id: int):
    row = get_payment_by_id(payment_id)
    if row is None:
        st.error("Payment not found.")
        return

    st.text_input("Payment ID", value=row["PaymentID"], disabled=True)
    st.text_input("Order ID", value=row["OrderID"], disabled=True)
    st.text_input("Order Number", value=row["OrderNumber"], disabled=True)
    st.text_input("Payment Date", value=str(row["PaymentDate"]), disabled=True)
    st.text_input("Amount", value=row["Amount"], disabled=True)
    st.text_input("Method", value=row["PaymentMethod"], disabled=True)
    st.text_input("Transaction Ref", value=row["TransactionRef"], disabled=True)


# =========================================================================================
# POPUP: ADD / EDIT PAYMENT
# =========================================================================================
@st.dialog("💳 Add / Edit Payment", width="large")
def payment_form_dialog(payment_id: Optional[int] = None):

    orders = get_orders_dropdown()
    order_map = orders.set_index("OrderId")["OrderNumber"].to_dict()

    row = get_payment_by_id(payment_id) if payment_id else None
    is_edit = row is not None

    st.subheader("Edit Payment" if is_edit else "Add Payment")

    order_id = st.selectbox(
        "Order",
        options=list(order_map.keys()),
        index=(list(order_map.keys()).index(row["OrderID"]) if is_edit else 0),
        format_func=lambda x: order_map[x],
    )

    payment_date = st.date_input(
        "Payment Date", value=row["PaymentDate"] if is_edit else datetime.now()
    )

    amount = st.number_input(
        "Amount", min_value=0.0, value=float(row["Amount"]) if is_edit else 0.0
    )

    method_list = ["Cash", "Card", "Mobile Banking", "Bank Transfer", "Cheque", "Other"]
    method = st.selectbox(
        "Payment Method",
        method_list,
        index=(method_list.index(row["PaymentMethod"]) if is_edit else 0)
    )

    ref = st.text_input("Transaction Reference", value=row["TransactionRef"] if is_edit else "")

    if st.button("💾 Save Payment", type="primary", use_container_width=True):

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

        st.rerun()


# =========================================================================================
# MAIN PAGE — Payments List
# =========================================================================================
def main():
    st.title("💳 Payments Management")

    st.button("➕ Add Payment", on_click=payment_form_dialog, type="primary", use_container_width=True)

    df = get_payments()

    if df.empty:
        st.info("No payments recorded yet.")
        return

    for _, r in df.iterrows():

        cols = st.columns([1, 2, 2, 2, 1.5, 2, 0.8, 0.8, 0.8])

        cols[0].write(r["PaymentID"])
        cols[1].write(r["OrderNumber"])
        cols[2].write(str(r["PaymentDate"]))
        cols[3].write(float(r["Amount"]))
        cols[4].write(r["PaymentMethod"])
        cols[5].write(r["TransactionRef"])

        if cols[6].button("👁", key=f"view{r['PaymentID']}"):
            view_payment_dialog(int(r["PaymentID"]))

        if cols[7].button("✏️", key=f"edit{r['PaymentID']}"):
            payment_form_dialog(int(r["PaymentID"]))

        if cols[8].button("🗑️", key=f"del{r['PaymentID']}"):
            delete_payment(int(r["PaymentID"]))
            st.success("Deleted Successfully")
            st.rerun()


# =========================================================================================
# MULTIPAGE REQUIRED
# =========================================================================================
def render_page():
    main()


if __name__ == "__main__":
    main()

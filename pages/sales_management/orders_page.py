import streamlit as st
import pandas as pd
from datetime import datetime
from typing import Optional
from db_connect import get_connection

# =========================================================================================
# PAGE CONFIG
# =========================================================================================
st.set_page_config(page_title="Orders Management", page_icon="🛒", layout="wide")


# =========================================================================================
# DATABASE FUNCTIONS (FIXED FOR POSTGRESQL)
# =========================================================================================

def get_orders() -> pd.DataFrame:
    conn = get_connection()
    query = """
        SELECT 
            O.orderid      AS "OrderId",
            O.ordernumber  AS "OrderNumber",
            C.fullname     AS "CustomerName",
            O.orderdate    AS "OrderDate",
            O.status       AS "Status",
            O.subtotal     AS "SubTotal",
            O.discount     AS "Discount",
            O.tax          AS "Tax",
            O.totalamount  AS "TotalAmount"
        FROM public.orders O
        JOIN public.customers C ON O.customerid = C.customerid
        ORDER BY O.orderdate DESC;
    """
    df = pd.read_sql(query, conn)
    conn.close()
    return df


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
        return True, "✅ Order deleted successfully."

    except Exception as e:
        return False, f"❌ Error deleting order: {str(e)}"

    finally:
        conn.close()


# =========================================================================================
# AUTO-GENERATE ORDER NUMBER (FIXED)
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

    last_seq = int(df.iloc[0]["OrderNumber"].split("-")[1])
    return f"{today}-{str(last_seq + 1).zfill(4)}"


# =========================================================================================
# POPUP: ORDER DETAILS
# =========================================================================================
@st.dialog("📄 Order Details", width="large")
def order_details_dialog(order_id: int):
    row = get_order_by_id(order_id)
    if row is None:
        st.error("Order not found.")
        return

    st.text_input("Order Number", row["OrderNumber"], disabled=True)
    st.text_input("Customer ID", row["CustomerID"], disabled=True)
    st.text_input("Order Date", str(row["OrderDate"]), disabled=True)
    st.text_input("Subtotal", row["SubTotal"], disabled=True)
    st.text_input("Discount", row["Discount"], disabled=True)
    st.text_input("Tax", row["Tax"], disabled=True)
    st.text_input("Total", row["TotalAmount"], disabled=True)


# =========================================================================================
# POPUP: ORDER FORM
# =========================================================================================
@st.dialog("📝 Add / Edit Order", width="large")
def order_form_dialog(order_id: Optional[int] = None):

    customers = get_customers()
    customer_map = customers.set_index("CustomerId")["FullName"].to_dict()

    row = get_order_by_id(order_id) if order_id else None
    is_edit = row is not None

    order_number = row["OrderNumber"] if is_edit else generate_order_number()
    order_number = st.text_input("Order Number", order_number, disabled=True)

    customer_id = st.selectbox(
        "Customer",
        list(customer_map.keys()),
        index=list(customer_map.keys()).index(row["CustomerID"]) if is_edit else 0,
        format_func=lambda x: customer_map[x],
    )

    order_date = st.date_input("Order Date", value=row["OrderDate"] if is_edit else datetime.now())

    status_list = ["New", "Pending", "Shipped", "Completed", "Cancelled"]
    status = st.selectbox("Status", status_list,
                          index=status_list.index(row["Status"]) if is_edit else 0)

    c1, c2, c3, c4 = st.columns(4)
    subtotal = c1.number_input("SubTotal", min_value=0.0, value=float(row["SubTotal"]) if is_edit else 0.0)
    discount = c2.number_input("Discount", min_value=0.0, value=float(row["Discount"]) if is_edit else 0.0)
    tax = c3.number_input("Tax", min_value=0.0, value=float(row["Tax"]) if is_edit else 0.0)
    total = subtotal - discount + tax
    c4.number_input("Total Amount", value=total, disabled=True)

    if st.button("💾 Save Order", type="primary", use_container_width=True):

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

        st.rerun()


# =========================================================================================
# MAIN PAGE UI
# =========================================================================================
def main():
    st.title("🛒 Orders Management")
    st.button("➕ Add New Order", type="primary", on_click=order_form_dialog, use_container_width=True)

    df = get_orders()
    if df.empty:
        st.warning("No Orders Found")
        return

    for _, r in df.iterrows():
        with st.container(border=True):
            cols = st.columns([1, 2, 2, 2, 1, 1.5, 0.5, 0.5, 0.5])

            cols[0].write(r["OrderId"])
            cols[1].write(r["OrderNumber"])
            cols[2].write(r["CustomerName"])
            cols[3].write(str(r["OrderDate"]))
            cols[4].write(r["Status"])
            cols[5].write(r["TotalAmount"])

            if cols[6].button("👁", key=f"view{r['OrderId']}"):
                order_details_dialog(int(r["OrderId"]))

            if cols[7].button("✏️", key=f"edit{r['OrderId']}"):
                order_form_dialog(int(r["OrderId"]))

            if cols[8].button("🗑️", key=f"del{r['OrderId']}"):
                success, msg = delete_order(int(r["OrderId"]))
                if success:
                    st.success(msg)
                    st.rerun()
                else:
                    st.error(msg)


# =========================================================================================
# MULTIPAGE HOOK
# =========================================================================================
def render_page():
    main()


if __name__ == "__main__":
    main()

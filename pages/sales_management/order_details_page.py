import streamlit as st
import pandas as pd
from datetime import datetime
from typing import Optional
from db_connect import get_connection

# =========================================================================================
# Page config
# =========================================================================================
st.set_page_config(page_title="Order Items (Order Details)", page_icon="📦", layout="wide")


# =========================================================================================
# Database helpers (FIXED for PostgreSQL)
# =========================================================================================
def get_orders_for_dropdown() -> pd.DataFrame:
    conn = get_connection()
    df = pd.read_sql("""
        SELECT 
            orderid     AS "OrderId",
            ordernumber AS "OrderNumber",
            orderdate   AS "OrderDate"
        FROM public.orders
        ORDER BY orderdate DESC
    """, conn)
    conn.close()
    return df


def get_products() -> pd.DataFrame:
    conn = get_connection()
    df = pd.read_sql("""
        SELECT 
            productid   AS "ProductId",
            sku         AS "SKU",
            productname AS "ProductName",
            unitprice   AS "UnitPrice"
        FROM public.products
        WHERE isactive = TRUE
    """, conn)
    conn.close()
    return df


def get_order_details(order_id: int) -> pd.DataFrame:
    conn = get_connection()
    query = """
        SELECT 
            od.oderdetailid AS "OrderDetailId",
            od.orderid      AS "OrderId",
            od.productid    AS "ProductID",
            p.sku           AS "SKU",
            p.productname   AS "ProductName",
            od.quantity     AS "Quantity",
            od.unitprice    AS "UnitPrice",
            od.linetotal    AS "LineTotal"
        FROM public.orderdetails od
        JOIN public.products p ON od.productid = p.productid
        WHERE od.orderid = %s
        ORDER BY od.oderdetailid ASC
    """
    df = pd.read_sql(query, conn, params=[order_id])
    conn.close()
    return df


def get_order_detail_by_id(detail_id: int):
    conn = get_connection()
    df = pd.read_sql("""
        SELECT 
            od.oderdetailid AS "OrderDetailId",
            od.orderid      AS "OrderId",
            od.productid    AS "ProductID",
            od.quantity     AS "Quantity",
            od.unitprice    AS "UnitPrice",
            od.linetotal    AS "LineTotal",
            p.sku           AS "SKU",
            p.productname   AS "ProductName"
        FROM public.orderdetails od
        JOIN public.products p ON od.productid = p.productid
        WHERE od.oderdetailid = %s
    """, conn, params=[detail_id])
    conn.close()
    return df.iloc[0] if not df.empty else None


def insert_order_detail(data: dict):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO public.orderdetails (orderid, productid, quantity, unitprice)
        VALUES (%s, %s, %s, %s)
    """, (data["OrderId"], data["ProductID"], data["Quantity"], data["UnitPrice"]))
    conn.commit()
    conn.close()


def update_order_detail(detail_id: int, data: dict):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE public.orderdetails
        SET productid=%s, quantity=%s, unitprice=%s
        WHERE oderdetailid=%s
    """, (data["ProductID"], data["Quantity"], data["UnitPrice"], detail_id))
    conn.commit()
    conn.close()


def delete_order_detail(detail_id: int):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM public.orderdetails WHERE oderdetailid=%s", (detail_id,))
    conn.commit()
    conn.close()


# =========================================================================================
# View-only popup
# =========================================================================================
@st.dialog("🔎 Order Item Details", width="large")
def order_detail_view(detail_id: int):
    row = get_order_detail_by_id(detail_id)
    if row is None:
        st.error("Order item not found.")
        return

    st.text_input("Detail ID", value=row["OrderDetailId"], disabled=True)
    st.text_input("Order ID", value=row["OrderId"], disabled=True)
    st.text_input("Product ID", value=row["ProductID"], disabled=True)

    st.text_input("SKU", value=row["SKU"], disabled=True)
    st.text_input("Product Name", value=row["ProductName"], disabled=True)

    st.number_input("Quantity", value=int(row["Quantity"]), disabled=True)
    st.number_input("Unit Price", value=float(row["UnitPrice"]), disabled=True)
    st.number_input("Line Total", value=float(row["LineTotal"]), disabled=True)


# =========================================================================================
# Add/Edit popup
# =========================================================================================
@st.dialog("✏️ Add / Edit Order Item", width="large")
def order_detail_form(detail_id: Optional[int] = None, order_id: Optional[int] = None):

    products = get_products()
    product_map = products.set_index("ProductId").to_dict(orient="index")
    product_ids = list(product_map.keys())

    is_edit = detail_id is not None
    row = get_order_detail_by_id(detail_id) if is_edit else None

    st.header("Edit Item" if is_edit else "Add Item")

    if not is_edit and not order_id:
        st.error("Order ID is required.")
        return

    default_index = 0
    if is_edit:
        try:
            default_index = product_ids.index(row["ProductID"])
        except:
            pass

    prod_choice = st.selectbox(
        "Product (SKU — Name)",
        product_ids,
        index=default_index,
        format_func=lambda x: f"{product_map[x]['SKU']} — {product_map[x]['ProductName']}",
    )

    default_price = float(row["UnitPrice"]) if is_edit else float(product_map[prod_choice]["UnitPrice"])

    unit_price = st.number_input("Unit Price", min_value=0.0, value=default_price)
    quantity = st.number_input("Quantity", min_value=1, value=int(row["Quantity"]) if is_edit else 1)
    line_total = unit_price * quantity

    st.markdown(f"**Line Total:** `{line_total:.2f}`")

    if st.button("💾 Save", type="primary", use_container_width=True):
        data = {
            "OrderId": row["OrderId"] if is_edit else order_id,
            "ProductID": prod_choice,
            "Quantity": quantity,
            "UnitPrice": unit_price,
        }

        if is_edit:
            update_order_detail(detail_id, data)
            st.success("Updated.")
        else:
            insert_order_detail(data)
            st.success("Added.")

        st.rerun()


# =========================================================================================
# Main Page UI
# =========================================================================================
def main():

    st.title("📦 Order Items (Order Details)")

    orders = get_orders_for_dropdown()
    if orders.empty:
        st.warning("No orders found.")
        return

    order_map = orders.set_index("OrderId")["OrderNumber"].to_dict()

    selected_order_id = st.selectbox(
        "Select Order",
        list(order_map.keys()),
        format_func=lambda x: order_map[x]
    )

    st.button("➕ Add Item", on_click=order_detail_form, kwargs={"order_id": selected_order_id})

    df = get_order_details(selected_order_id)
    if df.empty:
        st.info("No items found.")
        return

    st.markdown("### Items")

    for _, r in df.iterrows():
        cols = st.columns([1, 5, 1, 1.2, 1.2, 0.8, 0.8, 0.8])

        cols[0].write(r["OrderDetailId"])
        cols[1].write(f"**{r['SKU']} — {r['ProductName']}**")
        cols[2].write(r["Quantity"])
        cols[3].write(f"{float(r['UnitPrice']):.2f}")
        cols[4].write(f"**{float(r['LineTotal']):.2f}**")

        if cols[5].button("👁", key=f"v{r['OrderDetailId']}"):
            order_detail_view(int(r["OrderDetailId"]))

        if cols[6].button("✏️", key=f"e{r['OrderDetailId']}"):
            order_detail_form(detail_id=int(r["OrderDetailId"]))

        if cols[7].button("🗑️", key=f"d{r['OrderDetailId']}"):
            delete_order_detail(int(r["OrderDetailId"]))
            st.success("Deleted.")
            st.rerun()


# =========================================================================================
# Multipage hook
# =========================================================================================
def render_page():
    main()


if __name__ == "__main__":
    main()

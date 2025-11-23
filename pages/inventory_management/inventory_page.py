import streamlit as st
import pandas as pd
from datetime import datetime
from typing import Optional
from db_connect import get_connection


# ============================================================
# DB FUNCTIONS
# ============================================================

def get_inventory(search: str = "") -> pd.DataFrame:
    conn = get_connection()
    sql = """
        SELECT 
            I.inventoryid   AS "InventoryID",
            I.productid     AS "ProductID",
            P.sku           AS "SKU",
            P.productname   AS "ProductName",
            I.warehouseid   AS "WarehouseID",
            W.warehousename AS "WarehouseName",
            I.stockqty      AS "StockQty",
            I.purchaseprice AS "PurchasePrice",
            I.salesprice    AS "SalesPrice",
            I.lastupdate    AS "LastUpdate"
        FROM public.inventory I
        JOIN public.products P ON I.productid = P.productid
        JOIN public.warehouse W ON I.warehouseid = W.warehouseid
        WHERE P.productname ILIKE %s
        ORDER BY I.inventoryid DESC;
    """
    df = pd.read_sql(sql, conn, params=[f"%{search}%"])
    conn.close()
    return df


def upsert_inventory(product_id: int, warehouse_id: int, qty_delta: int,
                     purchase_price: Optional[float], sales_price: Optional[float]):

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT inventoryid, stockqty 
        FROM public.inventory 
        WHERE productid=%s AND warehouseid=%s
    """, (product_id, warehouse_id))

    row = cur.fetchone()
    now = datetime.utcnow()

    if row:
        inv_id, old_qty = row
        new_qty = old_qty + qty_delta

        if new_qty < 0:
            raise ValueError("Stock cannot be negative.")

        cur.execute("""
            UPDATE public.inventory 
            SET stockqty=%s,
                purchaseprice=COALESCE(%s, purchaseprice),
                salesprice=COALESCE(%s, salesprice),
                lastupdate=%s
            WHERE inventoryid=%s
        """, (new_qty, purchase_price, sales_price, now, inv_id))

    else:
        if qty_delta < 0:
            raise ValueError("Cannot reduce non-existing stock.")

        cur.execute("""
            INSERT INTO public.inventory 
            (productid, warehouseid, stockqty, purchaseprice, salesprice, lastupdate)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (product_id, warehouse_id, qty_delta,
              purchase_price or 0, sales_price or 0, now))

    conn.commit()
    conn.close()


def update_inventory_row(inv_id: int, qty: int, purchase: float, sales: float):

    if qty < 0:
        raise ValueError("Stock cannot be negative.")

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        UPDATE public.inventory 
        SET stockqty=%s, 
            purchaseprice=%s, 
            salesprice=%s, 
            lastupdate=%s
        WHERE inventoryid=%s
    """, (qty, purchase, sales, datetime.utcnow(), inv_id))

    conn.commit()
    conn.close()


def delete_inventory_row(inv_id: int):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        DELETE FROM public.inventory 
        WHERE inventoryid=%s
    """, (inv_id,))

    conn.commit()
    conn.close()


# ============================================================
# MAIN FUNCTION
# ============================================================

def main():
    st.title("Inventory Stock Management")

    # init popup
    if "show_edit" not in st.session_state:
        st.session_state.show_edit = False
        st.session_state.edit_id = None

    st.markdown("### Adjust Stock (IN / OUT)")
    conn = get_connection()

    prod_df = pd.read_sql("""
        SELECT productid AS "ProductId", productname AS "ProductName", sku AS "SKU"
        FROM public.products
        ORDER BY productid;
    """, conn)

    wh_df = pd.read_sql("""
        SELECT warehouseid AS "WarehouseId", warehousename AS "WarehouseName"
        FROM public.warehouse
        ORDER BY warehouseid;
    """, conn)

    conn.close()

    if prod_df.empty or wh_df.empty:
        st.error("No products or warehouses!")
        return

    with st.expander("Add / Reduce Stock", expanded=True):
        with st.form("adjust"):
            pmap = {pid: f"{n} (SKU: {s})" for pid, n, s in zip(prod_df.ProductId, prod_df.ProductName, prod_df.SKU)}

            c1, c2 = st.columns(2)
            pid = c1.selectbox("Product", options=list(pmap.keys()), format_func=lambda x: pmap[x])
            wid = c2.selectbox("Warehouse", wh_df.WarehouseId, format_func=lambda x: wh_df.loc[wh_df.WarehouseId==x, "WarehouseName"].iloc[0])

            c3, c4 = st.columns(2)
            move = c3.radio("Movement", ["IN", "OUT"], horizontal=True)
            qty = c4.number_input("Qty", min_value=1, step=1)

            c5, c6 = st.columns(2)
            pp = c5.number_input("Purchase Price (opt)", min_value=0.0, value=0.0)
            sp = c6.number_input("Sales Price (opt)", min_value=0.0, value=0.0)

            if st.form_submit_button("Apply", type="primary"):
                delta = qty if move == "IN" else -qty
                upsert_inventory(pid, wid, delta, pp if pp > 0 else None, sp if sp > 0 else None)
                st.success("Done!")
                st.rerun()

    st.markdown("### Current Stock")

    search = st.text_input("Search product", "")
    df = get_inventory(search)

    if not df.empty:
        for _, r in df.iterrows():

            with st.container(border=True):
                cols = st.columns([1, 3, 2, 1.2, 1.4, 1.4, 2])

                cols[0].write(f"**ID:** `{r.InventoryID}`")
                cols[1].write(f"**{r.ProductName}**  \nSKU: `{r.SKU}`")
                cols[2].write(f"**{r.WarehouseName}**")
                cols[3].write(f"### {int(r.StockQty)}")
                cols[4].write(f"**৳{r.PurchasePrice:.2f}**")
                cols[5].write(f"**৳{r.SalesPrice:.2f}**")

                with cols[6]:
                    b1, b2 = st.columns(2)

                    if b1.button("✏️", key=f"e{r.InventoryID}", use_container_width=True):
                        st.session_state.show_edit = True
                        st.session_state.edit_id = r.InventoryID
                        st.rerun()

                    if b2.button("🗑️", key=f"d{r.InventoryID}", use_container_width=True, type="secondary"):
                        delete_inventory_row(r.InventoryID)
                        st.rerun()

    st.caption(f"Total records: {len(df)}")

    # ✅ Popup Overlay inside main()
    if st.session_state.show_edit:
        df = get_inventory()
        row = df[df.InventoryID == st.session_state.edit_id].iloc[0]

        st.markdown("""
            <div style="
                position: fixed;
                top: 0; left: 0;
                width: 100%; height: 100%;
                background: rgba(0,0,0,0.5);
                z-index: 9999;
                display: flex;
                justify-content: center;
                align-items: center;">
        """, unsafe_allow_html=True)

        with st.container():
            st.markdown("""
                <div style="background:white; padding:25px; border-radius:10px; width:450px;">
            """, unsafe_allow_html=True)

            with st.form("edit_form_popup"):
                st.subheader("✏️ Edit Inventory")

                qty = st.number_input("Stock Quantity", min_value=0, value=int(row.StockQty))
                p_price = st.number_input("Purchase Price", min_value=0.0, value=float(row.PurchasePrice or 0))
                s_price = st.number_input("Sales Price", min_value=0.0, value=float(row.SalesPrice or 0))

                c1, c2 = st.columns(2)

                if c1.form_submit_button("✅ Update"):
                    update_inventory_row(st.session_state.edit_id, qty, p_price, s_price)
                    st.session_state.show_edit = False
                    st.rerun()

                if c2.form_submit_button("❌ Cancel"):
                    st.session_state.show_edit = False
                    st.rerun()

            st.markdown("</div></div>", unsafe_allow_html=True)


def render_page():
    main()


if __name__ == "__main__":
    main()

import streamlit as st
import pandas as pd
from datetime import datetime
from typing import Optional
from db_connect import get_connection

# =========================================================================================
# I. SESSION STATE & MODAL MANAGEMENT (New)
# =========================================================================================

def init_session_state():
    """Initializes session state variables for modal control."""
    for key, value in {
        "show_detail_view": False,
        "show_detail_form": False,
        "active_detail_id": None
    }.items():
        if key not in st.session_state:
            st.session_state[key] = value

def open_view(detail_id: int):
    """Opens the detail view modal."""
    st.session_state.active_detail_id = detail_id
    st.session_state.show_detail_view = True
    st.session_state.show_detail_form = False

def open_form(detail_id: Optional[int] = None, order_id: Optional[int] = None):
    """Opens the add/edit form modal."""
    # Note: If adding, order_id will be passed directly. If editing, it's retrieved from the detail.
    st.session_state.active_detail_id = detail_id
    st.session_state.selected_order_for_add = order_id # Store order_id for ADD mode
    st.session_state.show_detail_form = True
    st.session_state.show_detail_view = False
    
def close_modals():
    """Closes all modals and reruns the app to refresh."""
    st.session_state.show_detail_view = False
    st.session_state.show_detail_form = False
    st.rerun()


# =========================================================================================
# II. DATABASE HELPERS
# =========================================================================================
@st.cache_data(ttl=60)
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

@st.cache_data(ttl=300)
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

@st.cache_data(ttl=60)
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
    st.cache_data.clear()

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
    st.cache_data.clear()

def delete_order_detail(detail_id: int):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM public.orderdetails WHERE oderdetailid=%s", (detail_id,))
    conn.commit()
    conn.close()
    st.cache_data.clear() # Clear cache on write


# =========================================================================================
# III. MODAL CONTENT FUNCTIONS (Replacing @st.dialog)
# =========================================================================================

def render_order_detail_view(detail_id: int):
    """View-only details for an order item."""
    st.header("🔎 Order Item Details")
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
    
    if st.button("Close View", type="primary", use_container_width=True):
        close_modals()


def render_order_detail_form(detail_id: Optional[int] = None, order_id_for_add: Optional[int] = None):
    # ... (existing setup code)

    products = get_products()
    if products.empty:
        st.error("No active products available to add to an order.")
        return
        
    product_map = products.set_index("ProductId").to_dict(orient="index")
    product_ids = list(product_map.keys())

    is_edit = detail_id is not None
    row = get_order_detail_by_id(detail_id) if is_edit else None

    # --- NEW CHECK ADDED HERE ---
    if is_edit and row is None:
        st.error(f"Order Detail ID {detail_id} not found in the database.")
        # Optionally, close the modal and stop rendering the form
        if st.button("Close"):
             st.session_state.show_detail_form = False
             st.rerun()
        return
    # -----------------------------

    # Determine the Order ID we are working with
    # This line (191) is now safe because we ensured 'row' is not None if 'is_edit' is True
    target_order_id = row["OrderId"] if is_edit else order_id_for_add

    # ... (rest of the function continues below)
    
    

    st.header(f"✏️ {'Edit Item' if is_edit else 'Add Item'}")
    st.markdown(f"**Target Order ID:** `{target_order_id}`")
    st.markdown("---")
    
    if not target_order_id:
        st.error("Order ID is required to add an item.")
        return

    # Set default index for product selection
    default_index = 0
    if is_edit:
        try:
            default_index = product_ids.index(row["ProductID"])
        except ValueError:
            pass # Keep default_index 0 if the product is no longer active

    # --- Product Selection ---
    prod_choice = st.selectbox(
        "Product (SKU — Name)",
        product_ids,
        index=default_index,
        format_func=lambda x: f"{product_map[x]['SKU']} — {product_map[x]['ProductName']}",
        key="product_select"
    )

    # --- Price and Quantity ---
    # Determine the default price based on whether we are editing or adding
    if is_edit:
        default_price = float(row["UnitPrice"])
    else:
        # If adding, use the price from the product map for the selected product
        default_price = float(product_map[prod_choice]["UnitPrice"])

    # Determine the default quantity
    default_quantity = int(row["Quantity"]) if is_edit else 1

    unit_price = st.number_input("Unit Price", min_value=0.0, value=default_price, key="unit_price_input")
    quantity = st.number_input("Quantity", min_value=1, value=default_quantity, step=1, key="quantity_input")
    
    line_total = round(unit_price * quantity, 2)
    st.markdown(f"**Calculated Line Total:** `{line_total:.2f}`")

    # --- Save Button ---
    col_save, col_cancel = st.columns(2)
    with col_save:
        if st.button("💾 Save", type="primary", use_container_width=True):
            data = {
                "OrderId": target_order_id,
                "ProductID": prod_choice,
                "Quantity": quantity,
                "UnitPrice": unit_price,
                "LineTotal": line_total
            }

            if is_edit:
                update_order_detail(detail_id, data)
                st.success("Order item updated successfully!")
            else:
                insert_order_detail(data)
                st.success("New order item added successfully!")
            
            close_modals()

    with col_cancel:
        if st.button("❌ Cancel", use_container_width=True):
            close_modals()


# =========================================================================================
# IV. MAIN PAGE UI
# =========================================================================================
def main():
    init_session_state()

    st.title("📦 Order Items (Order Details)")

    orders = get_orders_for_dropdown()
    if orders.empty:
        st.warning("No orders found in the database. Please create an order first.")
        return

    order_map = orders.set_index("OrderId")["OrderNumber"].to_dict()

    # Get or set the selected order ID in session state
    if "selected_order_id_page" not in st.session_state:
        st.session_state.selected_order_id_page = list(order_map.keys())[0]

    selected_order_id = st.selectbox(
        "Select Order",
        list(order_map.keys()),
        index=list(order_map.keys()).index(st.session_state.selected_order_id_page) if st.session_state.selected_order_id_page in order_map else 0,
        format_func=lambda x: f"{order_map[x]} (ID: {x})",
        key="selected_order_id_page"
    )
    
    # --- Add Item Button ---
    st.button("➕ Add Item", type="primary", 
              on_click=open_form, 
              kwargs={"order_id": selected_order_id})
    st.markdown("---")

    df = get_order_details(selected_order_id)
    if df.empty:
        st.info(f"Order **{order_map[selected_order_id]}** has no items.")
        # Do not return here to allow modals to render if triggered by the button above

    else:
        st.markdown(f"### Items for Order: {order_map[selected_order_id]}")

        # Create a header row for the list
        header_cols = st.columns([1, 5, 1, 1.2, 1.2, 0.8, 0.8, 0.8])
        header_cols[0].markdown("**ID**")
        header_cols[1].markdown("**Product**")
        header_cols[2].markdown("**Qty**")
        header_cols[3].markdown("**Price**")
        header_cols[4].markdown("**Line Total**")

        for _, r in df.iterrows():
            with st.container(border=True):
                cols = st.columns([1, 5, 1, 1.2, 1.2, 0.8, 0.8, 0.8])

                cols[0].write(r["OrderDetailId"])
                cols[1].markdown(f"**{r['SKU']}** — {r['ProductName']}")
                cols[2].write(int(r["Quantity"]))
                cols[3].write(f"${float(r['UnitPrice']):.2f}")
                cols[4].markdown(f"**${float(r['LineTotal']):.2f}**")

                detail_id = int(r["OrderDetailId"])

                if cols[5].button("👁", key=f"v{detail_id}"):
                    open_view(detail_id)

                if cols[6].button("✏️", key=f"e{detail_id}"):
                    open_form(detail_id=detail_id)

                if cols[7].button("🗑️", key=f"d{detail_id}"):
                    delete_order_detail(detail_id)
                    st.success("Item deleted.")
                    st.rerun()

    # =================================================================
    # V. MODAL RENDERING (Conditional Logic)
    # =================================================================
    if st.session_state.show_detail_view and st.session_state.active_detail_id is not None:
        st.markdown("## 🔍 Order Item Details (Popup)")
        with st.container(border=True):
            render_order_detail_view(st.session_state.active_detail_id)
            
    if st.session_state.show_detail_form:
        st.markdown(f"## {'✏️ Edit Item' if st.session_state.active_detail_id else '➕ Add Item'} (Popup)")
        with st.container(border=True):
            render_order_detail_form(
                detail_id=st.session_state.active_detail_id, 
                order_id_for_add=st.session_state.selected_order_for_add
            )


# =========================================================================================
# VI. MULTIPAGE HOOK
# =========================================================================================
def render_page():
    main()


if __name__ == "__main__":
    main()
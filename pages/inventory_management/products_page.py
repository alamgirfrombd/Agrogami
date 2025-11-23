# product_ui.py
# ===========================================================
# IMPORTS
# ===========================================================
import streamlit as st                 # 👉 Streamlit UI framework
import pandas as pd                    # 👉 Data handling
import os                              # 👉 File path operations
from fpdf import FPDF                  # 👉 For generating PDF files (kept as requested)
from io import BytesIO                 # 👉 For handling byte streams (kept as requested)
from db_connect import get_connection  # 👉 Custom function to connect DB

# ===========================================================
# LOAD CSS
# ===========================================================
def load_css():
    """
    Load custom CSS from app/static/style.css if it exists.
    Fallback to inline styles defined in the UI where necessary.
    """
    css_path = os.path.join("app", "static", "style.css")   # 👉 External CSS path
    if os.path.exists(css_path):                             # 👉 Check if file exists
        try:
            with open(css_path, "r", encoding="utf-8") as f:
                st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)  # 👉 Inject CSS into UI
        except Exception:
            # If CSS fails to load, silently ignore (UI still works)
            pass

# ===========================================================
# DATABASE FUNCTIONS (unchanged functionality)
# ===========================================================
def get_products(search=""):
    conn = get_connection()  # 👉 Open DB connection
    query = """
        SELECT P.productid, P.sku, P.productname, P.categoryid, 
               C.categoryname, P.unitprice, P.isactive
        FROM public.products P
        JOIN public.categories C ON P.categoryid = C.categoryid
        WHERE P.productname LIKE %s
        ORDER BY P.productid DESC
    """
    df = pd.read_sql(query, conn, params=[f"%{search}%"])  # 👉 Load into DataFrame
    conn.close()
    return df


def get_categories():
    conn = get_connection()
    df = pd.read_sql("SELECT categoryid, categoryname FROM public.categories", conn)
    conn.close()
    return df


def create_product(sku, name, cat_id, price, active):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        """
        INSERT INTO public.products (sku, productname, categoryid, unitprice, isactive)
        VALUES (%s, %s, %s, %s, %s)
        """,
        (sku, name, cat_id, price, bool(active))
    )

    conn.commit()
    cur.close()
    conn.close()



def update_product(pid, sku, name, category_id, price, active):
    conn = get_connection()
    cur = conn.cursor()

    query = """
        UPDATE public.products
        SET 
            sku = %s,
            productname = %s,
            categoryid = %s,
            unitprice = %s,
            isactive = %s
        WHERE productid = %s
    """

    # 🔥 FIX: active must be True/False (NOT 1/0)
    active_bool = True if active else False

    cur.execute(query, (sku, name, category_id, price, active_bool, pid))

    conn.commit()
    cur.close()
    conn.close()


def delete_product(pid):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        UPDATE public.products
        SET isactive = FALSE
        WHERE productid = %s
    """, (pid,))

    conn.commit()
    cur.close()
    conn.close()


# ===========================================================
# SKU GENERATOR (unchanged functionality)
# ===========================================================
def generate_new_sku(category_name, category_id):
    """
    Generate SKU like PRE-<category_id>01, PRE-<category_id>02 ...
    Keeps previous behavior: first 3 letters uppercase, then -<id><2-digit number>
    """
    if not isinstance(category_name, str) or category_name.strip() == "":
        prefix = "PRO"
    else:
        prefix = category_name[:3].upper()
    cat_prefix = f"{prefix}-{category_id}"

    conn = get_connection()
    df = pd.read_sql("SELECT sku FROM public.products WHERE categoryid = %s", conn, params=[category_id])
    conn.close()

    # Filter SKUs that start with the required prefix
    try:
        df = df[df["sku"].str.startswith(cat_prefix, na=False)]
    except Exception:
        # if SKU column missing or not string, return default
        return f"{prefix}-{category_id}01"

    if df.empty:
        return f"{prefix}-{category_id}01"

    # Extract last 2 digits and increment
    last_numbers = df["sku"].str.extract(r"(\d{2})$")[0].astype(float).fillna(0).astype(int)
    if last_numbers.empty:
        next_number = 1
    else:
        next_number = last_numbers.max() + 1

    return f"{prefix}-{category_id}{next_number:02d}"


# ===========================================================
# UTILITY: Init session state keys used by the page
# ===========================================================
def init_session_state():
    if "edit_open" not in st.session_state:
        st.session_state.edit_open = False
    if "delete_open" not in st.session_state:
        st.session_state.delete_open = False
    if "edit_id" not in st.session_state:
        st.session_state.edit_id = None
    if "delete_id" not in st.session_state:
        st.session_state.delete_id = None


# ===========================================================
# REFRESH BUTTON (kept near top UI)
# ===========================================================
def render_refresh_button():
    refresh_col = st.columns([0.12, 0.88])
    with refresh_col[0]:
        if st.button("🔄 Refresh", help="Refresh Page"):
            st.session_state.clear()               # 👉 Clear session memory
            st.success("Page refreshed!")
            st.rerun()


# ===========================================================
# MAIN PAGE UI (professional rework, functionality unchanged)
# ===========================================================
def render_page():
    # initialize session flags
    init_session_state()

    load_css()   # 👉 Load custom styling

    # Top bar: Title + refresh
    top = st.container()
    with top:
        t1, t2 = st.columns([0.85, 0.15])
        with t1:
            st.markdown(
                "<div style='padding:10px 0 6px 0;'>"
                "<h2 style='margin:0; color:#222;'>🛍️ Product Management</h2>"
                "<div style='color:#666; margin-top:4px;'>Manage products, categories and pricing</div>"
                "</div>",
                unsafe_allow_html=True
            )
        with t2:
            # Refresh inside top-right
            if st.button("🔄"):
                st.session_state.clear()
                st.success("Page refreshed!")
                st.rerun()

    st.markdown("---")

    # -----------------------------
    # ADD PRODUCT CARD
    # -----------------------------
    st.markdown("<div class='card' style='padding:22px; border-radius:12px;'>", unsafe_allow_html=True)
    st.markdown("<h3 style='margin-bottom:6px; color:#333;'>➕ Add New Product</h3>", unsafe_allow_html=True)
    cat_df = get_categories()

    with st.form("add_form"):
        # layout: two rows - first row category & price, second row sku & name
        r1c1, r1c2 = st.columns([2.5, 1])
        with r1c1:
            # select category
            if not cat_df.empty:
                cat_name = st.selectbox("Category", cat_df["categoryname"])
                cat_id = int(cat_df.loc[cat_df["categoryname"] == cat_name, "categoryid"].iloc[0])
            else:
                st.warning("No categories found. Please add categories in the database.")
                cat_name = ""
                cat_id = 0

        with r1c2:
            price = st.number_input("Unit Price", min_value=0.0, step=0.01, format="%.2f")

        r2c1, r2c2 = st.columns([1.8, 2.2])
        with r2c1:
            auto_sku = generate_new_sku(cat_name, cat_id) if cat_name else ""
            sku = st.text_input("SKU (Auto)", auto_sku, disabled=True)
        with r2c2:
            name = st.text_input("Product Name", placeholder="Enter product name...")

        active = st.checkbox("Is Active?", value=True)

        submitted = st.form_submit_button("Add Product")
        if submitted:
            # keep functionality same
            create_product(auto_sku, name, cat_id, price, active)
            st.success("Product added successfully!")
            st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("")  # tiny spacer

    # -----------------------------
    # SEARCH / ACTIONS BAR
    # -----------------------------
    st.markdown("<div class='card' style='padding:12px; border-radius:12px;'>", unsafe_allow_html=True)
    s1, s2, s3 = st.columns([3, 1, 1])
    with s1:
        search = st.text_input("", placeholder="🔍 Search Products by name...", label_visibility="collapsed")
    with s2:
        # export placeholder (kept for future use; not implemented)
        if st.button("Export CSV"):
            # simple export of current search results
            df_export = get_products(search)
            if not df_export.empty:
                csv = df_export.to_csv(index=False).encode('utf-8')
                st.download_button("Download CSV", csv, file_name="products.csv", mime="text/csv")
            else:
                st.info("No data to export.")
    with s3:
        # quick clear search
        if st.button("Clear"):
            search = ""
            st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

    # -----------------------------
    # LOAD PRODUCTS DATA
    # -----------------------------
    df = get_products(search)

    # -----------------------------
    # PRODUCT LIST (professional table-like rows)
    # -----------------------------
    st.markdown("<div class='card' style='padding:16px; border-radius:12px;'>", unsafe_allow_html=True)
    st.markdown("<h3 style='color:#333; margin-bottom:4px;'>📋 Product List</h3>", unsafe_allow_html=True)
    st.markdown("<div style='color:#666; margin-top:-6px; margin-bottom:8px;'>Showing latest products first</div>", unsafe_allow_html=True)

    # Header
    st.markdown("""
        <div style='display:flex; padding:8px 6px; font-weight:600; color:#333;'>
            <div style='width:7%;'>ID</div>
            <div style='width:18%;'>SKU</div>
            <div style='width:36%;'>Product</div>
            <div style='width:22%;'>Category</div>
            <div style='width:8%; text-align:center;'>Edit</div>
            <div style='width:9%; text-align:center;'>Delete</div>
        </div>
        <div style='border-bottom:1px solid #ececec; margin-bottom:6px;'></div>
    """, unsafe_allow_html=True)

    # Rows
    if df.empty:
        st.info("No products found.")
    else:
        for _, row in df.iterrows():
            # use container so buttons align per row
            row_container = st.container()
            c1, c2, c3, c4, c5, c6 = row_container.columns([0.8, 2, 4, 2.4, 0.6, 0.6])

            c1.markdown(f"**{row['productid']}**")
            c2.write(row.get("sku", ""))
            c3.write(row.get("productname", ""))
            c4.write(row.get("categoryname", ""))

            # Edit button
            if c5.button("✏️", key=f"edit_{row['productid']}", help="Edit Product"):
                st.session_state.edit_id = int(row["productid"])
                st.session_state.edit_open = True

            # Delete button
            if c6.button("🗑️", key=f"del_{row['productid']}", help="Delete Product"):
                st.session_state.delete_id = int(row["productid"])
                st.session_state.delete_open = True

    st.markdown("</div>", unsafe_allow_html=True)

    # -----------------------------
    # EDIT POPUP (keeps functionality)
    # -----------------------------
    if st.session_state.edit_open:
        pid = st.session_state.edit_id
        # guard in case df changed
        if pid is None or df.empty or not (df["productid"] == pid).any():
            st.warning("Selected product not found.")
            st.session_state.edit_open = False
        else:
            product = df[df["productid"] == pid].iloc[0]
            st.markdown("<div class='card' style='padding:22px; margin-top:16px; border-left:5px solid #3498db; border-radius:8px;'>", unsafe_allow_html=True)
            st.markdown("<h3 style='color:#2c3e50;'>✏️ Edit Product</h3>", unsafe_allow_html=True)

            with st.form("edit_form"):
                e1, e2 = st.columns([2.5, 1])
                with e1:
                    # category select (keep selected index)
                    if not cat_df.empty:
                        try:
                            selected_index = cat_df["categoryname"].tolist().index(product["categoryname"])
                        except ValueError:
                            selected_index = 0
                        cat_name = st.selectbox("Category", cat_df["categoryname"], index=selected_index)
                        cat_id = int(cat_df.loc[cat_df["categoryname"] == cat_name, "categoryid"].iloc[0])
                    else:
                        st.warning("No categories available.")
                        cat_name = ""
                        cat_id = 0

                with e2:
                    price = st.number_input("Unit Price", value=float(product["unitprice"]), step=0.01, format="%.2f")

                e3, e4 = st.columns([1.6, 2.4])
                with e3:
                    auto_sku = generate_new_sku(cat_name, cat_id) if cat_name else product.get("sku", "")
                    sku = st.text_input("SKU (Auto)", auto_sku, disabled=True)
                with e4:
                    name = st.text_input("Product Name", value=product["productname"])

                active = st.checkbox("Is Active?", value=bool(product["isactive"]))

                b1, b2 = st.columns(2)
                with b1:
                    if st.form_submit_button("Update Product"):
                        update_product(pid, auto_sku, name, cat_id, price, active)
                        st.success("Updated successfully!")
                        st.session_state.edit_open = False
                        st.rerun()
                with b2:
                    if st.form_submit_button("Cancel"):
                        st.session_state.edit_open = False

            st.markdown("</div>", unsafe_allow_html=True)

    # -----------------------------
    # DELETE POPUP (keeps functionality)
    # -----------------------------
    if st.session_state.delete_open:
        pid = st.session_state.delete_id
        if pid is None or df.empty or not (df["productid"] == pid).any():
            st.warning("Selected product not found.")
            st.session_state.delete_open = False
        else:
            product = df[df["productid"] == pid].iloc[0]
            st.markdown("<div class='card' style='padding:20px; margin-top:14px; border-left:5px solid #e74c3c; border-radius:8px;'>", unsafe_allow_html=True)
            st.markdown("<h3 style='color:#c0392b;'>⚠️ Confirm Delete</h3>", unsafe_allow_html=True)

            st.error(f"Are you sure you want to delete **{product['productname']}** (SKU: {product['sku']})?")
            d1, d2 = st.columns(2)
            with d1:
                if st.button("Yes, Delete"):
                    delete_product(pid)
                    st.success("Deleted successfully!")
                    st.session_state.delete_open = False
                    st.rerun()
            with d2:
                if st.button("Cancel"):
                    st.session_state.delete_open = False

            st.markdown("</div>", unsafe_allow_html=True)


# ===========================================================
# RUN PAGE
# ===========================================================
if __name__ == "__main__":
    render_page()

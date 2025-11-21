# Streamlit Category CRUD Application (World-Class UI)
# -------------------------------------------------
# Includes:
# ✔ Modern UI
# ✔ Search Filter
# ✔ Pagination
# ✔ Export (CSV & PDF)
# ✔ Beautiful Card Layout
# ✔ Success/Error Toasts
# ✔ Fully responsive design

import streamlit as st
import pandas as pd
from db_connect import get_connection
from fpdf import FPDF
import math
import os

# ===========================================================
# LOAD CUSTOM CSS
# ===========================================================



def load_css():
    st.markdown(
        """
        <style>
        .card {
            padding: 20px;
            border-radius: 12px;
            background: #ffffff;
            box-shadow: 0px 4px 12px rgba(0,0,0,0.08);
            margin-bottom: 20px;
        }
        .title-text {
            font-size: 24px;
            font-weight: 700;
            color: #222;
        }
        .sub-text {
            font-size: 16px;
            color: #444;
            margin-bottom: 10px;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

# ===========================================================
# READ CATEGORIES
# ===========================================================
def get_categories(search=""):
    conn = get_connection()
    query = "SELECT categoryid, CategoryName FROM public.categories WHERE CategoryName LIKE %s ORDER BY CategoryID DESC"
    return pd.read_sql(query, conn, params=(f"%{search}%",))

# ===========================================================
# CREATE CATEGORY
# ===========================================================
def create_category(name):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO public.categories (CategoryName) VALUES (%s)", (name,))
    conn.commit()
    cursor.close(); conn.close()

# ===========================================================
# UPDATE CATEGORY
# ===========================================================
def update_category(cat_id, new_name):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE public.categories SET CategoryName = %s WHERE categoryid = %s", (new_name, cat_id))
    conn.commit()
    cursor.close(); conn.close()

# ===========================================================
# DELETE CATEGORY
# ===========================================================
def delete_category(cat_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM public.categories WHERE categoryid = %s", (cat_id,))
    conn.commit()
    cursor.close(); conn.close()

# ===========================================================
# EXPORT PDF
# ===========================================================
def export_pdf(df):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    pdf.cell(200, 10, txt="Category List", ln=True, align='C')
    pdf.ln(5)

    for index, row in df.iterrows():
        pdf.cell(0, 10, txt=f"ID: {row['categoryid']} | Name: {row['categoryname']}", ln=True)

    return pdf.output(dest='S').encode('latin-1')

# ===========================================================
# PAGE RENDERING
# ===========================================================
def render_page():
    load_css()

    st.markdown("<div class='title-text'>📦 Category Management</div>", unsafe_allow_html=True)
    st.markdown("<div class='sub-text'>A modern and world-class interface to manage product categories.</div>", unsafe_allow_html=True)

    # ======================= ADD NEW ========================
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.subheader("➕ Add New Category")
    with st.form("add_form"):
        new_cat = st.text_input("Category Name", placeholder="Enter category name...")
        submit = st.form_submit_button("Add Category")
        if submit and new_cat:
            create_category(new_cat)
            st.success("Category added successfully!")
    st.markdown("</div>", unsafe_allow_html=True)


    # ======================= SEARCH =========================
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    search = st.text_input("🔍 Search Category", placeholder="Type to search...")
    df = get_categories(search)
    st.markdown("</div>", unsafe_allow_html=True)

    # ======================= PAGINATION =======================
    items_per_page = 5
    total_items = len(df)
    total_pages = max(1, math.ceil(total_items / items_per_page))

    col1, col2, col3 = st.columns(3)
    with col2:
        page = st.number_input("Page", min_value=1, max_value=total_pages)

    start = (page - 1) * items_per_page
    end = start + items_per_page

    df_page = df.iloc[start:end]

    st.dataframe(df_page, use_container_width=True)

    # ======================= UPDATE ===========================
    if len(df) > 0:
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.subheader("✏️ Update Category")

        selected_id = st.selectbox("Select Category", df["categoryid"])
        old_name = df[df["categoryid"] == selected_id].iloc[0]["categoryname"]
        new_name = st.text_input("New Name", value=old_name)

        if st.button("Update Category"):
            update_category(selected_id, new_name)
            st.success("Category updated successfully!")

        st.markdown("</div>", unsafe_allow_html=True)


    # ======================= DELETE ===========================
    if len(df) > 0:
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.subheader("🗑️ Delete Category")

        del_id = st.selectbox("Select Category to Delete", df[["categoryid", "categoryname"]], key="delete")
        if st.button("Delete Category"):
            delete_category(del_id)
            st.error("Category deleted!")

        st.markdown("</div>", unsafe_allow_html=True)
        

    # ======================= EXPORT ===========================
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.subheader("📤 Export Data")

    col1, col2 = st.columns(2)
    with col1:
        st.download_button("Download CSV", df.to_csv(index=False), "categories.csv")
    with col2:
        st.download_button("Download PDF", export_pdf(df), "categories.pdf")

    st.markdown("</div>", unsafe_allow_html=True)

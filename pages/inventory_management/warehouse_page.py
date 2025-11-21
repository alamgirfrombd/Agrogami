# ===========================================================
# IMPORTS & CONFIGURATION
# ===========================================================
import streamlit as st
import pandas as pd
import os
from db_connect import get_connection

# ===========================================================
# LOAD OPTIONAL CSS (YOU CAN ENABLE LATER)
# ===========================================================
def load_css():
    css_path = os.path.join("app", "static", "style.css")
    if os.path.exists(css_path):
        with open(css_path, "r", encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


# ===========================================================
# DATABASE FUNCTIONS
# ===========================================================
def get_warehouses(search=""):
    conn = get_connection()

    if search:
        query = """
            SELECT 
                warehouseid   AS "WarehouseId",
                warehousename AS "WarehouseName",
                location      AS "Location"
            FROM public.warehouse
            WHERE warehousename ILIKE %s
            ORDER BY warehouseid DESC
        """
        df = pd.read_sql(query, conn, params=[f"%{search}%"])
    else:
        query = """
            SELECT 
                warehouseid   AS "WarehouseId",
                warehousename AS "WarehouseName",
                location      AS "Location"
            FROM public.warehouse
            ORDER BY warehouseid DESC
        """
        df = pd.read_sql(query, conn)

    conn.close()
    return df


def create_warehouse(name, location):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO public.warehouse (warehousename, location)
        VALUES (%s, %s)
    """, (name, location))
    conn.commit()
    conn.close()


def update_warehouse(wid, name, location):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        UPDATE public.warehouse
        SET warehousename = %s, location = %s
        WHERE warehouseid = %s
    """, (name, location, wid))
    conn.commit()
    conn.close()


def delete_warehouse(wid):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM public.warehouse WHERE warehouseid = %s", (wid,))
    conn.commit()
    conn.close()


# ===========================================================
# MAIN PAGE UI
# ===========================================================
def render_page():

    load_css()

    st.markdown("""
        <h2 style='margin-bottom:5px;'>🏬 Warehouse Management</h2>
        <p style='color:#666; margin-top:-8px;'>Manage all warehouses in your inventory</p>
        <hr>
    """, unsafe_allow_html=True)

    # Initialize session states
    if "edit_open" not in st.session_state:
        st.session_state.edit_open = False
    if "delete_open" not in st.session_state:
        st.session_state.delete_open = False

    # =====================================================
    # ADD NEW WAREHOUSE
    # =====================================================
    st.markdown("<div class='card' style='padding:22px;'>", unsafe_allow_html=True)
    st.subheader("➕ Add New Warehouse")

    with st.form("add_form"):
        c1, c2 = st.columns(2)

        with c1:
            name = st.text_input("Warehouse Name", placeholder="Enter warehouse name...")

        with c2:
            location = st.text_input("location", placeholder="Enter location...")

        if st.form_submit_button("Add warehouse"):
            if name.strip() == "":
                st.error("Warehouse name cannot be empty!")
            else:
                create_warehouse(name, location)
                st.success("Warehouse created successfully!")
                st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)

    # =====================================================
    # SEARCH SECTION
    # =====================================================
    st.markdown("<div class='card' style='padding:12px;'>", unsafe_allow_html=True)
    search = st.text_input("", placeholder="🔍 Search Warehouse by Name", label_visibility="collapsed")
    df = get_warehouses(search)
    st.markdown("</div>", unsafe_allow_html=True)

    # =====================================================
    # WAREHOUSE LIST
    # =====================================================
    st.markdown("<div class='card' style='padding:18px;'>", unsafe_allow_html=True)
    st.subheader("📋 Warehouse List")

    if df.empty:
        st.info("No warehouses found.")
    else:
        # Table Header
        st.markdown("""
            <div style='display:flex; font-weight:600; padding:6px;'>
                <div style='width:10%;'>ID</div>
                <div style='width:40%;'>Name</div>
                <div style='width:30%;'>Location</div>
                <div style='width:10%; text-align:center;'>Edit</div>
                <div style='width:10%; text-align:center;'>Del</div>
            </div>
            <hr>
        """, unsafe_allow_html=True)

        # Table Rows
    for _, row in df.iterrows():

        r = st.container()
        c1, c2, c3, c4, c5 = r.columns([1, 4, 3, 1, 1])

        # ✔ Correct column names (use alias!)
        c1.write(f"**{row['WarehouseId']}**")
        c2.write(row["WarehouseName"])
        c3.write(row["Location"])

        # ✔ Correct button keys
        if c4.button("✏️", key=f"edit_{row['WarehouseId']}"):
            st.session_state.edit_id = row["WarehouseId"]
            st.session_state.edit_open = True

        if c5.button("🗑️", key=f"del_{row['WarehouseId']}"):
            st.session_state.delete_id = row["WarehouseId"]
            st.session_state.delete_open = True



    st.markdown("</div>", unsafe_allow_html=True)

    # =====================================================
    # EDIT POPUP
    # =====================================================
    if st.session_state.edit_open:

        wid = st.session_state.edit_id
        row = df[df["WarehouseId"] == wid].iloc[0]


        st.markdown("""
            <div class='card' style='padding:22px; margin-top:18px; border-left:5px solid #3498db;'>
        """, unsafe_allow_html=True)
        st.subheader("✏️ Edit Warehouse")

        with st.form("edit_form"):
            e1, e2 = st.columns(2)

            with e1:
                name = st.text_input("Warehouse Name", row["WarehouseName"])


            with e2:
                location = st.text_input("Location", row["Location"])

            b1, b2 = st.columns(2)

            with b1:
                if st.form_submit_button("Update"):
                    update_warehouse(wid, name, location)
                    st.success("Updated successfully!")
                    st.session_state.edit_open = False
                    st.rerun()

            with b2:
                if st.form_submit_button("Cancel"):
                    st.session_state.edit_open = False

        st.markdown("</div>", unsafe_allow_html=True)

    # =====================================================
    # DELETE POPUP
    # =====================================================
    if st.session_state.delete_open:

        wid = st.session_state.delete_id
        row = df[df["WarehouseId"] == wid].iloc[0]

        st.markdown("""
            <div class='card' style='padding:22px; margin-top:18px; border-left:5px solid #e74c3c;'>
        """, unsafe_allow_html=True)
        st.subheader("⚠️ Confirm Delete")

        st.error(
            f"Are you sure you want to delete **{row['WarehouseName']}** (ID: {row['WarehouseId']})?"
        )

        d1, d2 = st.columns(2)

        with d1:
            if st.button("Yes, Delete"):
                delete_warehouse(wid)
                st.success("Deleted successfully!")
                st.session_state.delete_open = False
                st.rerun()

        with d2:
            if st.button("Cancel"):
                st.session_state.delete_open = False

        st.markdown("</div>", unsafe_allow_html=True)

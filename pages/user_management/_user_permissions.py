# ===========================================================
# USER PERMISSIONS MANAGEMENT (RBAC + BITMASK + CRUD)
# PostgreSQL Corrected Version (FULL WORKING)
# ===========================================================

import os
import pandas as pd
import streamlit as st
from datetime import datetime
from db_connect import get_connection


# ===========================================================
# ENTRY POINT for Home.py
# ===========================================================
def render_page():
    main()


# ===========================================================
# PAGE CONFIG
# ===========================================================
def setup_page():
    st.set_page_config(page_title="User Permissions", page_icon="🔐", layout="wide")
    st.markdown("<h1 class='page-title'>🔐 User Permissions</h1>", unsafe_allow_html=True)


# ===========================================================
# LOAD CSS
# ===========================================================
def load_css(file_name="style.css"):
    current = os.path.abspath(__file__)
    while True:
        current = os.path.dirname(current)
        if "app" in os.listdir(current):
            css_path = os.path.join(current, "app", "static", file_name)
            break

    if os.path.exists(css_path):
        with open(css_path, "r", encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    else:
        st.warning(f"⚠ CSS not found at: {css_path}")


# ===========================================================
# RBAC ROLE CONFIG
# ===========================================================
ROLE_PERMISSIONS = {
    "Admin": dict(view=True, create=True, edit=True, delete=True),
    "Manager": dict(view=True, create=True, edit=True, delete=False),
    "User": dict(view=True, create=False, edit=False, delete=False),
}


# ===========================================================
# BITMASK
# ===========================================================
PERMISSIONS = {"View": 1, "Create": 2, "Edit": 4, "Delete": 8}


def encode_perm(v, c, e, d):
    return (PERMISSIONS["View"] if v else 0) | \
           (PERMISSIONS["Create"] if c else 0) | \
           (PERMISSIONS["Edit"] if e else 0) | \
           (PERMISSIONS["Delete"] if d else 0)


def decode_perm(val):
    return {
        "View": bool(val & 1),
        "Create": bool(val & 2),
        "Edit": bool(val & 4),
        "Delete": bool(val & 8),
    }


# ===========================================================
# MODULE LIST
# ===========================================================
MODULE_LIST = [
    "All",
    "Users", "Roles", "Permissions", "UserProfiles",
    "UserLoginHistory", "AuditLogs",
    "AdminDashboard", "InventoryManagement",
]


# ===========================================================
# DB HELPERS
# ===========================================================
def load_users():
    try:
        conn = get_connection()
        df = pd.read_sql("""
            SELECT userid, username
            FROM public.users
            ORDER BY username
        """, conn)
        conn.close()
        return df
    except:
        return pd.DataFrame()


def table_has_cols(table, cols):
    try:
        conn = get_connection()
        q = f"""
            SELECT column_name
            FROM information_schema.columns
            WHERE table_schema='public' AND table_name='{table.lower()}'
        """
        existing = pd.read_sql(q, conn)["column_name"].str.lower().tolist()
        conn.close()
        return all(c.lower() in existing for c in cols)
    except:
        return False


def load_permissions():
    try:
        conn = get_connection()
        df = pd.read_sql("""
            SELECT permissionid, userid, modulename, permissionvalue, createdat
            FROM public.userpermissions
            ORDER BY permissionid DESC
        """, conn)
        conn.close()
        return df
    except Exception as e:
        st.error(f"Error loading permissions: {e}")
        return pd.DataFrame()


# ===========================================================
# CRUD (PostgreSQL Version)
# ===========================================================
def create_permission(user_id, module, val):
    try:
        conn = get_connection()
        cur = conn.cursor()

        cur.execute("""
            INSERT INTO public.userpermissions (userid, modulename, permissionvalue, createdat)
            VALUES (%s, %s, %s, NOW())
        """, (user_id, module, val))

        conn.commit()
        conn.close()
        st.success("Permission created!")
        return True

    except Exception as e:
        st.error(f"Error: {e}")
        return False


def update_permission(pid, user_id, module, val):
    try:
        conn = get_connection()
        cur = conn.cursor()

        cur.execute("""
            UPDATE public.userpermissions
            SET userid=%s, modulename=%s, permissionvalue=%s, updatedat=NOW()
            WHERE permissionid=%s
        """, (user_id, module, val, pid))

        conn.commit()
        conn.close()
        st.success("Updated!")
        return True

    except Exception as e:
        st.error(f"Error: {e}")
        return False


def delete_permission(pid):
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("DELETE FROM public.userpermissions WHERE permissionid=%s", (pid,))
        conn.commit()
        conn.close()
        st.success("Deleted!")
        return True
    except Exception as e:
        st.error(f"Error: {e}")
        return False


# ===========================================================
# MAIN UI FUNCTION
# ===========================================================
def main():
    setup_page()
    load_css()

    # -------------------------------------------------------
    # Role simulator
    # -------------------------------------------------------
    with st.sidebar:
        st.header("Role Simulator")
        role = st.selectbox("Current Role:", ["Admin", "Manager", "User"])
    ROLE = ROLE_PERMISSIONS.get(role, ROLE_PERMISSIONS["User"])

    users_df = load_users()
    user_map = dict(zip(users_df["username"], users_df["userid"]))
    perm_df = load_permissions()

    # -------------------------------------------------------
    # Search
    # -------------------------------------------------------
    st.subheader("🔎 Search")
    search = st.text_input("Module / Username / UserID")

    if search:
        merged = perm_df.merge(users_df, on="userid", how="left")
        perm_df = merged[merged.apply(
            lambda r: search.lower() in str(r["modulename"]).lower()
                      or search.lower() in str(r["username"]).lower()
                      or search.lower() in str(r["userid"]).lower(),
            axis=1
        )]
    else:
        perm_df = perm_df.merge(users_df, on="userid", how="left")

    # -------------------------------------------------------
    # LIST VIEW
    # -------------------------------------------------------
    st.divider()

    if perm_df.empty:
        st.info("No permission records.")
    else:
        for _, r in perm_df.iterrows():
            st.markdown("<div class='profile-card-row'>", unsafe_allow_html=True)

            c1, c2, c3, c4 = st.columns([2, 2, 3, 2])

            with c1:
                st.write(f"**{r['username']}** (ID: {r['userid']})")

            with c2:
                st.write(r["modulename"])

            with c3:
                decoded = decode_perm(r["permissionvalue"])
                parts = [p for p, v in decoded.items() if v]
                st.write(", ".join(parts) if parts else "—")

            with c4:
                v, e, d = st.columns([1, 1, 1])

                if ROLE["view"] and v.button("VIEW", key=f"v{r['permissionid']}"):
                    st.session_state.view = int(r["permissionid"])
                    st.rerun()

                if ROLE["edit"] and e.button("EDIT", key=f"e{r['permissionid']}"):
                    st.session_state.edit = int(r["permissionid"])
                    st.rerun()

                if ROLE["delete"] and d.button("❌", key=f"d{r['permissionid']}"):
                    st.session_state.delete = int(r["permissionid"])
                    st.rerun()

            st.markdown("</div>", unsafe_allow_html=True)

    # -------------------------------------------------------
    # DELETE CONFIRM
    # -------------------------------------------------------
    if st.session_state.get("delete"):
        pid = st.session_state["delete"]
        st.warning(f"Confirm delete permission #{pid}?")

        yes, no = st.columns(2)
        if yes.button("Yes Delete"):
            delete_permission(pid)
            st.session_state.pop("delete")
            st.rerun()
        if no.button("Cancel"):
            st.session_state.pop("delete")
            st.rerun()

    # -------------------------------------------------------
    # VIEW DETAILS
    # -------------------------------------------------------
    if st.session_state.get("view"):
        pid = st.session_state["view"]
        row = perm_df[perm_df["permissionid"] == pid].iloc[0]

        with st.expander("Permission Details", expanded=True):
            st.json({
                "UserID": row["userid"],
                "UserName": row["username"],
                "Module": row["modulename"],
                "PermissionValue": int(row["permissionvalue"]),
                "Decoded": decode_perm(int(row["permissionvalue"]))
            })

        if st.button("Close"):
            st.session_state.pop("view")
            st.rerun()

    # -------------------------------------------------------
    # EDIT FORM
    # -------------------------------------------------------
    if st.session_state.get("edit"):
        pid = st.session_state["edit"]
        row = perm_df[perm_df["permissionid"] == pid].iloc[0]
        decoded = decode_perm(int(row["permissionvalue"]))

        with st.expander("Edit Permission", expanded=True):
            with st.form("edit_form"):

                user_sel = st.selectbox("User", list(user_map.keys()),
                                        index=list(user_map.values()).index(row["userid"]))
                user_id = user_map[user_sel]

                module_sel = st.selectbox(
                    "Module",
                    MODULE_LIST,
                    index=MODULE_LIST.index(row["modulename"])
                    if row["modulename"] in MODULE_LIST else 0
                )

                c1, c2, c3, c4 = st.columns(4)
                v = c1.checkbox("View", decoded["View"])
                c = c2.checkbox("Create", decoded["Create"])
                e = c3.checkbox("Edit", decoded["Edit"])
                d = c4.checkbox("Delete", decoded["Delete"])

                if st.form_submit_button("Update"):
                    new_val = encode_perm(v, c, e, d)
                    update_permission(pid, user_id, module_sel, new_val)
                    st.session_state.pop("edit")
                    st.rerun()

        if st.button("Cancel Edit"):
            st.session_state.pop("edit")
            st.rerun()

    # -------------------------------------------------------
    # CREATE NEW
    # -------------------------------------------------------
    st.divider()
    st.subheader("➕ Create Permission")

    with st.expander("Add Permission"):

        with st.form("create_perm"):

            user_sel = st.selectbox("User", list(user_map.keys()))
            user_id = user_map[user_sel]

            modules = st.multiselect("Modules", MODULE_LIST, default=["Users"])

            c1, c2, c3, c4 = st.columns(4)
            v = c1.checkbox("View", True)
            c = c2.checkbox("Create")
            e = c3.checkbox("Edit")
            d = c4.checkbox("Delete")

            val = encode_perm(v, c, e, d)

            if st.form_submit_button("Create"):
                targets = MODULE_LIST[1:] if "All" in modules else modules
                for m in targets:
                    create_permission(user_id, m, val)
                st.rerun()

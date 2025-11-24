# ===========================================================
# IMPORTS & CONFIGURATION
# ===========================================================
from db_connect import get_connection
import pandas as pd
import streamlit as st
from datetime import datetime
from fpdf import FPDF
import os


# ===========================================================
# STREAMLIT PAGE CONFIG
# ===========================================================
#st.set_page_config(page_title="Roles Management", page_icon="👥", layout="wide")


# ===========================================================
# PDF EXPORT
# ===========================================================
def dataframe_to_pdf(df, title="Roles Report"):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, title, ln=True, align="C")
    pdf.ln(10)

    pdf.set_font("Arial", "B", 12)
    for col in df.columns:
        pdf.cell(40, 10, str(col), border=1)
    pdf.ln()

    pdf.set_font("Arial", "", 12)
    for _, row in df.iterrows():
        for item in row:
            pdf.cell(40, 10, str(item), border=1)
        pdf.ln()

    return pdf.output(dest="S").encode("latin1")


# ===========================================================
# LOAD ROLES FROM POSTGRESQL
# ===========================================================
def load_roles():
    try:
        conn = get_connection()
        df = pd.read_sql("""
            SELECT 
                roleid,
                rolename,
                description,
                issystemrole,
                createdat,
                updatedat
            FROM public.roles
            ORDER BY roleid
        """, conn)
        conn.close()
        return df

    except Exception as e:
        st.error(f"❌ DB Error: {e}")
        return pd.DataFrame()


# ===========================================================
# FORMAT DATA
# ===========================================================
def format_roles_data(df):
    if df.empty:
        return df

    for c in ["createdat", "updatedat"]:
        if c in df.columns:
            df[c] = pd.to_datetime(df[c]).dt.strftime("%Y-%m-%d %H:%M")

    df["issystemrole"] = df["issystemrole"].apply(lambda x: "✅" if x else "❌")

    return df


# ===========================================================
# PAGE ENTRY
# ===========================================================
def render_page():
    st.title("👥 Roles Management")
    st.caption("System Roles and Permissions")

    # Load roles
    if "roles_data" not in st.session_state:
        st.session_state.roles_data = load_roles()

    roles_df = st.session_state.roles_data

    st.subheader("🎯 Roles List")

    if roles_df.empty:
        st.warning("⚠ No roles found.")
        return

    st.dataframe(format_roles_data(roles_df.copy()),
                 use_container_width=True,
                 hide_index=True)

    # ===========================================================
    # ACTION BUTTONS
    # ===========================================================
    col1, col2, col3 = st.columns([2, 2, 2])

    with col1:
        st.download_button(
            "📥 Export CSV",
            data=roles_df.to_csv(index=False),
            file_name=f"roles_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
            mime="text/csv",
            use_container_width=True
        )

    with col2:
        pdf_bytes = dataframe_to_pdf(roles_df, "Roles Report")
        st.download_button(
            "📥 Export PDF",
            data=pdf_bytes,
            file_name=f"roles_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf",
            mime="application/pdf",
            use_container_width=True
        )

    with col3:
        if st.button("🔄 Refresh", use_container_width=True):
            st.session_state.roles_data = load_roles()
            st.rerun()

    # ===========================================================
    # CREATE ROLE
    # ===========================================================
    st.divider()
    with st.expander("➕ Create New Role"):
        with st.form("create_role_form"):
            role_name = st.text_input("Role Name")
            desc = st.text_area("Description")
            sys_role = st.checkbox("System Role", False)
            submit = st.form_submit_button("Create Role")

            if submit:
                if not role_name.strip():
                    st.error("⚠ Role name required!")
                else:
                    try:
                        conn = get_connection()
                        cur = conn.cursor()

                        # Duplicate Check
                        cur.execute(
                            "SELECT COUNT(*) FROM public.roles WHERE rolename=%s",
                            (role_name,)
                        )
                        exists = cur.fetchone()[0]

                        if exists > 0:
                            st.warning("⚠ Role already exists!")
                        else:
                            cur.execute("""
                                INSERT INTO public.roles
                                (rolename, description, issystemrole, createdat, updatedat)
                                VALUES (%s, %s, %s, NOW(), NOW())
                            """, (role_name.strip(), desc.strip(), sys_role))

                            conn.commit()
                            st.success("✅ Role created!")
                            st.session_state.roles_data = load_roles()

                        cur.close()
                        conn.close()

                    except Exception as e:
                        st.error(f"❌ Error: {e}")

    # ===========================================================
    # EDIT & DELETE ROLE
    # ===========================================================
    st.divider()
    with st.expander("✏️ Edit / 🗑 Delete Role"):

        selected = st.selectbox("Select Role", roles_df["rolename"])
        selected_row = roles_df[roles_df["rolename"] == selected].iloc[0]

        new_name = st.text_input("Role Name", selected_row["rolename"])
        new_desc = st.text_area("Description", selected_row["description"])
        new_sys_role = st.checkbox("System Role", bool(selected_row["issystemrole"]))

        colE, colD = st.columns(2)

        # UPDATE ROLE
        with colE:
            if st.button("💾 Update Role"):
                try:
                    conn = get_connection()
                    cur = conn.cursor()

                    cur.execute("""
                        UPDATE public.roles
                        SET rolename=%s,
                            description=%s,
                            issystemrole=%s,
                            updatedat=NOW()
                        WHERE roleid=%s
                    """, (new_name, new_desc, new_sys_role, int(selected_row["roleid"])))   # FIXED HERE ✔

                    conn.commit()
                    cur.close()
                    conn.close()

                    st.success("✅ Updated!")
                    st.session_state.roles_data = load_roles()
                    st.rerun()

                except Exception as e:
                    st.error(f"❌ Error: {e}")

        # DELETE ROLE
        with colD:
            del_confirm = st.checkbox("Confirm Delete")
            if st.button("🗑 Delete Role"):
                if del_confirm:
                    try:
                        conn = get_connection()
                        cur = conn.cursor()

                        cur.execute(
                            "DELETE FROM public.roles WHERE roleid=%s",
                            (int(selected_row["roleid"]),)     # FIXED HERE ✔
                        )

                        conn.commit()
                        cur.close()
                        conn.close()

                        st.success("🗑 Deleted!")
                        st.session_state.roles_data = load_roles()
                        st.rerun()

                    except Exception as e:
                        st.error(f"❌ Error: {e}")

                else:
                    st.warning("⚠ Please confirm delete first.")

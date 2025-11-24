# ===========================================================
# IMPORTS & CONFIGURATION
# ===========================================================
from db_connect import get_connection
import pandas as pd
import streamlit as st
from datetime import datetime
import re
import bcrypt


# -----------------------------------------------------------
# PAGE CONFIG
# -----------------------------------------------------------
#st.set_page_config(page_title="Users", page_icon="👥", layout="wide")


# -----------------------------------------------------------
# SESSION STATE INITIALIZATION (FIXED)
# -----------------------------------------------------------
if "confirm_delete" not in st.session_state:
    st.session_state.confirm_delete = None

if "edit_user" not in st.session_state:
    st.session_state.edit_user = None


# ===========================================================
# PASSWORD UTILITIES
# ===========================================================
def validate_password_strength(password: str):
    if len(password) < 8:
        return False, "Password must be at least 8 characters long."
    if not re.search(r"[A-Z]", password):
        return False, "Password must include at least one uppercase letter."
    if not re.search(r"[a-z]", password):
        return False, "Password must include at least one lowercase letter."
    if not re.search(r"\d", password):
        return False, "Password must include at least one digit."
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        return False, "Password must include at least one special character."
    return True, "Password is strong."


def hash_password(plain_password: str) -> str:
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(plain_password.encode("utf-8"), salt)
    return hashed.decode("utf-8")


# ===========================================================
# DATABASE FUNCTIONS (POSTGRESQL)
# ===========================================================

def load_roles():
    try:
        conn = get_connection()
        df = pd.read_sql("SELECT roleid, rolename FROM public.roles ORDER BY roleid", conn)
        conn.close()
        return df
    except Exception as e:
        st.error(f"❌ Error loading roles: {e}")
        return pd.DataFrame()


def load_users():
    try:
        conn = get_connection()
        df = pd.read_sql("""
            SELECT 
                userid, username, fullname, email, phonenumber,
                passwordhash, roleid, isactive, lastlogin, createdat, updatedat
            FROM public.users
            ORDER BY userid
        """, conn)
        conn.close()

        df["passwordhash"] = df["passwordhash"].apply(
            lambda x: x[:6] + "..." if isinstance(x, str) else x
        )
        df["isactive"] = df["isactive"].apply(lambda x: "Active" if x else "Inactive")

        return df

    except Exception as e:
        st.error(f"❌ Error loading users: {e}")
        return pd.DataFrame()


def update_user_status(user_id, new_status):
    try:
        conn = get_connection()
        cur = conn.cursor()

        cur.execute("""
            UPDATE public.users
            SET isactive = %s, updatedat = NOW()
            WHERE userid = %s
        """, (new_status, int(user_id)))

        conn.commit()
        conn.close()

        st.success("User status updated!")
    except Exception as e:
        st.error(f"❌ Error updating user: {e}")


def create_user(UserName, FullName, Email, PhoneNumber, raw_password, RoleID, IsActive):
    try:
        ok, msg = validate_password_strength(raw_password)
        if not ok:
            st.error(msg)
            return False

        hashed_pass = hash_password(raw_password)

        conn = get_connection()
        cur = conn.cursor()

        cur.execute("SELECT COUNT(*) FROM public.users WHERE username=%s", (UserName,))
        if cur.fetchone()[0] > 0:
            st.error("❌ Username already exists!")
            return False

        cur.execute("""
            INSERT INTO public.users
            (username, fullname, email, phonenumber, passwordhash, roleid, isactive, createdat, updatedat)
            VALUES (%s, %s, %s, %s, %s, %s, %s, NOW(), NOW())
        """, (UserName, FullName, Email, PhoneNumber, hashed_pass, int(RoleID), bool(IsActive)))

        conn.commit()
        conn.close()

        st.success("✅ User created successfully!")
        return True

    except Exception as e:
        st.error(f"❌ Error creating user: {e}")
        return False


def update_user(user_id, full_name, email, phone, role_id):
    try:
        conn = get_connection()
        cur = conn.cursor()

        cur.execute("""
            UPDATE public.users
            SET fullname=%s, email=%s, phonenumber=%s, roleid=%s, updatedat=NOW()
            WHERE userid=%s
        """, (full_name, email, phone, int(role_id), int(user_id)))

        conn.commit()
        conn.close()

        st.success("User updated successfully!")
        return True

    except Exception as e:
        st.error(f"❌ Error updating user: {e}")
        return False


def delete_user(user_id):
    try:
        conn = get_connection()
        cur = conn.cursor()

        cur.execute("DELETE FROM public.users WHERE userid=%s", (int(user_id),))

        conn.commit()
        conn.close()

        st.success("🗑 User deleted successfully!")
    except Exception as e:
        st.error(f"❌ Error deleting user: {e}")


# ===========================================================
# MAIN SCREEN
# ===========================================================
def main():

    st.title("👥 Users Management")
    st.markdown("Manage and view user information in the system.")

    roles_df = load_roles()
    users_df = load_users()

    if not users_df.empty and not roles_df.empty:
        users_df = users_df.merge(
            roles_df[["roleid", "rolename"]],
            on="roleid",
            how="left"
        )

    st.subheader("User List")

    if users_df.empty:
        st.info("No users found.")
        return

    header_cols = st.columns([2, 3, 3, 3, 2, 2, 2, 2])
    labels = ["UserName", "Full Name", "Role", "Email", "Status", "Action", "Edit", "Delete"]
    for col, label in zip(header_cols, labels):
        col.markdown(f"**{label}**")

    # -------------------------------------------------------
    # USERS LOOP
    # -------------------------------------------------------
    for _, row in users_df.iterrows():

        uid = int(row["userid"])
        col1, col2, col3, col4, col5, col6, col7, col8 = st.columns([2, 3, 3, 3, 2, 2, 2, 2])

        col1.write(f"**{row['username']}**")
        col2.write(row["fullname"])
        col3.write(row.get("rolename", "N/A"))
        col4.write(row["email"])
        col5.write("🟢 Active" if row["isactive"] == "Active" else "🔴 Inactive")

        # Toggle status
        if row["isactive"] == "Active":
            if col6.button("Deactivate", key=f"deact_{uid}"):
                update_user_status(uid, 0)
                st.rerun()
        else:
            if col6.button("Activate", key=f"act_{uid}"):
                update_user_status(uid, 1)
                st.rerun()

        # Edit
        if col7.button("✏️ Edit", key=f"edit_{uid}"):
            st.session_state.edit_user = uid
            st.rerun()

        # Delete
        if col8.button("🗑 Delete", key=f"delete_{uid}"):
            st.session_state.confirm_delete = uid
            st.rerun()

        # DELETE CONFIRM
        if st.session_state.confirm_delete == uid:
            st.warning(f"Are you sure you want to delete **{row['username']}**?")
            a1, a2 = st.columns(2)

            if a1.button("Yes, Delete", key=f"yes_delete_{uid}"):
                delete_user(uid)
                st.session_state.confirm_delete = None
                st.rerun()

            if a2.button("Cancel", key=f"cancel_delete_{uid}"):
                st.session_state.confirm_delete = None
                st.rerun()

        # EDIT POPUP
        if st.session_state.edit_user == uid:
            st.write("### ✏️ Edit User")

            with st.form(f"edit_form_{uid}"):
                new_fullname = st.text_input("Full Name", row["fullname"])
                new_email = st.text_input("Email", row["email"])
                new_phone = st.text_input("Phone", row["phonenumber"])

                role_map = roles_df.set_index("roleid")["rolename"].to_dict()

                new_role = st.selectbox(
                    "Select Role",
                    role_map.keys(),
                    index=list(role_map.keys()).index(int(row["roleid"])),
                    format_func=lambda x: role_map[x]
                )

                if st.form_submit_button("Update User"):
                    update_user(uid, new_fullname, new_email, new_phone, int(new_role))
                    st.session_state.edit_user = None
                    st.rerun()

            if st.button("Cancel Editing", key=f"cancel_edit_{uid}"):
                st.session_state.edit_user = None
                st.rerun()

    # -----------------------------------------------------------
    # CREATE NEW USER
    # -----------------------------------------------------------
    st.divider()
    with st.expander("➕ Create New User"):

        if roles_df.empty:
            st.warning("No roles found!")
        else:
            with st.form("create_user_form"):

                user_name = st.text_input("User Name")
                full_name = st.text_input("Full Name")
                email = st.text_input("Email")
                phone = st.text_input("Phone Number")
                password = st.text_input("Password", type="password")
                confirm_password = st.text_input("Confirm Password", type="password")

                role_map = roles_df.set_index("roleid")["rolename"].to_dict()

                role_id = st.selectbox("User Role", role_map.keys(), format_func=lambda x: role_map[x])

                is_active = st.checkbox("Is Active?", value=True)

                if st.form_submit_button("Create User"):

                    if password != confirm_password:
                        st.error("❌ Passwords do not match!")
                    else:
                        ok = create_user(
                            user_name, full_name, email, phone,
                            password, role_id, int(is_active)
                        )
                        if ok:
                            st.rerun()


# ===========================================================
# EXPORT FUNCTION FOR STREAMLIT NAVIGATION
# ===========================================================
def render_page():
    main()

import streamlit as st
import pandas as pd
from db_connect import get_connection


# ============================================================
# 1. Fetch all accounts
# ============================================================
def get_accounts():
    conn = get_connection()
    df = pd.read_sql(
        """
        SELECT account_id, group_type, account_name, account_code, 
               parent_id, level_id, is_posting, is_active
        FROM chart_of_accounts
        ORDER BY account_id
        """,
        conn,
    )
    conn.close()
    return df


# ============================================================
# 2. Generate Account Code
# ============================================================
def generate_account_code(parent, group):
    conn = get_connection()
    cur = conn.cursor()

    group_prefix = {
        "Asset": "1",
        "Liability": "2",
        "Equity": "3",
        "Income": "4",
        "Expense": "5",
    }[group]

    # ✅ Child account code: parent_code + . + running 5 digit
    if parent:
        cur.execute(
            "SELECT account_code FROM chart_of_accounts WHERE account_id=%s",
            (parent,),
        )
        parent_code = cur.fetchone()[0]

        cur.execute(
            """
            SELECT account_code 
            FROM chart_of_accounts 
            WHERE parent_id=%s 
            ORDER BY account_code DESC 
            LIMIT 1
            """,
            (parent,),
        )
        row = cur.fetchone()
        new_child = "00001" if not row else str(int(row[0].split(".")[-1]) + 1).zfill(5)
        conn.close()
        return f"{parent_code}.{new_child}"

    # ✅ Top level account code: group_prefix + running 5 digit
    cur.execute(
        """
        SELECT account_code 
        FROM chart_of_accounts 
        WHERE group_type=%s AND parent_id IS NULL 
        ORDER BY account_code DESC 
        LIMIT 1
        """,
        (group,),
    )
    row = cur.fetchone()
    new_code = group_prefix + "00000" if not row else str(int(row[0]) + 1).zfill(6)
    conn.close()
    return new_code


# ============================================================
# 3. Insert / Update / Delete
# ============================================================
def insert_account(name, parent, group, posting):
    conn = get_connection()
    cur = conn.cursor()

    # ✅ Level calculate
    level = 1
    if parent:
        cur.execute(
            "SELECT level_id FROM chart_of_accounts WHERE account_id=%s", (parent,)
        )
        level = cur.fetchone()[0] + 1

    # ✅ New code
    code = generate_account_code(parent, group)

    # ✅ Insert new account
    cur.execute(
        """
        INSERT INTO chart_of_accounts 
            (account_name, account_code, parent_id, level_id, group_type, is_posting, is_active)
        VALUES (%s, %s, %s, %s, %s, %s, TRUE)
        """,
        (name, code, parent, level, group, posting),
    )

    # ======================================
    #  🔥 Posting Rule: Parent Auto Non-Posting
    # ======================================
    # ✅ If this is a child → make parent NON-posting
    if parent:

        # প্রথমে parent-এর current posting status check (optional but safe)
        cur.execute(
            "SELECT is_posting FROM chart_of_accounts WHERE account_id = %s",
            (parent,)
        )
        current_posting = cur.fetchone()

        # যদি parent এখনো posting=True থাকে → child ঢোকার সাথে সাথে FALSE করব
        if current_posting and current_posting[0] == True:

            cur.execute(
                """
                UPDATE chart_of_accounts
                SET is_posting = FALSE
                WHERE account_id = %s
                """,
                (parent,),
            )
    # ============================================================

    # ====== SAVE CHANGES AND CLOSE ======

    conn.commit()
    conn.close()


def update_account(account_id, name, parent, group, posting):
    conn = get_connection()
    cur = conn.cursor()

    # ✅ Level recalc from parent
    level = 1
    if parent:
        cur.execute(
            "SELECT level_id FROM chart_of_accounts WHERE account_id=%s", (parent,)
        )
        level = cur.fetchone()[0] + 1

    # ✅ Simple update (posting user controlled)
    cur.execute(
        """
        UPDATE chart_of_accounts SET 
            account_name=%s, parent_id=%s, level_id=%s, group_type=%s, is_posting=%s
        WHERE account_id=%s
        """,
        (name, parent, level, group, posting, account_id),
    )

    conn.commit()
    conn.close()


def delete_account(account_id):
    conn = get_connection()
    cur = conn.cursor()

    # ✅ Check if account has children
    cur.execute(
        "SELECT COUNT(*) FROM chart_of_accounts WHERE parent_id=%s", (account_id,)
    )
    child_count = cur.fetchone()[0]

    # ✅ Block delete if children exist
    if child_count > 0:
        conn.close()
        return False

    # ✅ Safe to delete
    cur.execute("DELETE FROM chart_of_accounts WHERE account_id=%s", (account_id,))
    conn.commit()
    conn.close()
    return True


# ============================================================
# 4. Helper
# ============================================================
def get_group_type_by_id(account_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT group_type FROM chart_of_accounts WHERE account_id=%s", (account_id,)
    )
    row = cur.fetchone()
    conn.close()
    return row[0] if row else None


# ============================================================
# 5. Add New Account Form
# ============================================================
def add_new_account_form(df):

    st.markdown("### ➕ Create New Account")

    # ACCOUNT NAME
    name = st.text_input("Account Name", key="new_name")

    # ============================
    # Parent dropdown (FULL DF)
    # ============================
    full_df = get_accounts()   # filtered df ব্যবহার করা যাবে না

    options = [("-- Top Level --", None)]
    for _, r in full_df.iterrows():
        indent = "    " * (r["level_id"] - 1)
        options.append(
            (f"{indent}└ {r['account_code']} - {r['account_name']}", r["account_id"])
        )

    selected = st.selectbox(
        "Parent Account", options, format_func=lambda x: x[0], key="new_parent"
    )
    parent_id = selected[1]

    # ============================
    # Group Logic (Inherited)
    # ============================
    if parent_id:
        group = get_group_type_by_id(parent_id)
        st.info(f"Group Type (Inherited Automatically): **{group}**")
    else:
        group = st.selectbox(
            "Group Type",
            ["Asset", "Liability", "Equity", "Income", "Expense"],
            key="new_group",
        )

    # ============================
    # Posting Logic (Correct rule)
    # ============================
    if parent_id:  # child account ALWAYS posting
        posting = True
        st.info("Posting Account: Automatically TRUE for child accounts.")
    else:
        posting = st.checkbox("Posting Account?", value=True, key="new_posting")

    # ============================
    # Create Button (BOTTOM)
    # ============================
    if st.button("Create Account", key="btn_create_new"):
        st.session_state.add_trigger = True
        st.session_state.edit_mode = None
        st.session_state.delete_mode = None
        st.rerun()

    return name.strip(), parent_id, group, posting


# ============================================================
# 6. Main Page
# ============================================================
def render_page():
    if "add_trigger" not in st.session_state:
        st.session_state.add_trigger = False

    # === Session state for Edit & Delete ===
    if "edit_mode" not in st.session_state:
        st.session_state.edit_mode = None
    if "delete_mode" not in st.session_state:
        st.session_state.delete_mode = None
    
    st.title("Chart of Accounts")

    df = get_accounts()
    if df.empty:
        st.info("No accounts yet. Create the first one!")
        df = pd.DataFrame(
            columns=[
                "account_id",
                "account_name",
                "account_code",
                "group_type",
                "parent_id",
                "level_id",
                "is_posting",
                "is_active",
            ]
        )

    # ✅ Two filters in one row
    col1, col2 = st.columns(2)

    # ✅ Filter 1: Group Type
    group_options = ["-- All Groups --"] + df["group_type"].unique().tolist()
    selected_group = col1.selectbox("Filter by Group Type", group_options)

    if selected_group != "-- All Groups --":
        df = df[df["group_type"] == selected_group]

    # ✅ Filter 2: Account Name (Full path - only leaf accounts)
    all_parents = df["parent_id"].dropna().unique()
    last_level_df = df[~df["account_id"].isin(all_parents)]

    def build_chain(row, full_df):
        chain = []
        current = row
        while True:
            chain.append(f"{current['account_name']}:{current['account_code']}")
            if pd.isna(current["parent_id"]):
                break
            parent_df = full_df[full_df["account_id"] == current["parent_id"]]
            if parent_df.empty:  # Fix: Check if parent exists in full_df
                break
            current = parent_df.iloc[0]
        chain.reverse()
        return " - ".join(chain)

    if not last_level_df.empty:
        last_level_df = last_level_df.copy()
        last_level_df["full_chain"] = last_level_df.apply(
            lambda r: build_chain(r, df), axis=1
        )
        name_options = ["-- All Accounts --"] + last_level_df["full_chain"].tolist()
    else:
        name_options = ["-- All Accounts --"]

    selected_name = col2.selectbox("Filter by Account (Full Path)", name_options)

    if selected_name != "-- All Accounts --":
        last_segment = selected_name.split(" - ")[-1]
        last_account_name = last_segment.split(":", 1)[0]
        df = df[df["account_name"] == last_account_name]
        
    # ============================================================
    # ==== ADD NEW ACCOUNT FORM SECTION ====
    # ============================================================
    # Always use full chart for the form
    full_df = get_accounts()

    name, parent_id, group, posting = add_new_account_form(full_df)

    if st.session_state.add_trigger:
        if not name:
            st.error("Account name is required!")
        else:
            # validate parent still exists in full_df
            if parent_id and parent_id not in full_df["account_id"].tolist():
                st.error("Selected parent no longer exists or invalid. Please re-select parent.")
            else:
                insert_account(name, parent_id, group, posting)
                st.success("Account Created Successfully!")

        st.session_state.add_trigger = False
        st.rerun()

    # ============================================================
    # ==== Header ====
    # ============================================================
    # ✅ Header
    header_html = """
    <div style='
        border:1px solid #ccc;
        padding:6px 8px;
        font-weight:600;
        background:#f2f2f2;
        font-size:14px;
    '>
        TABLE_HEADER
    </div>
    """

    h1, h2, h3, h4, h5, h6, h7, h8 = st.columns([1, 2, 5, 3, 1, 1, 1, 2])
    h1.markdown(header_html.replace("TABLE_HEADER", "ID"), unsafe_allow_html=True)
    h2.markdown(header_html.replace("TABLE_HEADER", "Type"), unsafe_allow_html=True)
    h3.markdown(header_html.replace("TABLE_HEADER", "Name"), unsafe_allow_html=True)
    h4.markdown(header_html.replace("TABLE_HEADER", "Code"), unsafe_allow_html=True)
    h5.markdown(header_html.replace("TABLE_HEADER", "Level"), unsafe_allow_html=True)
    h6.markdown(header_html.replace("TABLE_HEADER", "Posting"), unsafe_allow_html=True)
    h7.markdown(header_html.replace("TABLE_HEADER", "Active"), unsafe_allow_html=True)
    h8.markdown(header_html.replace("TABLE_HEADER", "Action"), unsafe_allow_html=True)

    # ✅ Display Rows
    for _, row in df.iterrows():
        pad = (row["level_id"] - 1) * 18
        name_display = f"<div style='padding-left:{pad}px;'>{row['account_name']}</div>"

        cell_html = """
        <div style='
            border:1px solid #ddd;
            padding:6px 8px;
            font-size:13px;
            background:#ffffff;
        '>
            {}
        </div>
        """

        c1, c2, c3, c4, c5, c6, c7, c8 = st.columns([1, 2, 5, 3, 1, 1, 1, 2])

        c1.markdown(cell_html.format(row["account_id"]), unsafe_allow_html=True)
        c2.markdown(cell_html.format(row["group_type"]), unsafe_allow_html=True)
        c3.markdown(cell_html.format(name_display), unsafe_allow_html=True)
        c4.markdown(cell_html.format(row["account_code"]), unsafe_allow_html=True)
        c5.markdown(cell_html.format(row["level_id"]), unsafe_allow_html=True)
        c6.markdown(
            cell_html.format("Yes" if row["is_posting"] else "No"),
            unsafe_allow_html=True,
        )
        c7.markdown(
            cell_html.format("Yes" if row["is_active"] else "No"),
            unsafe_allow_html=True,
        )

        #=============================================================
        # Edit and Delete Button 
        #============================================================
        # === Action Buttons (Edit & Delete) ===
        edit_btn, delete_btn = c8.columns([1, 1])

        # Edit Button
        if edit_btn.button("✏️", key=f"edit_trigger_{row['account_id']}"):
            st.session_state.edit_mode = row['account_id']
            st.rerun()

        # Delete Button
        if delete_btn.button("🗑", key=f"del_trigger_{row['account_id']}"):
            st.session_state.delete_mode = row['account_id']
            st.rerun()

        # === Edit Form (Only show if in edit mode) ===
        if st.session_state.edit_mode == row['account_id']:
            with st.expander(f"Editing → {row['account_name']}", expanded=True):
                new_name = st.text_input(
                    "Name", value=row["account_name"], key=f"edit_name_{row['account_id']}"
                )

                par_opts = [("-- Top Level --", None)]
                for _, r in df.iterrows():
                    if r["account_id"] == row['account_id']:
                        continue  # নিজেকে parent বানাতে দেব না
                    ind = "    " * (r["level_id"] - 1)
                    par_opts.append(
                        (f"{ind}└ {r['account_code']} - {r['account_name']}", r["account_id"])
                    )
                idx = next((i for i, v in enumerate(par_opts) if v[1] == row["parent_id"]), 0)
                
                selected_parent = st.selectbox(
                    "Parent",
                    par_opts,
                    index=idx,
                    format_func=lambda x: x[0],
                    key=f"edit_parent_{row['account_id']}",
                )
                new_parent = selected_parent[1]

                st.text_input("Group Type", value=row["group_type"], disabled=True)
                new_posting = st.checkbox(
                    "Posting Account?",
                    value=bool(row["is_posting"]),
                    key=f"edit_posting_{row['account_id']}",
                )

                col_a, col_b = st.columns(2)
                if col_a.button("Save Changes", key=f"save_edit_{row['account_id']}"):
                    update_account(
                        row["account_id"],
                        new_name.strip(),
                        new_parent,
                        row["group_type"],
                        new_posting,
                    )
                    st.success("Updated successfully!")
                    st.session_state.edit_mode = None
                    st.rerun()

                if col_b.button("Cancel", key=f"cancel_edit_{row['account_id']}"):
                    st.session_state.edit_mode = None
                    st.rerun()

        # === Delete Confirmation ===
        if st.session_state.delete_mode == row['account_id']:
            with st.expander(f"Delete {row['account_name']}?", expanded=True):
                st.error(f"Permanently delete **{row['account_name']}**?")
                col1, col2 = st.columns(2)
                if col1.button("Yes, Delete", type="primary", key=f"confirm_del_{row['account_id']}"):
                    success = delete_account(row['account_id'])
                    if success:
                        st.success("Deleted!")
                    else:
                        st.error("Cannot delete: This account has child accounts.")
                    st.session_state.delete_mode = None
                    st.rerun()
                if col2.button("Cancel", key=f"cancel_del_{row['account_id']}"):
                    st.session_state.delete_mode = None
                    st.rerun()

# ============================================================
# Run
# ============================================================
if __name__ == "__main__":
    st.set_page_config(page_title="Chart of Accounts", layout="wide")
    render_page()
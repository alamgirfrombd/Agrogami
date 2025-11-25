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
        ORDER BY account_code
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

    if parent:
        cur.execute(
            "SELECT account_code FROM chart_of_accounts WHERE account_id=%s", (parent,)
        )
        parent_code = cur.fetchone()[0]
        cur.execute(
            "SELECT account_code FROM chart_of_accounts WHERE parent_id=%s ORDER BY account_code DESC LIMIT 1",
            (parent,),
        )
        row = cur.fetchone()
        new_child = "00001" if not row else str(int(row[0].split(".")[-1]) + 1).zfill(5)
        conn.close()
        return f"{parent_code}.{new_child}"

    cur.execute(
        "SELECT account_code FROM chart_of_accounts WHERE group_type=%s AND parent_id IS NULL ORDER BY account_code DESC LIMIT 1",
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
    level = 1
    if parent:
        cur.execute(
            "SELECT level_id FROM chart_of_accounts WHERE account_id=%s", (parent,)
        )
        level = cur.fetchone()[0] + 1
    code = generate_account_code(parent, group)
    cur.execute(
        """
        INSERT INTO chart_of_accounts 
        (account_name, account_code, parent_id, level_id, group_type, is_posting, is_active)
        VALUES (%s, %s, %s, %s, %s, %s, TRUE)
    """,
        (name, code, parent, level, group, posting),
    )
    conn.commit()
    conn.close()


def update_account(account_id, name, parent, group, posting):
    conn = get_connection()
    cur = conn.cursor()
    level = 1
    if parent:
        cur.execute(
            "SELECT level_id FROM chart_of_accounts WHERE account_id=%s", (parent,)
        )
        level = cur.fetchone()[0] + 1
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
    cur.execute("DELETE FROM chart_of_accounts WHERE account_id=%s", (account_id,))
    conn.commit()
    conn.close()


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
    st.markdown("### Add New Account")
    name = st.text_input("Account Name", key="new_name")

    options = [("-- Top Level --", None)]
    for _, r in df.iterrows():
        indent = "    " * (r["level_id"] - 1)
        options.append(
            (f"{indent}└ {r['account_code']} - {r['account_name']}", r["account_id"])
        )

    selected = st.selectbox(
        "Parent Account", options, format_func=lambda x: x[0], key="new_parent"
    )
    parent_id = selected[1]

    if parent_id:
        group = get_group_type_by_id(parent_id)
        st.info(f"Group Type (Inherited): **{group}**")
    else:
        group = st.selectbox(
            "Group Type",
            ["Asset", "Liability", "Equity", "Income", "Expense"],
            key="new_group",
        )

    posting = st.checkbox("Posting Account?", value=True, key="new_posting")
    return name.strip(), parent_id, group, posting


# ============================================================
# 6. Main Page
# ============================================================
def render_page():
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

    # ✅ Filter 2: Account Name (depends on group)

    # ✅ Determine last-level accounts (no children)
    all_parents = df["parent_id"].dropna().unique()
    last_level_df = df[~df["account_id"].isin(all_parents)]

    # ✅ Function to build full chain
    def build_chain(row, full_df):
        chain = []
        current = row
        while True:
            chain.append(f"{current['account_name']}:{current['account_code']}")
            if pd.isna(current["parent_id"]):
                break
            current = full_df[full_df["account_id"] == current["parent_id"]].iloc[0]
        chain.reverse()
        return " - ".join(chain)

    # ✅ Create concatenation column
    last_level_df["full_chain"] = last_level_df.apply(lambda r: build_chain(r, df), axis=1)

    # ✅ Dropdown Options (Full Path)
    name_options = ["-- All Accounts --"] + last_level_df["full_chain"].tolist()
    selected_name = col2.selectbox("Filter by Account (Full Path)", name_options)

    # ✅ Apply filter
    if selected_name != "-- All Accounts --":
        last_segment = selected_name.split(" - ")[-1]  # get last part
        last_account_name = last_segment.split(":", 1)[0]
        df = df[df["account_name"] == last_account_name]
    


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

        edit_btn, delete_btn = c8.columns([0.8, 0.8])

        if edit_btn.button("✏️", key=f"edit_{row['account_id']}"):
            with st.expander(f"Editing → {row['account_name']}", expanded=True):
                new_name = st.text_input(
                    "Name", value=row["account_name"], key=f"n_{row['account_id']}"
                )
                par_opts = [("-- Top Level --", None)]
                for _, r in df.iterrows():
                    ind = "    " * (r["level_id"] - 1)
                    par_opts.append(
                        (
                            f"{ind}└ {r['account_code']} - {r['account_name']}",
                            r["account_id"],
                        )
                    )
                idx = next(
                    (i for i, v in enumerate(par_opts) if v[1] == row["parent_id"]), 0
                )
                new_parent = st.selectbox(
                    "Parent",
                    par_opts,
                    index=idx,
                    format_func=lambda x: x[0],
                    key=f"p_{row['account_id']}",
                )[1]

                st.text_input("Group Type", value=row["group_type"], disabled=True)
                new_posting = st.checkbox(
                    "Posting Account?",
                    value=bool(row["is_posting"]),
                    key=f"post_{row['account_id']}",
                )

                if st.button("Save Changes", key=f"save_{row['account_id']}"):
                    update_account(
                        row["account_id"],
                        new_name,
                        new_parent,
                        row["group_type"],
                        new_posting,
                    )
                    st.success("Updated!")
                    st.rerun()

        if delete_btn.button("🗑", key=f"del_{row['account_id']}"):
            with st.expander("Confirm Delete", expanded=True):
                st.error(f"Delete **{row['account_name']}** permanently?")
                col1, col2 = st.columns(2)
                if col1.button(
                    "Yes, Delete", type="primary", key=f"yesdel_{row['account_id']}"
                ):
                    delete_account(row["account_id"])
                    st.success("Deleted!")
                    st.rerun()
                if col2.button("Cancel", key=f"nod_{row['account_id']}"):
                    st.rerun()

    st.markdown("---")
    name, parent, group, posting = add_new_account_form(df)

    if st.button("Create New Account", type="primary", use_container_width=True):
        if not name:
            st.error("Account name is required!")
        else:
            insert_account(name, parent, group, posting)
            st.success(f"Account '{name}' created!")
            st.rerun()

# ============================================================
# Run
# ============================================================
if __name__ == "__main__":
    st.set_page_config(page_title="Chart of Accounts", layout="wide")
    render_page()

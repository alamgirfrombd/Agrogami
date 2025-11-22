import streamlit as st
import pandas as pd
from datetime import datetime
from typing import Optional, Tuple
from db_connect import get_connection


# =========================================================================================
# PAGE CONFIG
# =========================================================================================
#st.set_page_config(page_title="Customers Management", page_icon="👥", layout="wide")


# =========================================================================================
# AUTO CUSTOMER CODE (CUST-000001)
# =========================================================================================
def generate_customer_code() -> str:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT ISNULL(MAX(CustomerId), 0) FROM Customers;")
    last_id = cur.fetchone()[0]
    conn.close()

    next_id = last_id + 1
    return f"CUST-{next_id:06d}"


# =========================================================================================
# DATABASE FUNCTIONS
# =========================================================================================
def get_customers():
    conn = get_connection()
    df = pd.read_sql("""
        SELECT 
            customerid    AS "CustomerId",
            customercode  AS "CustomerCode",
            fullname      AS "FullName",
            contactphone  AS "ContactPhone",
            email         AS "Email",
            city          AS "City",
            nid           AS "NID",
            isactive      AS "IsActive"
        FROM public.customers
        ORDER BY customerid DESC
    """, conn)
    conn.close()
    return df


def get_customer_by_id(cid: int):
    conn = get_connection()
    df = pd.read_sql("""
        SELECT 
            customerid    AS "CustomerId",
            customercode  AS "CustomerCode",
            fullname      AS "FullName",
            contactphone  AS "ContactPhone",
            email         AS "Email",
            city          AS "City",
            nid           AS "NID",
            isactive      AS "IsActive"
        FROM public.customers
        WHERE customerid = %s
    """, conn, params=[cid])
    conn.close()
    return df.iloc[0] if not df.empty else None


def create_customer(data: dict):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO public.customers
        (customercode, fullname, contactphone, email,
         createddate, city, nid, isactive)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """, (
        data["CustomerCode"], data["FullName"], data["ContactPhone"],
        data["Email"], datetime.utcnow(), data["City"], data["NID"],
        data["IsActive"]
    ))

    conn.commit()
    conn.close()



def update_customer(cid: int, data: dict):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        UPDATE public.customers SET
            fullname=%s, contactphone=%s, email=%s, city=%s, nid=%s,
            isactive=%s, updateddate=%s
        WHERE customerid=%s
    """, (
        data["FullName"], data["ContactPhone"], data["Email"], data["City"],
        data["NID"], data["IsActive"], datetime.utcnow(), cid
    ))

    conn.commit()
    conn.close()



def delete_customer(cid: int) -> Tuple[bool, str]:
    conn = get_connection()
    cur = conn.cursor()

    try:
        cur.execute("SELECT COUNT(*) FROM public.orders WHERE customerid=%s", (cid,))
        used = cur.fetchone()[0]

        if used > 0:
            return False, "❌ This Customer cannot be deleted because it is already used in Orders."

        cur.execute("DELETE FROM public.customers WHERE customerid=%s", (cid,))
        conn.commit()
        return True, "✅ Customer deleted successfully."

    except Exception as e:
        return False, f"Error: {str(e)}"

    finally:
        conn.close()



# =========================================================================================
# CUSTOMER DETAILS POPUP
# =========================================================================================
@st.dialog("👁 Customer Details", width="large")
def view_customer(cid: int):
    row = get_customer_by_id(cid)
    if row is None:
        st.error("Customer not found.")
        return

    st.subheader("Basic Info")
    c1, c2 = st.columns(2)
    c1.text_input("Customer Code", row.CustomerCode, disabled=True)
    c2.text_input("Full Name", row.FullName, disabled=True)

    st.subheader("Contact Info")
    c3, c4 = st.columns(2)
    c3.text_input("Phone", row.ContactPhone or "", disabled=True)
    c4.text_input("Email", row.Email or "", disabled=True)

    st.subheader("Address Info")
    st.text_input("City", row.City or "", disabled=True)
    st.text_input("NID", row.NID or "", disabled=True)

    st.subheader("Status")
    st.checkbox("Active", value=bool(row.IsActive), disabled=True)


# =========================================================================================
# ADD / EDIT POPUP
# =========================================================================================
@st.dialog("✏️ Add / Edit Customer", width="large")
def customer_form(cid: Optional[int] = None):
    row = get_customer_by_id(cid) if cid else None
    is_edit = row is not None

    st.subheader("Edit Customer" if is_edit else "Add Customer")

    cust_code = row.CustomerCode if is_edit else generate_customer_code()

    c1, c2 = st.columns(2)
    c1.text_input("Customer Code", cust_code, disabled=True)
    fullname = c2.text_input("Full Name", value=row.FullName if is_edit else "")

    phone = st.text_input("Phone", value=row.ContactPhone if is_edit else "")
    email = st.text_input("Email", value=row.Email if is_edit else "")

    city = st.text_input("City", value=row.City if is_edit else "")
    nid = st.text_input("NID", value=row.NID if is_edit else "")

    active = st.checkbox("Active", value=bool(row.IsActive) if is_edit else True)

    if st.button("💾 Save", type="primary", use_container_width=True):

        data = {
            "CustomerCode": cust_code,
            "FullName": fullname,
            "ContactPhone": phone,
            "Email": email,
            "City": city,
            "NID": nid,
            "IsActive": 1 if active else 0,
        }

        if is_edit:
            update_customer(cid, data)
            st.success("Customer Updated Successfully")
        else:
            create_customer(data)
            st.success("Customer Added Successfully")

        st.rerun()


# =========================================================================================
# MAIN PAGE (Order Details Style)
# =========================================================================================
def main():

    st.title("👥 Customers Management")

    st.button("➕ Add Customer", type="primary", on_click=customer_form)

    df = get_customers()
    if df.empty:
        st.info("No customers found.")
        return

    st.markdown("### Customers List")

    header = st.columns([0.8, 1.2, 2, 1.5, 2, 1.3, 1, 1.2])
    header[0].markdown("**ID**")
    header[1].markdown("**Code**")
    header[2].markdown("**Full Name**")
    header[3].markdown("**Phone**")
    header[4].markdown("**Email**")
    header[5].markdown("**City**")
    header[6].markdown("**NID**")
    header[7].markdown("**Actions**")

    st.markdown("---")

    for _, r in df.iterrows():

        cols = st.columns([0.8, 1.2, 2, 1.5, 2, 1.3, 1, 1.2])

        cols[0].markdown(f"{r['CustomerId']}")
        cols[1].markdown(f"**{r['CustomerCode']}**")
        cols[2].markdown(f"**{r['FullName']}**")
        cols[3].markdown(r['ContactPhone'] or "-")
        cols[4].markdown(r['Email'] or "-")
        cols[5].markdown(r['City'] or "-")
        cols[6].markdown(r['NID'] or "-")

        with cols[7]:
            a, b, c = st.columns(3)

            if a.button("👁", key=f"v{r['CustomerId']}"):
                view_customer(int(r['CustomerId']))

            if b.button("✏️", key=f"e{r['CustomerId']}"):
                customer_form(int(r['CustomerId']))

            if c.button("🗑️", key=f"d{r['CustomerId']}"):
                success, msg = delete_customer(int(r['CustomerId']))
                if success:
                    st.success(msg)
                    st.rerun()
                else:
                    st.error(msg)


# =========================================================================================
# MULTIPAGE HOOK
# =========================================================================================
def render_page():
    main()


if __name__ == "__main__":
    main()

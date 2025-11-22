# ===========================================================
# IMPORTS & CONFIGURATION
# ===========================================================
import os
from datetime import datetime
import pandas as pd
import streamlit as st
from db_connect import get_connection

# ===========================================================
# STREAMLIT PAGE SETUP
# ===========================================================
#st.set_page_config(page_title="User Profiles", page_icon="👥", layout="wide")

# ===========================================================
# LOAD CUSTOM CSS
# ===========================================================
def load_css(file_name="style.css"):
    project_root = os.getcwd()
    css_path = os.path.join(project_root, "app", "static", file_name)

    if os.path.exists(css_path):
        with open(css_path, "r", encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    else:
        st.markdown("""
        <style>
        .profile-header-row{
            display:grid;
            grid-template-columns:2.2fr 2.8fr 1.6fr 1.6fr 1.2fr 2fr;
            padding:10px;
            font-weight:700;
            background:#f0f2f6;
            border-radius:8px;
        }
        .profile-row{
            display:grid;
            grid-template-columns:2.2fr 2.8fr 1.6fr 1.6fr 1.2fr 2fr;
            padding:12px;
            border-radius:8px;
            background:#f9f9f9;
            margin-bottom:6px;
            align-items:center;
            transition:0.2s;
        }
        .profile-row:hover {background:#eef0f5;}
        </style>
        """, unsafe_allow_html=True)

# ===========================================================
# DATABASE FUNCTIONS
# ===========================================================
def load_user_profiles():
    try:
        conn = get_connection()
        df = pd.read_sql("""
            SELECT 
                profileid    AS "ProfileId",
                userid       AS "UserId",
                address      AS "Address",
                city         AS "City",
                country      AS "Country",
                dateofbirth  AS "DateOfBirth",
                gender       AS "Gender",
                profilepictureurl AS "ProfilePictureUrl",
                createdat    AS "CreatedAt",
                updatedat    AS "UpdatedAt"
            FROM public.userprofiles
            ORDER BY profileid
        """, conn)
        conn.close()
        return df
    except Exception as e:
        st.error(f"Error loading profiles: {e}")
        return pd.DataFrame()

def load_user_dropdown():
    try:
        conn = get_connection()
        df = pd.read_sql("""
            SELECT userid AS "UserId", username AS "Username"
            FROM public.users
            ORDER BY username
        """, conn)
        conn.close()
        return df
    except Exception as e:
        st.error(f"Error loading users: {e}")
        return pd.DataFrame()

def create_user_profile(userid, address, city, country, dob, gender, profile_pic_file):
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM public.userprofiles WHERE userid=%s", (userid,))
        if cur.fetchone()[0] > 0:
            st.error("❌ This user already has a profile!")
            conn.close()
            return False

        picture_url = None
        if profile_pic_file:
            folder = "uploads/profile_pics"
            os.makedirs(folder, exist_ok=True)
            ext = profile_pic_file.name.split(".")[-1].lower()
            picture_url = f"{folder}/user_{userid}.{ext}"
            with open(picture_url, "wb") as f:
                f.write(profile_pic_file.getbuffer())

        now = datetime.now()
        cur.execute("""
            INSERT INTO public.userprofiles
            (userid, address, city, country, dateofbirth, gender, profilepictureurl, createdat, updatedat)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (userid, address, city, country, dob, gender, picture_url, now, now))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        st.error(f"Create error: {e}")
        return False

def update_user_profile(profileid, address, city, country, dob, gender, pic_file, userid):
    # ... (একই আছে, শুধু ছোট উন্নতি)
    try:
        conn = get_connection()
        cur = conn.cursor()
        picture_url = None
        if pic_file:
            folder = "uploads/profile_pics"
            os.makedirs(folder, exist_ok=True)
            ext = pic_file.name.split(".")[-1].lower()
            picture_url = f"{folder}/user_{userid}.{ext}"
            with open(picture_url, "wb") as f:
                f.write(pic_file.getbuffer())

        now = datetime.now()
        if picture_url:
            cur.execute("""
                UPDATE public.userprofiles SET
                    address=%s, city=%s, country=%s, dateofbirth=%s, gender=%s,
                    profilepictureurl=%s, updatedat=%s
                WHERE profileid=%s
            """, (address, city, country, dob, gender, picture_url, now, profileid))
        else:
            cur.execute("""
                UPDATE public.userprofiles SET
                    address=%s, city=%s, country=%s, dateofbirth=%s, gender=%s, updatedat=%s
                WHERE profileid=%s
            """, (address, city, country, dob, gender, now, profileid))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        st.error(f"Update error: {e}")
        return False

def delete_user_profile(profileid):
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("DELETE FROM public.userprofiles WHERE profileid=%s", (profileid,))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        st.error(f"Delete error: {e}")
        return False

# ===========================================================
# SESSION STATE
# ===========================================================
for key, default in {
    "page_mode": None,   # None, "view", "edit", "delete"
    "view_id": None,
    "edit_id": None,
    "delete_id": None,
}.items():
    if key not in st.session_state:
        st.session_state[key] = default

# ===========================================================
# MAIN PAGE
# ===========================================================
def render_page():
    load_css()
    st.title("👥 User Profiles Management")

    profiles_df = load_user_profiles()
    users_df = load_user_dropdown()

    # Merge username
    if not profiles_df.empty and not users_df.empty:
        profiles_df = profiles_df.merge(users_df, on="UserId", how="left")
    if "Username" not in profiles_df.columns:
        profiles_df["Username"] = ""

    # ======================================================
    # SEARCH BAR (একবারই, unique key)
    # ======================================================
    search = st.text_input("🔍 Search by Username, Address, City or Country", "", key="profile_search_input")

    filtered = profiles_df.copy()

    if search and search.strip():
        query = search.strip().lower()
        mask = (
            filtered["Username"].astype(str).str.lower().str.contains(query, na=False) |
            filtered["Address"].astype(str).str.lower().str.contains(query, na=False) |
            filtered["City"].astype(str).str.lower().str.contains(query, na=False) |
            filtered["Country"].astype(str).str.lower().str.contains(query, na=False)
        )
        filtered = filtered[mask]

    # ======================================================
    # CREATE NEW PROFILE
    # ======================================================
    with st.expander("➕ Create New Profile", expanded=False):
        if users_df.empty:
            st.warning("No users found in the system.")
        else:
            user_map = dict(zip(users_df["Username"], users_df["UserId"]))
            selected_username = st.selectbox("Select User", options=sorted(user_map.keys()), key="create_user")
            selected_userid = user_map[selected_username]

            col1, col2 = st.columns(2)
            with col1:
                address = st.text_area("Address", key="create_address")
                city = st.text_input("City", key="create_city")
            with col2:
                country = st.text_input("Country", key="create_country")
                dob = st.date_input("Date of Birth", key="create_dob")
            gender = st.selectbox("Gender", ["Male", "Female", "Other", "Prefer not to say"], key="create_gender")
            pic = st.file_uploader("Profile Picture (jpg, jpeg, png)", type=["jpg", "jpeg", "png"], key="create_pic")

            if st.button("✅ Create Profile", type="primary", key="btn_create"):
                if create_user_profile(selected_userid, address, city, country, dob, gender, pic):
                    st.success("Profile created successfully!")
                    st.rerun()

    if filtered.empty:
        st.info("No profiles found matching your search.")
        return

    # ======================================================
    # TABLE HEADER
    # ======================================================
    st.markdown("""
    <div class='profile-header-row'>
        <div>User Info</div>
        <div>Address</div>
        <div>City</div>
        <div>Country</div>
        <div>Gender</div>
        <div>Actions</div>
    </div>
    """, unsafe_allow_html=True)

    # ======================================================
    # TABLE ROWS
    # ======================================================
    for _, row in filtered.iterrows():
        st.markdown("<div class='profile-row'>", unsafe_allow_html=True)
        c1, c2, c3, c4, c5, c6 = st.columns([2.2, 2.8, 1.6, 1.6, 1.2, 2])
        pid = row["ProfileId"]

        with c1:
            st.write(f"**{row['UserId']}** - {row.get('Username', 'N/A')}")
        with c2: st.write(row["Address"] or "-")
        with c3: st.write(row["City"] or "-")
        with c4: st.write(row["Country"] or "-")
        with c5: st.write(row["Gender"] or "-")

        with c6:
            v, e, d = st.columns(3)
            if v.button("👁", key=f"view_{pid}"):
                st.session_state.view_id = pid
                st.session_state.page_mode = "view"
                st.rerun()
            if e.button("✏️", key=f"edit_{pid}"):
                st.session_state.edit_id = pid
                st.session_state.page_mode = "edit"
                st.rerun()
            if d.button("🗑️", key=f"delete_{pid}"):
                st.session_state.delete_id = pid
                st.session_state.page_mode = "delete"
                st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

    # ======================================================
    # VIEW / EDIT / DELETE MODES
    # ======================================================
    if st.session_state.page_mode == "view" and st.session_state.view_id:
        pid = st.session_state.view_id
        row = profiles_df[profiles_df["ProfileId"] == pid].iloc[0]
        st.markdown("---")
        st.subheader(f"👁 Viewing Profile ID: {pid}")
        st.write(f"**User:** {row['UserId']} - {row.get('Username', 'N/A')}")
        st.write(f"**Address:** {row['Address']}")
        st.write(f"**City:** {row['City']} | **Country:** {row['Country']}")
        st.write(f"**Gender:** {row['Gender']} | **DOB:** {row['DateOfBirth']}")
        if row["ProfilePictureUrl"] and os.path.exists(row["ProfilePictureUrl"]):
            st.image(row["ProfilePictureUrl"], width=200)
        if st.button("✖ Close"):
            st.session_state.page_mode = None
            st.rerun()

    elif st.session_state.page_mode == "edit" and st.session_state.edit_id:
        pid = st.session_state.edit_id
        row = profiles_df[profiles_df["ProfileId"] == pid].iloc[0]
        st.markdown("---")
        st.subheader(f"✏️ Editing Profile ID: {pid}")

        with st.form(key=f"edit_form_{pid}"):
            col1, col2 = st.columns(2)
            with col1:
                address = st.text_area("Address", value=row["Address"] or "", key=f"edit_addr_{pid}")
                city = st.text_input("City", value=row["City"] or "", key=f"edit_city_{pid}")
            with col2:
                country = st.text_input("Country", value=row["Country"] or "", key=f"edit_country_{pid}")
                dob = st.date_input("Date of Birth", value=pd.to_datetime(row["DateOfBirth"]), key=f"edit_dob_{pid}")
            gender = st.selectbox("Gender", ["Male", "Female", "Other", "Prefer not to say"],
                                  index=["Male", "Female", "Other", "Prefer not to say"].index(row["Gender"])
                                  if row["Gender"] in ["Male", "Female", "Other", "Prefer not to say"] else 0,
                                  key=f"edit_gender_{pid}")
            pic = st.file_uploader("Replace Profile Picture", type=["jpg", "jpeg", "png"], key=f"edit_pic_{pid}")

            submitted = st.form_submit_button("💾 Save Changes")
            if submitted:
                if update_user_profile(pid, address, city, country, dob, gender, pic, row["UserId"]):
                    st.success("Profile updated successfully!")
                    st.session_state.page_mode = None
                    st.rerun()

        if st.button("✖ Cancel"):
            st.session_state.page_mode = None
            st.rerun()

    elif st.session_state.page_mode == "delete" and st.session_state.delete_id:
        pid = st.session_state.delete_id
        st.markdown("---")
        st.warning(f"⚠️ Are you sure you want to permanently delete Profile ID: {pid}?")
        col1, col2 = st.columns(2)
        if col1.button("🗑️ Yes, Delete", type="primary"):
            if delete_user_profile(pid):
                st.success("Profile deleted!")
                st.session_state.page_mode = None
                st.rerun()
        if col2.button("✖ Cancel"):
            st.session_state.page_mode = None
            st.rerun()

# ===========================================================
# RUN
# ===========================================================
render_page()
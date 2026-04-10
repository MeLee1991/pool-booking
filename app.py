import os
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

# 1. SETUP
st.set_page_config(page_title="Pool", layout="wide", initial_sidebar_state="collapsed")

# 2. DATA
USERS_FILE = "users.csv"
BOOKINGS_FILE = "bookings.csv"

def load_data(file, columns):
    if os.path.exists(file): return pd.read_csv(file, dtype=str)
    return pd.DataFrame(columns=columns)

def save_data(df, file): df.to_csv(file, index=False)

users = load_data(USERS_FILE, ["Email", "Name", "Password", "Role"])
bookings = load_data(BOOKINGS_FILE, ["User", "Name", "Date", "Table", "Time"])

# 3. SESSION STATE
if "user" not in st.session_state: st.session_state.user = None
if "name" not in st.session_state: st.session_state.name = None
if "role" not in st.session_state: st.session_state.role = None
if "sel_date" not in st.session_state: st.session_state.sel_date = str(datetime.now().date())
if "confirm_delete" not in st.session_state: st.session_state.confirm_delete = None

# 4. CSS (IMPROVED FOR TIGHT MOBILE GRID & SCROLLING)
st.markdown("""
<style>
/* 1. PREVENT MOBILE STACKING (The core fix) */
[data-testid="stHorizontalBlock"] {
    display: flex !important;
    flex-wrap: nowrap !important;
    gap: 0.2rem !important; /* Extremely tight gaps */
    align-items: center !important;
}

/* Remove default heavy padding inside Streamlit columns */
[data-testid="column"] {
    padding-left: 0.1rem !important;
    padding-right: 0.1rem !important;
    min-width: 0 !important;
}

/* 2. BUTTON SIZING & COLORS */
.stButton > button {
    width: 100% !important; height: 32px !important;
    padding: 0px !important; border-radius: 4px !important; font-weight: bold !important;
    font-size: 13px !important;
}
/* Free Slots (Secondary) -> Light Green */
button[kind="secondary"] { background-color: #e6ffed !important; color: #1a7f37 !important; border: 1px solid #4AC26B !important; }
/* Booked Slots (Primary/Disabled) -> Light Red */
button[kind="primary"], .table-row button:disabled { 
    background-color: #ffebe9 !important; color: #cf222e !important; 
    border: 1px solid #FF8182 !important; opacity: 1 !important; 
}

/* 3. TEXT & HEADERS */
.time-label { font-size: 12px; font-weight: bold; text-align: center; }
.header-box { 
    background: #000; color: #fff; text-align: center; font-size: 13px; font-weight: bold;
    height: 32px; line-height: 32px; border-radius: 4px;
}
[data-testid="stAppViewBlockContainer"] { padding: 1rem 0.5rem !important; }
</style>
""", unsafe_allow_html=True)

# 5. LOGIN (Main Logic)
if st.session_state.user is None:
    st.title("🎱 RESERVE")
    e = st.text_input("Email").lower().strip()
    p = st.text_input("Password", type="password")
    if st.button("Login"):
        match = users[(users["Email"] == e) & (users["Password"] == p)]
        if not match.empty:
            st.session_state.user, st.session_state.name, st.session_state.role = e, match.iloc[0]["Name"], match.iloc[0]["Role"]
            st.rerun()
    st.stop()

# ==========================================================
# 6. APPLICATION ROUTING
# ==========================================================

st.sidebar.title("🎱 Pool App")
st.sidebar.markdown(f"**Logged in:** {st.session_state.name} ({st.session_state.role.capitalize()})")

# Define pages and role checks
PAGES = {"Pool Booking": "user"}
if st.session_state.role == "admin":
    PAGES["Administration"] = "admin"

selected_page = st.sidebar.radio("Navigation", list(PAGES.keys()))

if st.sidebar.button("Logout"):
    st.session_state.clear()
    st.rerun()

# ==========================================================
# 7. PAGE LOGIC
# ==========================================================

if selected_page == "Pool Booking":
    st.write("### 📅 Dates")
    today = datetime.now().date()
    # We create columns for dates here, they will adhere to the nowrap CSS
    cols = st.columns(14)
    for i in range(14):
        d = today + timedelta(days=i)
        d_str = str(d)
        with cols[i]:
            is_active = (st.session_state.sel_date == d_str)
            # Use 'Sat' form as in your image
            label = f"{d.strftime('%a')}\n{d.day}"
            if st.button(label, key=f"d_{d_str}", type="primary" if is_active else "secondary"):
                st.session_state.sel_date = d_str; st.rerun()

    # Admin/User Confirmation Dialog
    if st.session_state.confirm_delete:
        idx_to_del, b_name = st.session_state.confirm_delete
        st.warning(f"Confirm Cancellation for {b_name}?")
        c1, c2 = st.columns([1,1])
        if c1.button("Confirm Cancel", type="primary"):
            bookings = bookings.drop(index=int(idx_to_del)); save_data(bookings, BOOKINGS_FILE)
            st.session_state.confirm_delete = None; st.rerun()
        if c2.button("Keep Booking"):
            st.session_state.confirm_delete = None; st.rerun()

    st.divider()

    # BOOKING TABLE
    # --- FIXED HEADERS ---
    # Use ratios [1, 3, 3, 3] to make 'Time' narrowest.
    h_cols = st.columns([1, 3, 3, 3])
    with h_cols[0]: st.write("")
    with h_cols[1]: st.markdown('<div class="header-box">T1</div>', unsafe_allow_html=True)
    with h_cols[2]: st.markdown('<div class="header-box">T2</div>', unsafe_allow_html=True)
    with h_cols[3]: st.markdown('<div class="header-box">T3</div>', unsafe_allow_html=True)

    # --- SCROLLING DATA ---
    schedule_container = st.container(height=400) # Adjust height as needed
    HOURS = [f"{h:02d}:{m}" for h in (list(range(8, 24)) + list(range(0, 3))) for m in ["00", "30"]]

    with schedule_container:
        for idx, t in enumerate(HOURS):
            # Same column ratios as headers
            r_cols = st.columns([1, 3, 3, 3])
            
            with r_cols[0]: st.markdown(f'<div class="time-label">{t}</div>', unsafe_allow_html=True)
                
            for i in range(3):
                t_n = f"Table {i+1}"
                match = bookings[(bookings["Table"] == t_n) & (bookings["Time"] == t) & (bookings["Date"] == st.session_state.sel_date)]
                with r_cols[i+1]:
                    if not match.empty:
                        b_user, b_name = match.iloc[0]["User"], match.iloc[0]["Name"]
                        
                        # Use your original booking logic
                        if st.session_state.user == b_user:
                            if st.button(f"❌ {b_name[:5]}", key=f"b_{t}_{i}", type="primary"):
                                bookings = bookings.drop(match.index); save_data(bookings, BOOKINGS_FILE); st.rerun()
                        elif st.session_state.role == "admin":
                            if st.button(f"🛡️ {b_name[:5]}", key=f"b_{t}_{i}", type="primary"):
                                st.session_state.confirm_delete = (match.index[0], b_name); st.rerun()
                        else:
                            st.button(f"🔒 {b_name[:5]}", key=f"b_{t}_{i}", disabled=True)
                    else:
                        if st.button("Free", key=f"b_{t}_{i}", type="secondary"):
                            new_b = pd.DataFrame([{"User":st.session_state.user, "Name":st.session_state.name, "Date":st.session_state.sel_date, "Table":t_n, "Time":t}])
                            save_data(pd.concat([bookings, new_b]), BOOKINGS_FILE); st.rerun()

elif selected_page == "Administration" and st.session_state.role == "admin":
    st.title("🛡️ Administration")
    
    # 8. MANAGE USERS
    st.subheader("Manage Users")
    st.dataframe(users, use_container_width=True)
    
    with st.expander("➕ Add/Edit User"):
        form_cols = st.columns([3, 2, 2, 1])
        u_mode = st.radio("Mode", ["Add New", "Edit Existing"])
        u_email = st.text_input("User Email", key="u_email").lower().strip()
        u_name = st.text_input("User Name", key="u_name").strip()
        u_pass = st.text_input("User Password", key="u_pass").strip()
        u_role = st.selectbox("User Role", ["user", "admin"], key="u_role")

        if u_mode == "Edit Existing":
            if u_email not in users["Email"].values:
                st.error("User does not exist!")
                # Reset name/pass if you want to clear the form on error
                st.session_state.u_name = ""; st.session_state.u_pass = ""
            else:
                user_data = users[users["Email"] == u_email].iloc[0]
                # Pre-fill (this can be complex in Streamlit, it requires resetting the keys)
                if not st.session_state.get('u_prefilled', False):
                    st.session_state.u_name = user_data["Name"]
                    st.session_state.u_pass = user_data["Password"]
                    st.session_state.u_role = user_data["Role"]
                    st.session_state.u_prefilled = True
                    st.rerun()
        else:
            if st.session_state.get('u_prefilled', False): # Reset if switch from edit to add
                 st.session_state.u_name = ""; st.session_state.u_pass = ""; st.session_state.u_role = "user"; st.session_state.u_prefilled = False; st.rerun()

        edit_col, del_col = st.columns([1,1])
        with edit_col:
            button_label = "Update User" if u_mode == "Edit Existing" else "Add User"
            if st.button(button_label, type="primary"):
                if not u_email or not u_name or not u_pass:
                    st.error("All fields required!")
                else:
                    if u_mode == "Add New":
                        if u_email in users["Email"].values:
                            st.error("Email already registered!")
                        else:
                            new_u = pd.DataFrame([{"Email": u_email, "Name": u_name, "Password": u_pass, "Role": u_role}])
                            save_data(pd.concat([users, new_u]), USERS_FILE)
                            st.success(f"Added user {u_name}")
                            # Reset for next add
                            st.session_state.u_email = ""; st.session_state.u_name = ""; st.session_state.u_pass = ""; st.rerun()
                    else: # Edit
                        users.loc[users["Email"] == u_email, ["Name", "Password", "Role"]] = [u_name, u_pass, u_role]
                        save_data(users, USERS_FILE)
                        st.success(f"Updated user {u_name}")
                        st.session_state.u_prefilled = False; st.rerun()

        with del_col:
            if u_mode == "Edit Existing":
                 if st.button("❌ Delete User", type="primary"):
                     if u_email == st.session_state.user:
                          st.error("You cannot delete yourself!")
                     else:
                          users = users[users["Email"] != u_email]; save_data(users, USERS_FILE)
                          st.success(f"Deleted user {u_name}")
                          st.session_state.u_prefilled = False; st.rerun()

    # 9. STATS
    st.divider()
    st.subheader("📊 Statistics")
    
    st.write(f"Total Bookings to Date: **{len(bookings)}**")
    
    st.markdown("Download full booking history in CSV format:")
    
    # We load it again to get the latest, or convert the existing DataFrame to CSV.
    full_bookings_csv = bookings.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="Download Bookings CSV",
        data=full_bookings_csv,
        file_name='full_bookings_history.csv',
        mime='text/csv',
    )


import streamlit as st
import pandas as pd
import os
from datetime import datetime, timedelta

# ===============================
# CONFIG & FILES
# ===============================
st.set_page_config(page_title="Poolhall", layout="centered", initial_sidebar_state="collapsed")

USERS_FILE = "users.csv"
BOOKINGS_FILE = "bookings.csv"
OWNER_EMAIL = "admin@gmail.com"

# ===============================
# THE REPAIRED CSS (STRICT GRID)
# ===============================
st.markdown("""
<style>
    .block-container { padding: 1rem 5px !important; max-width: 100% !important; }
    
    /* Horizontal Date Selector */
    div[data-testid="stHorizontalBlock"]:has(> div:nth-child(7):last-child) {
        display: flex !important; flex-wrap: nowrap !important;
        overflow-x: auto !important; gap: 6px !important;
    }
    div[data-testid="stHorizontalBlock"]:has(> div:nth-child(7):last-child) > div {
        min-width: 85px !important; flex: 0 0 auto !important;
    }

    /* Force 4 Columns for Main Table */
    div[data-testid="stHorizontalBlock"]:has(> div:nth-child(4):last-child) {
        display: grid !important; grid-template-columns: repeat(4, 1fr) !important;
        gap: 4px !important; margin-bottom: 4px !important;
    }
    div[data-testid="stHorizontalBlock"]:has(> div:nth-child(4):last-child) > div {
        width: 100% !important; min-width: 0 !important;
    }

    .stButton > button {
        height: 44px !important; border-radius: 6px !important;
        width: 100% !important; padding: 0 !important;
    }
    .stButton > button p { font-size: 11px !important; font-weight: bold !important; }

    /* Available Slot Color */
    div[data-testid="stHorizontalBlock"]:has(> div:nth-child(4):last-child) button[kind="secondary"] { 
        background-color: #e8f5e9 !important; color: #2e7d32 !important; border: 1px solid #c8e6c9 !important;
    }
    /* Booked Slot Color */
    div[data-testid="stHorizontalBlock"]:has(> div:nth-child(4):last-child) button[kind="primary"] { 
        background-color: #ffebee !important; color: #c62828 !important; border: 1px solid #ffcdd2 !important;
    }

    .grid-header {
        text-align: center; font-size: 11px; font-weight: bold; height: 44px; 
        line-height: 44px; border-radius: 6px; background-color: #212121; color: white;
    }
    .time-label {
        text-align: center; font-size: 11px; font-weight: bold; height: 44px; 
        line-height: 44px; border-radius: 6px; color: #333; background-color: #f5f5f5;
    }
    
    [data-testid="stHeader"] {display: none;}
</style>
""", unsafe_allow_html=True)

# ===============================
# DATA HELPERS (CRASH PROOF)
# ===============================
USER_COLS = ["email", "password", "role", "approved"]

def load_data(file, cols):
    if not os.path.exists(file):
        df = pd.DataFrame(columns=cols)
        if file == USERS_FILE:
            df = pd.DataFrame([[OWNER_EMAIL, "1234", "admin", True]], columns=cols)
        df.to_csv(file, index=False)
        return df
    
    df = pd.read_csv(file)
    # Automatically fix missing columns (Prevents KeyError)
    changed = False
    for col in cols:
        if col not in df.columns:
            df[col] = True if col == "approved" else ("user" if col == "role" else "")
            changed = True
    if changed: df.to_csv(file, index=False)
    return df[cols]

def save_data(df, file):
    df.to_csv(file, index=False)

def set_date(new_date): st.session_state.sel_date = new_date

def handle_booking(date_str, table, time_str, user_email, role):
    # Admin Mode: Use the target user selected in Admin tab
    target_user = st.session_state.get("admin_target_user", user_email)
    
    df = load_data(BOOKINGS_FILE, ["user", "date", "table", "time"])
    mask = (df["date"] == date_str) & (df["table"] == table) & (df["time"] == time_str)
    
    if df[mask].empty:
        new_row = pd.DataFrame([[target_user, date_str, table, time_str]], columns=df.columns)
        df = pd.concat([df, new_row], ignore_index=True)
    else:
        owner = df[mask].iloc[0]["user"]
        if owner == user_email or role == "admin": 
            df = df[~mask]
    save_data(df, BOOKINGS_FILE)

# ===============================
# LOGIN SYSTEM
# ===============================
if "user" not in st.session_state:
    mode = st.radio("M", ["Login", "Register"], horizontal=True, label_visibility="collapsed")
    if mode == "Login":
        st.markdown("<h3 style='text-align:center;'>🎱 Pool Login</h3>", unsafe_allow_html=True)
        l_user = st.text_input("User").lower()
        l_pw = st.text_input("Password", type="password")
        if st.button("Log In", use_container_width=True):
            # Emergency bypass for admin
            if l_user == OWNER_EMAIL and str(l_pw) == "1234":
                st.session_state.user, st.session_state.role, st.session_state.name = OWNER_EMAIL, "admin", "Admin"
                st.rerun()
            u_df = load_data(USERS_FILE, USER_COLS)
            match = u_df[(u_df["email"] == l_user) & (u_df["password"].astype(str) == str(l_pw))]
            if not match.empty:
                if match.iloc[0]["approved"]:
                    st.session_state.user, st.session_state.role = l_user, match.iloc[0]["role"]
                    st.session_state.name = l_user.split('@')[0].capitalize()
                    st.rerun()
                else: st.warning("Pending Admin Approval.")
            else: st.error("Invalid Login.")
    else:
        st.markdown("<h3 style='text-align:center;'>🎱 Register</h3>", unsafe_allow_html=True)
        r_user = st.text_input("New Username").lower()
        r_pw = st.text_input("New Password", type="password")
        if st.button("Submit Registration"):
            u_df = load_data(USERS_FILE, USER_COLS)
            if r_user in u_df["email"].values: st.error("User exists.")
            else:
                new_u = pd.DataFrame([[r_user, r_pw, "user", False]], columns=USER_COLS)
                save_data(pd.concat([u_df, new_u], ignore_index=True), USERS_FILE)
                st.success("Registered! Wait for approval.")
    st.stop()

# ===============================
# TABS & UI
# ===============================
if "sel_date" not in st.session_state: st.session_state.sel_date = datetime.now().date()

if st.session_state.role == "admin":
    tab_booking, tab_admin = st.tabs(["🎱 Bookings", "⚙️ Admin Dashboard"])
else:
    tab_booking = st.tabs(["🎱 Bookings"])[0]
    tab_admin = None

# Admin Tab logic (Fixes Dropdown and Save feedback)
if tab_admin:
    with tab_admin:
        u_df = load_data(USERS_FILE, USER_COLS)
        st.subheader("👥 User Management")
        edited = st.data_editor(u_df, num_rows="dynamic", use_container_width=True, column_config={
            "role": st.column_config.SelectboxColumn("Role", options=["user", "admin"], required=True),
            "approved": st.column_config.CheckboxColumn("Approved")
        })
        if st.button("💾 Save User Changes"):
            save_data(edited, USERS_FILE)
            st.success("Changes Saved Successfully!")
            st.rerun()

        st.divider()
        st.subheader("🛠️ Admin Booking Mode")
        user_list = u_df["email"].tolist()
        # Safety check for dropdown (Prevents ValueError)
        default_idx = user_list.index(st.session_state.user) if st.session_state.user in user_list else 0
        st.session_state.admin_target_user = st.selectbox("I am booking for:", user_list, index=default_idx)
        st.info(f"Booking Mode Active: Any ➕ you click will book for **{st.session_state.admin_target_user}**")

# Booking Tab logic (The Main Grid)
with tab_booking:
    st.write(f"**👤 {st.session_state.name}** | {st.session_state.sel_date}")
    
    # 14 Day Selector
    today = datetime.now().date()
    dates = [today + timedelta(days=i) for i in range(14)]
    for row_start in [0, 7]:
        d_cols = st.columns(7)
        for i in range(7):
            d = dates[row_start + i]
            lbl = f"TOD {d.day}" if d == today else f"TOM {d.day}" if d == (today + timedelta(1)) else f"{d.strftime('%a').upper()} {d.day}"
            with d_cols[i]:
                st.button(lbl, key=f"d_{d}", type="primary" if d == st.session_state.sel_date else "secondary", 
                          on_click=set_date, args=(d,), use_container_width=True)

    st.divider()

    # Main Grid Header
    h_cols = st.columns(4)
    for i, title in enumerate(["Time", "T1", "T2", "T3"]):
        with h_cols[i]: st.markdown(f"<div class='grid-header'>{title}</div>", unsafe_allow_html=True)

    # Main Grid Data
    times = [f"{h:02d}:{m}" for h in range(6, 24) for m in ("00","30")]
    bookings = load_data(BOOKINGS_FILE, ["user", "date", "table", "time"])
    df_day = bookings[bookings["date"] == str(st.session_state.sel_date)]

    for t in times:
        r_cols = st.columns(4)
        with r_cols[0]: 
            st.markdown(f"<div class='time-label'>{t}</div>", unsafe_allow_html=True)
        
        for i, table in enumerate(["T1", "T2", "T3"]):
            with r_cols[i+1]:
                match = df_day[(df_day["table"] == table) & (df_day["time"] == t)]
                btn_key = f"btn_{st.session_state.sel_date}_{table}_{t}"
                
                if not match.empty:
                    owner = match.iloc[0]["user"]
                    display_name = owner.split('@')[0].capitalize()[:7]
                    st.button(f"X {display_name}", key=btn_key, type="primary", on_click=handle_booking, 
                              args=(str(st.session_state.sel_date), table, t, st.session_state.user, st.session_state.role))
                else:
                    st.button("➕", key=btn_key, type="secondary", on_click=handle_booking, 
                              args=(str(st.session_state.sel_date), table, t, st.session_state.user, st.session_state.role))

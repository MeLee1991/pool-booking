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
# THE REPAIRED CSS (STRICT GRID) - NO CHANGES
# ===============================
st.markdown("""
<style>
    .block-container { padding: 1rem 5px !important; max-width: 100% !important; }
    div[data-testid="stHorizontalBlock"]:has(> div:nth-child(7):last-child) {
        display: flex !important; flex-wrap: nowrap !important;
        overflow-x: auto !important; gap: 6px !important;
    }
    div[data-testid="stHorizontalBlock"]:has(> div:nth-child(7):last-child) > div {
        min-width: 85px !important; flex: 0 0 auto !important;
    }
    div[data-testid="stHorizontalBlock"]:has(> div:nth-child(4):last-child) {
        display: grid !important; grid-template-columns: repeat(4, 1fr) !important;
        gap: 4px !important; margin-bottom: 4px !important;
    }
    div[data-testid="stHorizontalBlock"]:has(> div:nth-child(4):last-child) > div {
        width: 100% !important; min-width: 0 !important;
    }
    .stButton > button {
        height: 44px !important; border-radius: 6px !important;
        display: flex !important; justify-content: center !important; align-items: center !important;
        width: 100% !important;
    }
    .stButton > button p {
        font-size: 11px !important; font-weight: bold !important;
        text-align: center !important; margin: 0 !important;
    }
    div[data-testid="stHorizontalBlock"]:has(> div:nth-child(4):last-child) button[kind="secondary"] { 
        background-color: #e8f5e9 !important; color: #2e7d32 !important; border: 1px solid #c8e6c9 !important;
    }
    div[data-testid="stHorizontalBlock"]:has(> div:nth-child(4):last-child) button[kind="primary"] { 
        background-color: #ffebee !important; color: #c62828 !important; border: 1px solid #ffcdd2 !important;
    }
    .grid-header {
        text-align: center; font-size: 11px; font-weight: bold; 
        height: 44px; line-height: 44px; border-radius: 6px; 
        background-color: #6c757d; color: white;
    }
    .time-label {
        text-align: center; font-size: 11px; font-weight: bold; 
        height: 44px; line-height: 44px; border-radius: 6px; color: #333;
    }
    .time-block-0 { background-color: #fff9c4 !important; } 
    .time-block-1 { background-color: #ffe0b2 !important; } 
    .time-block-2 { background-color: #e3f2fd !important; } 
    .time-block-3 { background-color: #f1f8e9 !important; } 
    .time-block-4 { background-color: #efebe9 !important; } 
    [data-testid="stHeader"] {display: none;}
</style>
""", unsafe_allow_html=True)

# ===============================
# DATA HELPERS - AUTO-REPAIR
# ===============================
def load_data(file, cols):
    if not os.path.exists(file):
        df = pd.DataFrame(columns=cols)
        if file == USERS_FILE:
            df = pd.DataFrame([[OWNER_EMAIL, "1234", "admin", True]], columns=cols)
        df.to_csv(file, index=False)
        return df
    df = pd.read_csv(file)
    # FORCE REPAIR if columns are missing or wrong
    if list(df.columns) != cols:
        new_df = pd.DataFrame(columns=cols)
        if file == USERS_FILE:
            new_df = pd.DataFrame([[OWNER_EMAIL, "1234", "admin", True]], columns=cols)
        new_df.to_csv(file, index=False)
        return new_df
    return df

def save_data(df, file): df.to_csv(file, index=False)
def set_date(new_date): st.session_state.sel_date = new_date

def handle_booking(date_str, table, time_str, user_email, role):
    df = load_data(BOOKINGS_FILE, ["user", "date", "table", "time"])
    mask = (df["date"] == date_str) & (df["table"] == table) & (df["time"] == time_str)
    if df[mask].empty:
        new_row = pd.DataFrame([[user_email, date_str, table, time_str]], columns=df.columns)
        df = pd.concat([df, new_row], ignore_index=True)
    else:
        owner = df[mask].iloc[0]["user"]
        if owner == user_email or role == "admin": df = df[~mask]
    save_data(df, BOOKINGS_FILE)

# ===============================
# LOGIN SYSTEM
# ===============================
if "user" not in st.session_state:
    st.markdown("<h3 style='text-align:center;'>🎱 Pool Login</h3>", unsafe_allow_html=True)
    l_user = st.text_input("User").lower() # Label changed to User
    l_pw = st.text_input("Password", type="password")
    if st.button("Log In", use_container_width=True):
        u_df = load_data(USERS_FILE, ["email", "password", "role", "approved"])
        match = u_df[(u_df["email"] == l_user) & (u_df["password"].astype(str) == str(l_pw))]
        if not match.empty:
            if match.iloc[0]["approved"]:
                st.session_state.user, st.session_state.role = l_user, match.iloc[0]["role"]
                st.session_state.name = l_user.split('@')[0].capitalize()
                st.rerun()
            else: st.error("Wait for admin approval.")
        else: st.error("Invalid credentials.")
    st.stop()

# ===============================
# MAIN UI - UNCHANGED OUTLOOK
# ===============================
if "sel_date" not in st.session_state: st.session_state.sel_date = datetime.now().date()
st.write(f"**👤 {st.session_state.name}** | {st.session_state.sel_date}")

# Setup Tabs - ONLY ADMIN SEES DASHBOARD
if st.session_state.role == "admin":
    tab_booking, tab_admin = st.tabs(["🎱 Bookings", "⚙️ Admin Dashboard"])
else:
    tab_booking = st.tabs(["🎱 Bookings"])[0]
    tab_admin = None

with tab_booking:
    today, tomorrow = datetime.now().date(), datetime.now().date() + timedelta(days=1)
    dates = [today + timedelta(days=i) for i in range(14)]
    for row_start in [0, 7]:
        d_cols = st.columns(7)
        for i in range(7):
            d = dates[row_start + i]
            lbl = f"TOD\n{d.day}" if d == today else f"TOM\n{d.day}" if d == tomorrow else f"{d.strftime('%a').upper()}\n{d.day}"
            with d_cols[i]:
                st.button(lbl, key=f"d_{d}", type="primary" if d == st.session_state.sel_date else "secondary", 
                          on_click=set_date, args=(d,), use_container_width=True)

    st.divider()
    h_cols = st.columns(4)
    for i, title in enumerate(["Time", "T1", "T2", "T3"]):
        with h_cols[i]: st.markdown(f"<div class='grid-header'>{title}</div>", unsafe_allow_html=True)

    times = [f"{h:02d}:{m}" for h in range(6, 24) for m in ("00","30")]
    bookings = load_data(BOOKINGS_FILE, ["user", "date", "table", "time"])
    df_day = bookings[bookings["date"] == str(st.session_state.sel_date)]

    for t in times:
        r_cols = st.columns(4)
        block_idx = (int(t.split(":")[0]) - 6) // 4
        with r_cols[0]: st.markdown(f"<div class='time-label time-block-{block_idx}'>{t}</div>", unsafe_allow_html=True)
        for i, table in enumerate(["T1", "T2", "T3"]):
            with r_cols[i+1]:
                match = df_day[(df_day["table"] == table) & (df_day["time"] == t)]
                btn_key = f"btn_{st.session_state.sel_date}_{table}_{t}"
                if not match.empty:
                    owner_email = match.iloc[0]["user"]
                    display_name = owner_email.split('@')[0].capitalize()[:7]
                    st.button(display_name, key=btn_key, type="primary", on_click=handle_booking, 
                              args=(str(st.session_state.sel_date), table, t, st.session_state.user, st.session_state.role), use_container_width=True)
                else:
                    st.button("➕", key=btn_key, type="secondary", on_click=handle_booking, 
                              args=(str(st.session_state.sel_date), table, t, st.session_state.user, st.session_state.role), use_container_width=True)

# ===============================
# ADMIN DASHBOARD - USER MGMT ONLY
# ===============================
if tab_admin:
    with tab_admin:
        st.subheader("👥 User Management")
        u_df = load_data(USERS_FILE, ["email", "password", "role", "approved"])
        edited = st.data_editor(u_df, num_rows="dynamic", use_container_width=True,
                               column_config={
                                   "role": st.column_config.SelectboxColumn("Role", options=["user", "admin"]),
                                   "approved": st.column_config.CheckboxColumn("Approved")
                               })
        if st.button("💾 Save User Changes", use_container_width=True):
            save_data(edited, USERS_FILE)
            st.success("Saved!")
            st.rerun()

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
# RESTORED ORIGINAL DESIGN CSS
# ===============================
st.markdown("""
<style>
    .block-container { padding: 1rem 5px !important; max-width: 100% !important; }
    
    /* Date Selector Row */
    div[data-testid="stHorizontalBlock"]:has(> div:nth-child(7):last-child) {
        display: flex !important; flex-wrap: nowrap !important;
        overflow-x: auto !important; gap: 6px !important;
    }
    div[data-testid="stHorizontalBlock"]:has(> div:nth-child(7):last-child) > div {
        min-width: 85px !important; flex: 0 0 auto !important;
    }

    /* Grid Layout: 4 Columns */
    div[data-testid="stHorizontalBlock"]:has(> div:nth-child(4):last-child) {
        display: grid !important; grid-template-columns: repeat(4, 1fr) !important;
        gap: 4px !important; margin-bottom: 4px !important;
    }
    div[data-testid="stHorizontalBlock"]:has(> div:nth-child(4):last-child) > div {
        width: 100% !important; min-width: 0 !important;
    }

    /* Buttons */
    .stButton > button {
        height: 44px !important; border-radius: 6px !important;
        display: flex !important; justify-content: center !important; align-items: center !important;
        width: 100% !important;
    }
    .stButton > button p {
        font-size: 11px !important; font-weight: bold !important;
        text-align: center !important; margin: 0 !important;
    }

    /* COLORS: Light Green for Free, Light Red for Booked */
    div[data-testid="stHorizontalBlock"]:has(> div:nth-child(4):last-child) button[kind="secondary"] { 
        background-color: #e8f5e9 !important; color: #2e7d32 !important; border: 1px solid #c8e6c9 !important;
    }
    div[data-testid="stHorizontalBlock"]:has(> div:nth-child(4):last-child) button[kind="primary"] { 
        background-color: #ffebee !important; color: #c62828 !important; border: 1px solid #ffcdd2 !important;
    }

    /* Headers & Labels */
    .grid-header {
        text-align: center; font-size: 11px; font-weight: bold; 
        height: 44px; line-height: 44px; border-radius: 6px; 
        background-color: #6c757d; color: white;
    }
    .time-label {
        text-align: center; font-size: 11px; font-weight: bold; 
        height: 44px; line-height: 44px; border-radius: 6px; color: #333;
        background-color: #f0f2f6;
    }
    [data-testid="stHeader"] {display: none;}
</style>
""", unsafe_allow_html=True)

# ===============================
# DATA ENGINES
# ===============================
USER_COLS = ["email", "password", "role", "approved", "info"]
BOOK_COLS = ["user", "date", "table", "time"]

def load_data(file, cols):
    if not os.path.exists(file) or os.path.getsize(file) == 0:
        df = pd.DataFrame(columns=cols)
        if file == USERS_FILE:
            df = pd.DataFrame([[OWNER_EMAIL, "1234", "admin", "True", ""]], columns=cols)
        df.to_csv(file, index=False)
        return df
    try:
        df = pd.read_csv(file, dtype=str).fillna("")
        for c in cols:
            if c not in df.columns: df[c] = ""
        return df[cols]
    except:
        return pd.DataFrame(columns=cols)

def save_data(df, file):
    df.to_csv(file, index=False)

def set_date(new_date): st.session_state.sel_date = new_date

def handle_booking(date_str, table, time_str):
    user_email = st.session_state.user
    role = st.session_state.role
    target = st.session_state.get("admin_target_user", user_email) if role == "admin" else user_email
    
    df = load_data(BOOKINGS_FILE, BOOK_COLS)
    mask = (df["date"] == str(date_str)) & (df["table"] == str(table)) & (df["time"] == str(time_str))
    
    if df[mask].empty:
        new_row = pd.DataFrame([[target, date_str, table, time_str]], columns=BOOK_COLS)
        df = pd.concat([df, new_row], ignore_index=True)
    else:
        owner = str(df[mask].iloc[0]["user"])
        if owner.lower() == user_email.lower() or role == "admin": 
            df = df[~mask]
    save_data(df, BOOKINGS_FILE)

# ===============================
# LOGIN
# ===============================
if "user" not in st.session_state:
    st.markdown("<h3 style='text-align:center;'>🎱 Pool Login</h3>", unsafe_allow_html=True)
    l_user = st.text_input("User").lower().strip()
    l_pw = st.text_input("Password", type="password").strip()
    if st.button("Log In", use_container_width=True):
        if l_user == OWNER_EMAIL and l_pw == "1234":
            st.session_state.user, st.session_state.role, st.session_state.name = OWNER_EMAIL, "admin", "Admin"
            st.rerun()
        u_df = load_data(USERS_FILE, USER_COLS)
        match = u_df[(u_df["email"] == l_user) & (u_df["password"] == l_pw)]
        if not match.empty:
            st.session_state.user = l_user
            st.session_state.role = match.iloc[0]["role"]
            st.session_state.name = l_user.split('@')[0].capitalize()
            st.rerun()
        else: st.error("Invalid credentials.")
    st.stop()

# ===============================
# MAIN UI
# ===============================
if "sel_date" not in st.session_state: st.session_state.sel_date = datetime.now().date()
st.write(f"**👤 {st.session_state.name}** | {st.session_state.sel_date}")

tab_booking, tab_admin = st.tabs(["🎱 Bookings", "⚙️ Admin"]) if st.session_state.role == "admin" else (st.tabs(["🎱 Bookings"])[0], None)

with tab_booking:
    # Date Switcher
    today = datetime.now().date()
    dates = [today + timedelta(days=i) for i in range(14)]
    for row in [dates[:7], dates[7:]]:
        cols = st.columns(7)
        for i, d in enumerate(row):
            lbl = f"{d.strftime('%a').upper()}\n{d.day}"
            with cols[i]:
                st.button(lbl, key=f"d_{d}", type="primary" if d == st.session_state.sel_date else "secondary", 
                          on_click=set_date, args=(d,), use_container_width=True)

    st.divider()
    # Headers
    h_cols = st.columns(4)
    for i, title in enumerate(["Time", "T1", "T2", "T3"]):
        with h_cols[i]: st.markdown(f"<div class='grid-header'>{title}</div>", unsafe_allow_html=True)

    # Time Slots
    times = [f"{h:02d}:{m}" for h in range(6, 24) for m in ("00","30")]
    bookings = load_data(BOOKINGS_FILE, BOOK_COLS)
    df_day = bookings[bookings["date"] == str(st.session_state.sel_date)]

    for t in times:
        r_cols = st.columns(4)
        with r_cols[0]: st.markdown(f"<div class='time-label'>{t}</div>", unsafe_allow_html=True)
        for i, table in enumerate(["T1", "T2", "T3"]):
            with r_cols[i+1]:
                match = df_day[(df_day["table"] == table) & (df_day["time"] == t)]
                btn_key = f"b_{st.session_state.sel_date}_{table}_{t}"
                if not match.empty:
                    owner = str(match.iloc[0]["user"])
                    disp = (owner.split('@')[0] if '@' in owner else owner).capitalize()[:7]
                    st.button(disp, key=btn_key, type="primary", use_container_width=True,
                              on_click=handle_booking, args=(str(st.session_state.sel_date), table, t))
                else:
                    st.button("➕", key=btn_key, type="secondary", use_container_width=True,
                              on_click=handle_booking, args=(str(st.session_state.sel_date), table, t))

if tab_admin:
    with tab_admin:
        u_df = load_data(USERS_FILE, USER_COLS)
        st.subheader("👥 All Users Table")
        
        # Power Spreadsheet with sorting and Info cell
        u_df["approved"] = u_df["approved"].astype(str).str.lower().isin(["true", "1", "yes"])
        edited_df = st.data_editor(
            u_df, 
            num_rows="dynamic", 
            use_container_width=True, 
            key="admin_table",
            column_config={
                "approved": st.column_config.CheckboxColumn("Approve"),
                "info": st.column_config.TextColumn("Info/Photos")
            }
        )
        
        if st.button("💾 Save All User Data", use_container_width=True):
            save_data(edited_df, USERS_FILE)
            st.success("Updated!")
            st.rerun()

        st.divider()
        user_list = u_df["email"].tolist()
        st.session_state.admin_target_user = st.selectbox("🎯 Admin: Book on behalf of:", user_list)

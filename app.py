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
    
    /* 1. DATE SELECTOR */
    div[data-testid="stHorizontalBlock"]:has(> div:nth-child(7):last-child) {
        display: flex !important; flex-wrap: nowrap !important;
        overflow-x: auto !important; gap: 6px !important;
    }
    div[data-testid="stHorizontalBlock"]:has(> div:nth-child(7):last-child) > div {
        min-width: 85px !important; flex: 0 0 auto !important;
    }

    /* 2. MAIN TABLE - FORCE 4 COLUMNS */
    div[data-testid="stHorizontalBlock"]:has(> div:nth-child(4):last-child) {
        display: grid !important; grid-template-columns: repeat(4, 1fr) !important;
        gap: 4px !important; margin-bottom: 4px !important;
    }
    div[data-testid="stHorizontalBlock"]:has(> div:nth-child(4):last-child) > div {
        width: 100% !important; min-width: 0 !important;
    }

    /* 3. BUTTON STYLING */
    .stButton > button {
        height: 44px !important; border-radius: 6px !important;
        display: flex !important; justify-content: center !important; align-items: center !important;
        width: 100% !important;
    }
    .stButton > button p {
        font-size: 11px !important; font-weight: bold !important;
        text-align: center !important; margin: 0 !important;
    }

    /* Main Table Data Colors */
    div[data-testid="stHorizontalBlock"]:has(> div:nth-child(4):last-child) button[kind="secondary"] { 
        background-color: #e8f5e9 !important; color: #2e7d32 !important; border: 1px solid #c8e6c9 !important;
    }
    div[data-testid="stHorizontalBlock"]:has(> div:nth-child(4):last-child) button[kind="primary"] { 
        background-color: #ffebee !important; color: #c62828 !important; border: 1px solid #ffcdd2 !important;
    }

    /* 4. HEADERS & TIME LABELS */
    .grid-header {
        text-align: center; font-size: 11px; font-weight: bold; 
        height: 44px; line-height: 44px; border-radius: 6px; 
        background-color: #6c757d; color: white;
    }
    .time-label {
        text-align: center; font-size: 11px; font-weight: bold; 
        height: 44px; line-height: 44px; border-radius: 6px; color: #333;
    }
    
    /* LIGHT COLORS FOR TIME BLOCKS */
    .time-block-0 { background-color: #fff9c4 !important; } /* Yellow */
    .time-block-1 { background-color: #ffe0b2 !important; } /* Orange */
    .time-block-2 { background-color: #e3f2fd !important; } /* Blue */
    .time-block-3 { background-color: #f1f8e9 !important; } /* Green */
    .time-block-4 { background-color: #efebe9 !important; } /* Brown */
    
    [data-testid="stHeader"] {display: none;}
</style>
""", unsafe_allow_html=True)

# ===============================
# DATA HELPERS
# ===============================
def load_data(file, cols):
    if not os.path.exists(file): 
        df = pd.DataFrame(columns=cols)
        # Ensure default admin exists if file is new
        if file == USERS_FILE:
            df = pd.DataFrame([[OWNER_EMAIL, "1234", "admin"]], columns=cols)
        df.to_csv(file, index=False)
    return pd.read_csv(file)

def save_data(df, file): 
    df.to_csv(file, index=False)

def set_date(new_date): 
    st.session_state.sel_date = new_date

def handle_booking(date_str, table, time_str, user_email, role):
    df = load_data(BOOKINGS_FILE, ["user", "date", "table", "time"])
    mask = (df["date"] == date_str) & (df["table"] == table) & (df["time"] == time_str)
    if df[mask].empty:
        new_row = pd.DataFrame([[user_email, date_str, table, time_str]], columns=df.columns)
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
    st.markdown("<h3 style='text-align:center;'>🎱 Pool Login</h3>", unsafe_allow_html=True)
    login_email = st.text_input("Email").lower()
    login_pw = st.text_input("Password", type="password")
    
    if st.button("Log In", use_container_width=True):
        users_df = load_data(USERS_FILE, ["email", "password", "role"])
        match = users_df[(users_df["email"] == login_email) & (users_df["password"] == str(login_pw))]
        
        if not match.empty:
            st.session_state.user = login_email
            st.session_state.name = login_email.split('@')[0].capitalize()
            st.session_state.role = match.iloc[0]["role"]
            st.rerun()
        else:
            st.error("Invalid email or password. Please try again.")
    st.stop()

# ===============================
# MAIN UI
# ===============================
if "sel_date" not in st.session_state: 
    st.session_state.sel_date = datetime.now().date()

st.write(f"**👤 {st.session_state.name}** | {st.session_state.sel_date}")

# Tabs for Admin
if st.session_state.role == "admin":
    tab_booking, tab_admin = st.tabs(["🎱 Bookings", "⚙️ Admin Dashboard"])
else:
    tab_booking, tab_admin = st.tabs(["🎱 Bookings"])[0], None

with tab_booking:
    today = datetime.now().date()
    dates = [today + timedelta(days=i) for i in range(14)]
    for row_start in [0, 7]:
        d_cols = st.columns(7)
        for i in range(7):
            d = dates[row_start + i]
            lbl = f"{d.strftime('%a').upper()}\n{d.day}"
            with d_cols[i]:
                st.button(lbl, key=f"d_{d}", type="primary" if d == st.session_state.sel_date else "secondary", 
                          on_click=set_date, args=(d,), use_container_width=True)

    st.divider()

    # Table Header
    h_cols = st.columns(4)
    titles = ["Time", "T1", "T2", "T3"]
    for i, title in enumerate(titles):
        with h_cols[i]:
            st.markdown(f"<div class='grid-header'>{title}</div>", unsafe_allow_html=True)

    # Table Data
    times = [f"{h:02d}:{m}" for h in range(6, 24) for m in ("00","30")]
    tables = ["T1", "T2", "T3"]
    bookings = load_data(BOOKINGS_FILE, ["user", "date", "table", "time"])
    df_day = bookings[bookings["date"] == str(st.session_state.sel_date)]

    for t in times:
        r_cols = st.columns(4)
        hour = int(t.split(":")[0])
        block_idx = (hour - 6) // 4 # Creates blocks 0, 1, 2, 3, 4
        
        with r_cols[0]:
            st.markdown(f"<div class='time-label time-block-{block_idx}'>{t}</div>", unsafe_allow_html=True)
            
        for i, table in enumerate(tables):
            with r_cols[i+1]:
                match = df_day[(df_day["table"] == table) & (df_day["time"] == t)]
                btn_key = f"btn_{st.session_state.sel_date}_{table}_{t}"
                
                if not match.empty:
                    owner = match.iloc[0]["user"]
                    is_me = (owner == st.session_state.user) or (st.session_state.role == "admin")
                    label = f"X {owner.split('@')[0].capitalize()[:5]}" if is_me else "🔒"
                    st.button(label, key=btn_key, type="primary", on_click=handle_booking, 
                              args=(str(st.session_state.sel_date), table, t, st.session_state.user, st.session_state.role), use_container_width=True)
                else:
                    st.button("➕", key=btn_key, type="secondary", on_click=handle_booking, 
                              args=(str(st.session_state.sel_date), table, t, st.session_state.user, st.session_state.role), use_container_width=True)

# ===============================
# ADMIN DASHBOARD
# ===============================
if tab_admin:
    with tab_admin:
        st.subheader("📊 Statistics")
        c1, c2, c3 = st.columns(3)
        total_b = len(bookings)
        unique_u = bookings["user"].nunique() if not bookings.empty else 0
        c1.metric("Total Bookings", total_b)
        c2.metric("Active Users", unique_u)
        c3.metric("Tables", "3")

        st.divider()
        st.subheader("👥 User Management")
        users_df = load_data(USERS_FILE, ["email", "password", "role"])
        
        # Fixed data editor with dropdown config
        edited_users = st.data_editor(
            users_df, 
            num_rows="dynamic", 
            use_container_width=True,
            column_config={
                "role": st.column_config.SelectboxColumn("Role", options=["user", "admin"], required=True)
            }
        )
        
        if st.button("💾 Save User Changes", use_container_width=True):
            save_data(edited_users, USERS_FILE)
            st.success("User list updated and saved!")

        st.divider()
        st.subheader("💾 Data Export")
        with open(BOOKINGS_FILE, "rb") as f:
            st.download_button("📥 Download Booking History (CSV)", f, "bookings_history.csv", "text/csv", use_container_width=True)

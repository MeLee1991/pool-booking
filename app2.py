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
# THE REPAIRED CSS (FORCED 4-COL GRID)
# ===============================
st.markdown("""
<style>
    .block-container { padding: 1rem 5px !important; max-width: 100% !important; }
    
    /* 1. DATE SELECTOR - Horizontal Scroll */
    div[data-testid="stHorizontalBlock"]:has(> div:nth-child(7):last-child) {
        display: flex !important;
        flex-wrap: nowrap !important;
        overflow-x: auto !important;
        gap: 6px !important;
    }
    div[data-testid="stHorizontalBlock"]:has(> div:nth-child(7):last-child) > div {
        min-width: 85px !important;
        flex: 0 0 auto !important;
    }

    /* 2. MAIN TABLE - FORCE 4 COLUMNS ON MOBILE */
    /* This targets the horizontal blocks with exactly 4 children */
    div[data-testid="stHorizontalBlock"]:has(> div:nth-child(4):last-child) {
        display: grid !important;
        grid-template-columns: repeat(4, 1fr) !important;
        gap: 4px !important;
        margin-bottom: 4px !important;
    }
    /* Stop Streamlit from adding margin/width to individual columns in grid mode */
    div[data-testid="stHorizontalBlock"]:has(> div:nth-child(4):last-child) > div {
        width: 100% !important;
        min-width: 0 !important;
    }

    /* 3. BUTTON STYLING */
    .stButton > button {
        height: 44px !important; 
        border-radius: 6px !important;
        display: flex !important;
        justify-content: center !important;
        align-items: center !important;
        width: 100% !important;
    }
    .stButton > button p {
        font-size: 11px !important; 
        font-weight: bold !important;
        text-align: center !important;
        margin: 0 !important;
    }

    /* Main Table Button Colors (Light) */
    div[data-testid="stHorizontalBlock"]:has(> div:nth-child(4):last-child) button[kind="secondary"] { 
        background-color: #e8f5e9 !important; color: #2e7d32 !important; border: 1px solid #c8e6c9 !important;
    }
    div[data-testid="stHorizontalBlock"]:has(> div:nth-child(4):last-child) button[kind="primary"] { 
        background-color: #ffebee !important; color: #c62828 !important; border: 1px solid #ffcdd2 !important;
    }

    /* 4. HEADERS & LABELS */
    .grid-header {
        text-align: center; font-size: 11px; font-weight: bold; 
        height: 44px; line-height: 44px; border-radius: 6px; 
        background-color: #6c757d; color: white; /* LIGHTER HEADER */
    }
    
    .time-label {
        text-align: center; font-size: 11px; font-weight: bold; 
        height: 44px; line-height: 44px; border-radius: 6px; 
        color: #333;
    }
    
    /* 4-Hour Time Blocks */
    .time-block-0 { background-color: #f8f9fa; } 
    .time-block-1 { background-color: #e9ecef; }
    .time-block-2 { background-color: #dee2e6; }
    .time-block-3 { background-color: #ced4da; }
    .time-block-4 { background-color: #adb5bd; }
    
    [data-testid="stHeader"] {display: none;}
</style>
""", unsafe_allow_html=True)

# ===============================
# DATA HELPERS & LOGIC
# ===============================
def load_data(file, cols):
    if not os.path.exists(file): pd.DataFrame(columns=cols).to_csv(file, index=False)
    try: return pd.read_csv(file)
    except: return pd.DataFrame(columns=cols)

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
# LOGIN
# ===============================
if "user" not in st.session_state:
    st.markdown("<h3 style='text-align:center;'>🎱 Pool Login</h3>", unsafe_allow_html=True)
    email = st.text_input("Email").lower()
    pw = st.text_input("Password", type="password")
    if st.button("Log In", use_container_width=True):
        if email == OWNER_EMAIL and pw == "1234":
            st.session_state.user, st.session_state.name, st.session_state.role = email, "Admin", "admin"
            st.rerun()
    st.stop()

# ===============================
# MAIN UI
# ===============================
if "sel_date" not in st.session_state: st.session_state.sel_date = datetime.now().date()

st.write(f"**👤 {st.session_state.name}** | {st.session_state.sel_date}")

tab_booking, tab_admin = st.tabs(["🎱 Bookings", "⚙️ Admin"]) if st.session_state.role == "admin" else (st.tabs(["🎱 Bookings"])[0], None)

with tab_booking:
    # 14-Day Selector
    today = datetime.now().date()
    dates = [today + timedelta(days=i) for i in range(14)]
    for row_start in [0, 7]:
        d_cols = st.columns(7)
        for i in range(7):
            d = dates[row_start + i]
            lbl = f"{d.strftime('%a').upper()}\n{d.day}"
            with d_cols[i]:
                st.button(lbl, key=f"d_{d}", type="primary" if d == st.session_state.sel_date else "secondary", on_click=set_date, args=(d,), use_container_width=True)

    st.divider()

    # Main Table Headers
    h_cols = st.columns(4)
    titles = ["Time", "T1", "T2", "T3"]
    for i, title in enumerate(titles):
        with h_cols[i]:
            st.markdown(f"<div class='grid-header'>{title}</div>", unsafe_allow_html=True)

    # Main Table Data
    times = [f"{h:02d}:{m}" for h in range(6, 24) for m in ("00","30")]
    tables = ["T1", "T2", "T3"]
    bookings = load_data(BOOKINGS_FILE, ["user", "date", "table", "time"])
    df_day = bookings[bookings["date"] == str(st.session_state.sel_date)]

    for t in times:
        r_cols = st.columns(4)
        hour = int(t.split(":")[0])
        block_idx = (hour - 6) // 4
        
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
                    st.button(label, key=btn_key, type="primary", on_click=handle_booking, args=(str(st.session_state.sel_date), table, t, st.session_state.user, st.session_state.role), use_container_width=True)
                else:
                    st.button("➕", key=btn_key, type="secondary", on_click=handle_booking, args=(str(st.session_state.sel_date), table, t, st.session_state.user, st.session_state.role), use_container_width=True)

if tab_admin:
    with tab_admin:
        st.subheader("Manage Users")
        users_df = load_data(USERS_FILE, ["email", "password", "role"])
        edited_users = st.data_editor(users_df, num_rows="dynamic", use_container_width=True)
        if st.button("Save Changes"): save_data(edited_users, USERS_FILE)
        
        st.divider()
        with open(BOOKINGS_FILE, "rb") as f:
            st.download_button("📥 Download History", f, "history.csv", "text/csv", use_container_width=True)

import streamlit as st
import pandas as pd
import os
from datetime import datetime, timedelta

st.set_page_config(page_title="Poolhall", layout="centered", initial_sidebar_state="collapsed")

# ===============================
# CONFIG & FILES
# ===============================
USERS_FILE = "users.csv"
BOOKINGS_FILE = "bookings.csv"
OWNER_EMAIL = "admin@gmail.com"

# ===============================
# THE REPAIRED CSS
# ===============================
st.markdown("""
<style>
    .block-container { padding: 1rem 5px !important; max-width: 100% !important; }
    
    /* =========================================
       1. DATE ROWS - Wider (approx 1.5x of 55px)
       ========================================= */
    div[data-testid="stHorizontalBlock"]:has(> div:nth-child(7):last-child) {
        display: flex !important;
        flex-wrap: nowrap !important;
        overflow-x: auto !important;
        padding-bottom: 8px !important;
        gap: 6px !important;
    }
    div[data-testid="stHorizontalBlock"]:has(> div:nth-child(7):last-child) > div {
        min-width: 82px !important; /* 1.5x wider than before */
        flex: 0 0 auto !important;
    }

    /* =========================================
       2. MAIN TABLE ROWS - Fixed Grid
       ========================================= */
    div[data-testid="stHorizontalBlock"]:has(> div:nth-child(4):last-child) {
        display: grid !important;
        grid-template-columns: repeat(4, 1fr) !important;
        gap: 4px !important;
        margin-bottom: 4px !important;
        width: 100% !important;
    }
    div[data-testid="stHorizontalBlock"]:has(> div:nth-child(4):last-child) > div {
        min-width: 0 !important; 
        width: 100% !important; 
    }

    /* =========================================
       3. BUTTON STYLING - Smaller Font (9px)
       ========================================= */
    .stButton > button {
        width: 100% !important;
        height: 44px !important; /* Fixed size matching headers */
        border-radius: 6px !important;
        padding: 0 2px !important;
        border: 1px solid rgba(0,0,0,0.1) !important;
    }
    .stButton > button p {
        font-size: 9px !important; /* 2px smaller than before */
        font-weight: 800 !important;
        margin: 0 !important;
        white-space: pre-wrap !important;
        overflow: hidden;
        text-overflow: ellipsis;
    }

    /* =========================================
       4. COLORS & HEADERS
       ========================================= */
    /* Free Buttons (Green) */
    div[data-testid="stHorizontalBlock"]:has(> div:nth-child(4):last-child) button[kind="secondary"] {
        background-color: #28a745 !important; color: white !important; border: none !important;
    }
    /* Booked Buttons (Red) */
    div[data-testid="stHorizontalBlock"]:has(> div:nth-child(4):last-child) button[kind="primary"] {
        background-color: #dc3545 !important; color: white !important; border: none !important;
    }
    
    /* Date Selected - Blue */
    div[data-testid="stHorizontalBlock"]:has(> div:nth-child(7):last-child) button[kind="primary"] {
        background-color: #007bff !important; color: white !important;
    }

    /* Table Headers */
    .grid-header {
        background-color: #111; color: #fff; text-align: center;
        font-size: 11px; font-weight: bold; height: 44px; line-height: 44px;
        border-radius: 6px; margin-bottom: 0 !important;
    }

    /* Time Column */
    .time-label {
        height: 44px; display: flex; align-items: center; justify-content: center;
        font-size: 10px; font-weight: bold; border-radius: 6px; color: #222;
        background-color: #f1f3f4;
    }

    [data-testid="stHeader"] {display: none;}
</style>
""", unsafe_allow_html=True)

# ===============================
# DATA HELPERS & CALLBACKS
# ===============================
def load_data(file, cols):
    if not os.path.exists(file): pd.DataFrame(columns=cols).to_csv(file, index=False)
    try: return pd.read_csv(file)
    except: return pd.DataFrame(columns=cols)

def save_data(df, file): df.to_csv(file, index=False)

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
    st.markdown("<h2 style='text-align:center;'>🎱 Pool Login</h2>", unsafe_allow_html=True)
    email = st.text_input("Email").lower()
    pw = st.text_input("Password", type="password")
    if st.button("Continue", use_container_width=True):
        if email and pw == "1234":
            st.session_state.user = email
            st.session_state.name = email.split('@')[0].capitalize()
            st.session_state.role = "admin" if email == OWNER_EMAIL else "user"
            st.rerun()
    st.stop()

# ===============================
# UI START
# ===============================
if "sel_date" not in st.session_state: 
    st.session_state.sel_date = datetime.now().date()

st.markdown(f"**👤 {st.session_state.name}** &nbsp;|&nbsp; {st.session_state.sel_date}")

# ===============================
# 14-DAY SELECTOR (Slidable)
# ===============================
today = datetime.now().date()
dates = [today + timedelta(days=i) for i in range(14)]

# Rows of Dates (using 7 cols for the selector layout)
for row_start in [0, 7]:
    d_cols = st.columns(7)
    for i in range(7):
        d = dates[row_start + i]
        lbl = f"TOD\n{d.day}" if d == today else f"TOM\n{d.day}" if d == today + timedelta(days=1) else f"{d.strftime('%a').upper()}\n{d.day}"
        with d_cols[i]:
            st.button(lbl, key=f"date_{d}", type="primary" if d == st.session_state.sel_date else "secondary", on_click=set_date, args=(d,))

st.divider()

# ===============================
# MAIN TABLE
# ===============================
times = [f"{h:02d}:{m}" for h in range(6, 24) for m in ("00","30")]
tables = ["T1", "T2", "T3"]
bookings = load_data(BOOKINGS_FILE, ["user", "date", "table", "time"])
date_str = str(st.session_state.sel_date)
df_day = bookings[bookings["date"] == date_str]

# TABLE HEADER
h_cols = st.columns(4)
for title in ["Time", "T1", "T2", "T3"]:
    with h_cols[["Time", "T1", "T2", "T3"].index(title)]:
        st.markdown(f"<div class='grid-header'>{title}</div>", unsafe_allow_html=True)

# TABLE DATA
for t in times:
    r_cols = st.columns(4)
    with r_cols[0]:
        st.markdown(f"<div class='time-label'>{t}</div>", unsafe_allow_html=True)
        
    for i, table in enumerate(tables):
        with r_cols[i+1]:
            match = df_day[(df_day["table"] == table) & (df_day["time"] == t)]
            btn_key = f"btn_{date_str}_{table}_{t}" 
            
            if not match.empty:
                owner = match.iloc[0]["user"]
                is_me_or_admin = (owner == st.session_state.user) or (st.session_state.role == "admin")
                display_name = owner.split("@")[0].capitalize()[:6] if is_me_or_admin else ""
                label = f"X {display_name}" if is_me_or_admin else "🔒"
                st.button(label, key=btn_key, type="primary", on_click=handle_booking, args=(date_str, table, t, st.session_state.user, st.session_state.role))
            else:
                st.button("➕", key=btn_key, type="secondary", on_click=handle_booking, args=(date_str, table, t, st.session_state.user, st.session_state.role))

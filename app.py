import streamlit as st
import pandas as pd
import os
from datetime import datetime, timedelta

st.set_page_config(page_title="Poolhall", layout="centered", initial_sidebar_state="collapsed")

# ===============================
# CONFIG & FILES
# ===============================
BOOKINGS_FILE = "bookings.csv"
OWNER_EMAIL = "admin@gmail.com"

# ===============================
# THE UNBREAKABLE CSS
# ===============================
st.markdown("""
<style>
    .block-container { padding: 1rem 5px !important; max-width: 100% !important; }
    
    /* 1. DATE SELECTOR - 1.5x Wider (82px) */
    div[data-testid="stHorizontalBlock"]:has(button[key^="date_"]) {
        display: flex !important;
        flex-direction: row !important;
        flex-wrap: nowrap !important;
        overflow-x: auto !important;
        gap: 6px !important;
    }
    div[data-testid="stHorizontalBlock"]:has(button[key^="date_"]) > div {
        min-width: 82px !important; 
        flex: 0 0 auto !important;
    }

    /* 2. MAIN TABLE - Locked 4-Column Grid */
    .table-wrapper div[data-testid="stHorizontalBlock"] {
        display: flex !important;
        flex-direction: row !important; 
        flex-wrap: nowrap !important;
        gap: 4px !important;
        margin-bottom: 4px !important;
        width: 100% !important;
    }
    
    .table-wrapper div[data-testid="column"] {
        width: 25% !important;
        flex: 1 1 25% !important;
        min-width: 0 !important;
    }

    /* 3. BUTTONS & FONT - 9px (2px smaller) */
    .stButton > button {
        width: 100% !important;
        height: 44px !important; 
        border-radius: 4px !important;
        border: none !important;
        padding: 0 !important;
        margin: 0 !important;
    }
    .stButton > button p {
        font-size: 9px !important; 
        font-weight: 800 !important;
        text-transform: uppercase;
    }

    /* Headers & Labels */
    .grid-header {
        background-color: #111; color: #fff; text-align: center;
        font-size: 11px; font-weight: bold; height: 44px; line-height: 44px;
        border-radius: 4px; width: 100%;
    }
    .time-label {
        height: 44px; display: flex; align-items: center; justify-content: center;
        font-size: 10px; font-weight: bold; border-radius: 4px; 
        background-color: #f1f3f4; color: #222; width: 100%;
    }

    /* Colors */
    .table-wrapper button[kind="secondary"] { background-color: #28a745 !important; color: white !important; }
    .table-wrapper button[kind="primary"] { background-color: #dc3545 !important; color: white !important; }
    button[key^="date_"][kind="primary"] { background-color: #007bff !important; color: white !important; }

    [data-testid="stHeader"] {display: none;}
</style>
""", unsafe_allow_html=True)

# ===============================
# DATA HELPERS
# ===============================
def load_data():
    if not os.path.exists(BOOKINGS_FILE):
        return pd.DataFrame(columns=["user", "date", "table", "time"])
    return pd.read_csv(BOOKINGS_FILE)

def set_date(new_date):
    st.session_state.sel_date = new_date

def handle_booking(date_str, table, time_str):
    df = load_data()
    mask = (df["date"] == date_str) & (df["table"] == table) & (df["time"] == time_str)
    if df[mask].empty:
        new_row = pd.DataFrame([[st.session_state.user, date_str, table, time_str]], columns=df.columns)
        df = pd.concat([df, new_row], ignore_index=True)
    else:
        owner = df[mask].iloc[0]["user"]
        if owner == st.session_state.user or st.session_state.role == "admin":
            df = df[~mask]
    df.to_csv(BOOKINGS_FILE, index=False)

# ===============================
# LOGIN & STATE
# ===============================
if "user" not in st.session_state:
    st.markdown("<h2 style='text-align:center;'>🎱 Pool Login</h2>", unsafe_allow_html=True)
    email = st.text_input("Email").lower()
    if st.button("Continue", use_container_width=True):
        st.session_state.user = email
        st.session_state.role = "admin" if email == OWNER_EMAIL else "user"
        st.rerun()
    st.stop()

if "sel_date" not in st.session_state: 
    st.session_state.sel_date = datetime.now().date()

# ===============================
# UI RENDER
# ===============================
st.write(f"👤 **{st.session_state.user.split('@')[0].capitalize()}** | {st.session_state.sel_date}")

# 14-Day Date Bar
today = datetime.now().date()
dates = [today + timedelta(days=i) for i in range(14)]
for row_start in [0, 7]:
    d_cols = st.columns(7)
    for i in range(7):
        d = dates[row_start + i]
        lbl = f"{d.strftime('%a').upper()}\n{d.day}"
        d_cols[i].button(lbl, key=f"date_{d}", type="primary" if d == st.session_state.sel_date else "secondary", on_click=set_date, args=(d,))

st.divider()

# Main Table
st.markdown('<div class="table-wrapper">', unsafe_allow_html=True)

# Headers Row
h_cols = st.columns(4)
for i, title in enumerate(["Time", "T1", "T2", "T3"]):
    h_cols[i].markdown(f"<div class='grid-header'>{title}</div>", unsafe_allow_html=True)

# Time Rows
times = [f"{h:02d}:{m}" for h in range(6, 24) for m in ("00", "30")]
bookings = load_data()
date_str = str(st.session_state.sel_date)

for t in times:
    r_cols = st.columns(4)
    r_cols[0].markdown(f"<div class='time-label'>{t}</div>", unsafe_allow_html=True)
    for i, table in enumerate(["T1", "T2", "T3"]):
        # CORRECTED MATCH LINE BELOW
        match = bookings[(bookings["date"] == date_str) & (bookings["table"] == table) & (bookings["time"] == t)]
        btn_key = f"slot_{date_str}_{table}_{t}"
        
        if not match.empty:
            owner = match.iloc[0]["user"].split("@")[0].capitalize()[:6]
            is_mine = (match.iloc[0]["user"] == st.session_state.user) or (st.session_state.role == "admin")
            r_cols[i+1].button(f"X {owner}" if is_mine else "🔒", key=btn_key, type="primary", on_click=handle_booking, args=(date_str, table, t))
        else:
            r_cols[i+1].button("➕", key=btn_key, type="secondary", on_click=handle_booking, args=(date_str, table, t))

st.markdown('</div>', unsafe_allow_html=True)

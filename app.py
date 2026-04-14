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
# THE REPAIRED CSS
# ===============================
st.markdown("""
<style>
    .block-container { padding: 1rem 5px !important; max-width: 100% !important; }
    
    /* 1. DATE SELECTOR - Slidable & Independent */
    div[data-testid="stHorizontalBlock"]:has(button[key^="date_"]) {
        display: flex !important;
        flex-wrap: nowrap !important;
        overflow-x: auto !important;
        padding-bottom: 10px !important;
        gap: 8px !important;
    }
    div[data-testid="stHorizontalBlock"]:has(button[key^="date_"]) > div {
        min-width: 60px !important;
        flex: 0 0 auto !important;
    }

    /* 2. MAIN TABLE - Locked 4-Column Grid */
    /* Target only columns inside the 'table-wrapper' div */
    .table-wrapper [data-testid="column"] {
        flex: 1 1 0% !important;
        min-width: 0 !important;
        padding: 0 2px !important;
    }

    /* 3. BUTTONS - Wide, Fixed Height, and "Tom" Style */
    .stButton > button {
        width: 100% !important;
        height: 48px !important; /* Fixed chunky height */
        border-radius: 6px !important;
        border: none !important;
    }
    .stButton > button p {
        font-size: 13px !important;
        font-weight: 800 !important;
    }

    /* 4. COLORS (Main Table Only) */
    /* Free = Solid Green */
    .table-wrapper button[kind="secondary"] {
        background-color: #28a745 !important; color: white !important;
    }
    /* Booked = Solid Red */
    .table-wrapper button[kind="primary"] {
        background-color: #dc3545 !important; color: white !important;
    }
    
    /* Date Highlight - Blue */
    div[data-testid="stHorizontalBlock"]:has(button[key^="date_"]) button[kind="primary"] {
        background-color: #007bff !important; color: white !important;
    }

    /* Labels & Headers */
    .grid-header {
        background-color: #111; color: #fff; text-align: center;
        font-weight: bold; height: 48px; line-height: 48px;
        border-radius: 6px; margin-bottom: 8px;
    }
    .time-label {
        height: 48px; display: flex; align-items: center; justify-content: center;
        font-size: 14px; font-weight: bold; border-radius: 6px; 
        background-color: #f1f3f4; color: #333;
    }

    [data-testid="stHeader"] {display: none;}
</style>
""", unsafe_allow_html=True)

# ===============================
# LOGIC & CALLBACKS (Fixes URL forwarding & reacting)
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
# LOGIN SYSTEM
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
# DATE SELECTOR (Slidable Row)
# ===============================
st.write(f"👤 **{st.session_state.user.split('@')[0].capitalize()}** | {st.session_state.sel_date}")

today = datetime.now().date()
dates = [today + timedelta(days=i) for i in range(14)]
d_cols = st.columns(len(dates))
for i, d in enumerate(dates):
    lbl = f"{d.strftime('%a').upper()}\n{d.day}"
    is_sel = (d == st.session_state.sel_date)
    # Using key="date_..." to keep it separate from table buttons
    d_cols[i].button(lbl, key=f"date_{d}", type="primary" if is_sel else "secondary", on_click=set_date, args=(d,))

st.divider()

# ===============================
# MAIN TABLE (Wrapped in 'table-wrapper')
# ===============================
st.markdown('<div class="table-wrapper">', unsafe_allow_html=True)

# Headers
h_cols = st.columns(4)
for i, title in enumerate(["Time", "T1", "T2", "T3"]):
    h_cols[i].markdown(f"<div class='grid-header'>{title}</div>", unsafe_allow_html=True)

# Rows
times = [f"{h:02d}:{m}" for h in range(6, 24) for m in ("00", "30")]
bookings = load_data()
date_str = str(st.session_state.sel_date)

for t in times:
    r_cols = st.columns(4)
    with r_cols[0]:
        st.markdown(f"<div class='time-label'>{t}</div>", unsafe_allow_html=True)
        
    for i, table in enumerate(["T1", "T2", "T3"]):
        match = bookings[(bookings["date"] == date_str) & (bookings["table"] == table) & (bookings["time"] == t)]
        btn_key = f"slot_{date_str}_{table}_{t}" # Unique key to prevent bugs
        
        if not match.empty:
            owner = match.iloc[0]["user"].split("@")[0].capitalize()
            is_mine = (match.iloc[0]["user"] == st.session_state.user) or (st.session_state.role == "admin")
            label = f"X {owner}" if is_mine else "🔒"
            # Booked = Red (Primary)
            r_cols[i+1].button(label, key=btn_key, type="primary", on_click=handle_booking, args=(date_str, table, t))
        else:
            # Free = Green (Secondary)
            r_cols[i+1].button("+", key=btn_key, type="secondary", on_click=handle_booking, args=(date_str, table, t))

st.markdown('</div>', unsafe_allow_html=True)

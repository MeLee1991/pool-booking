import streamlit as st
import pandas as pd
import os
from datetime import datetime, timedelta

st.set_page_config(page_title="Poolhall", layout="centered", initial_sidebar_state="collapsed")

# ===============================
# CSS: THE "TOM" DESIGN REPLICA
# ===============================
st.markdown("""
<style>
    .block-container { padding: 1rem 10px !important; }
    
    /* 1. DATE SELECTOR - Simple & Clean */
    div[data-testid="column"] button p { font-size: 12px !important; font-weight: bold !important; }

    /* 2. THE MAIN TABLE GRID - Equal Column Widths */
    div.main-table div[data-testid="stHorizontalBlock"] {
        gap: 4px !important;
    }
    div.main-table div[data-testid="column"] {
        flex: 1 1 0% !important;
        min-width: 0 !important;
    }

    /* 3. BUTTONS: FIXED WIDTH & BLOCKY */
    .stButton > button {
        width: 100% !important;
        height: 45px !important;
        border-radius: 6px !important;
        border: none !important;
        transition: none !important;
    }

    /* Green for Free (+) */
    div.main-table button[kind="secondary"] {
        background-color: #28a745 !important;
        color: white !important;
    }

    /* Red for Booked (X Name) */
    div.main-table button[kind="primary"] {
        background-color: #ff4b4b !important;
        color: white !important;
    }

    /* 4. HEADERS & LABELS */
    .grid-header {
        background-color: #111;
        color: #fff;
        text-align: center;
        font-weight: bold;
        height: 45px;
        line-height: 45px;
        border-radius: 6px;
        font-size: 14px;
        margin-bottom: 5px;
    }

    .time-label {
        background-color: #f1f3f4;
        height: 45px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: bold;
        border-radius: 6px;
        color: #333;
    }

    [data-testid="stHeader"] {display: none;}
</style>
""", unsafe_allow_html=True)

# ===============================
# DATA HELPERS
# ===============================
BOOKINGS_FILE = "bookings.csv"

def load_bookings():
    if not os.path.exists(BOOKINGS_FILE):
        return pd.DataFrame(columns=["user", "date", "table", "time"])
    return pd.read_csv(BOOKINGS_FILE)

def toggle_slot(date_str, table, time_str):
    df = load_bookings()
    mask = (df["date"] == date_str) & (df["table"] == table) & (df["time"] == time_str)
    
    if df[mask].empty:
        new_row = pd.DataFrame([[st.session_state.user, date_str, table, time_str]], columns=df.columns)
        df = pd.concat([df, new_row], ignore_index=True)
    else:
        # Only allow user or admin to cancel
        if df[mask].iloc[0]["user"] == st.session_state.user or st.session_state.user == "admin@gmail.com":
            df = df[~mask]
    df.to_csv(BOOKINGS_FILE, index=False)

# ===============================
# SESSION & LOGIN
# ===============================
if "user" not in st.session_state:
    st.title("🎱 Pool Login")
    email = st.text_input("Email").lower()
    if st.button("Enter"):
        st.session_state.user = email
        st.rerun()
    st.stop()

if "sel_date" not in st.session_state:
    st.session_state.sel_date = datetime.now().date()

# ===============================
# TOP: DATE SELECTOR (Working Logic)
# ===============================
st.write(f"👤 **{st.session_state.user.split('@')[0].capitalize()}** | {st.session_state.sel_date}")

today = datetime.now().date()
# Create two rows of dates
for start_day in [0, 7]:
    d_cols = st.columns(7)
    for i in range(7):
        d = today + timedelta(days=start_day + i)
        label = f"{d.strftime('%a').upper()}\n{d.day}"
        # Selected date is highlighted Blue (Primary)
        is_selected = d == st.session_state.sel_date
        if d_cols[i].button(label, key=f"date_{d}", type="primary" if is_selected else "secondary"):
            st.session_state.sel_date = d
            st.rerun()

st.divider()

# ===============================
# MAIN TABLE: FIXED GRID
# ===============================
st.markdown('<div class="main-table">', unsafe_allow_html=True)

# Header Row
h_cols = st.columns(4)
for i, head in enumerate(["Time", "T 1", "T 2", "T 3"]):
    h_cols[i].markdown(f"<div class='grid-header'>{head}</div>", unsafe_allow_html=True)

# Booking Rows
times = [f"{h:02d}:{m}" for h in range(6, 24) for m in ("00", "30")]
df = load_bookings()
cur_date = str(st.session_state.sel_date)

for t in times:
    r_cols = st.columns(4)
    
    # Time Column
    r_cols[0].markdown(f"<div class='time-label'>{t}</div>", unsafe_allow_html=True)
    
    # Table Columns (T1, T2, T3)
    for i, table_id in enumerate(["T1", "T2", "T3"]):
        slot = df[(df["date"] == cur_date) & (df["table"] == table_id) & (df["time"] == t)]
        
        btn_key = f"btn_{cur_date}_{table_id}_{t}"
        
        if not slot.empty:
            name = slot.iloc[0]["user"].split("@")[0].capitalize()
            # Booked Slot: type="primary" renders RED
            if r_cols[i+1].button(f"X {name}", key=btn_key, type="primary"):
                toggle_slot(cur_date, table_id, t)
                st.rerun()
        else:
            # Free Slot: type="secondary" renders GREEN
            if r_cols[i+1].button("+", key=btn_key, type="secondary"):
                toggle_slot(cur_date, table_id, t)
                st.rerun()

st.markdown('</div>', unsafe_allow_html=True)

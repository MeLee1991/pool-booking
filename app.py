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
# THE "ROCK SOLID" CSS
# ===============================
st.markdown("""
<style>
    .block-container { padding: 1rem 5px !important; }
    
    /* 1. DATE BUTTONS - Standard Streamlit behavior for reliability */
    div[data-testid="column"] button p { font-size: 12px !important; font-weight: bold !important; }

    /* 2. MAIN TABLE - FORCING EQUAL COLUMN WIDTHS */
    /* We target the container of the table rows specifically */
    div.table-container div[data-testid="stHorizontalBlock"] {
        display: flex !important;
        flex-direction: row !important;
        width: 100% !important;
        gap: 5px !important;
    }
    
    div.table-container div[data-testid="column"] {
        flex: 1 1 0% !important; /* This forces all 4 columns to be EXACTLY equal width */
        min-width: 0 !important;
    }

    /* 3. BUTTON COLORS & SHAPE */
    .stButton > button {
        width: 100% !important;
        height: 42px !important;
        border-radius: 4px !important;
        border: none !important;
    }

    /* Green for Free (+) */
    div.table-container button[kind="secondary"] {
        background-color: #28a745 !important;
        color: white !important;
    }

    /* Red for Booked (X Name) */
    div.table-container button[kind="primary"] {
        background-color: #dc3545 !important;
        color: white !important;
    }

    /* 4. HEADERS & LABELS */
    .grid-header {
        background-color: #000;
        color: #fff;
        text-align: center;
        font-weight: bold;
        height: 40px;
        line-height: 40px;
        border-radius: 4px;
        font-size: 14px;
    }

    .time-box {
        background-color: #f8f9fa;
        height: 42px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: bold;
        border-radius: 4px;
        border: 1px solid #dee2e6;
    }

    [data-testid="stHeader"] {display: none;}
</style>
""", unsafe_allow_html=True)

# ===============================
# DATA & LOGIC
# ===============================
def load_data():
    if not os.path.exists(BOOKINGS_FILE):
        return pd.DataFrame(columns=["user", "date", "table", "time"])
    return pd.read_csv(BOOKINGS_FILE)

def toggle_booking(date_str, table, time_str):
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
# LOGIN
# ===============================
if "user" not in st.session_state:
    st.title("🎱 Pool Login")
    email = st.text_input("Email").lower()
    if st.button("Login (Password: 1234)"):
        st.session_state.user = email
        st.session_state.role = "admin" if email == OWNER_EMAIL else "user"
        st.rerun()
    st.stop()

# ===============================
# DATE SELECTOR
# ===============================
if "sel_date" not in st.session_state:
    st.session_state.sel_date = datetime.now().date()

st.write(f"Logged in as: **{st.session_state.user}**")

# 2 Rows of Dates
today = datetime.now().date()
for row_start in [0, 7]:
    cols = st.columns(7)
    for i in range(7):
        d = today + timedelta(days=row_start + i)
        lbl = d.strftime("%a %d")
        if cols[i].button(lbl, key=f"d_{d}", type="primary" if d == st.session_state.sel_date else "secondary"):
            st.session_state.sel_date = d
            st.rerun()

st.divider()

# ===============================
# THE TABLE
# ===============================
# We wrap the table in a div class 'table-container' so the CSS only hits these columns
st.markdown('<div class="table-container">', unsafe_allow_html=True)

# Headers
h_cols = st.columns(4)
titles = ["Time", "T1", "T2", "T3"]
for i, title in enumerate(titles):
    h_cols[i].markdown(f"<div class='grid-header'>{title}</div>", unsafe_allow_html=True)

# Rows
times = [f"{h:02d}:{m}" for h in range(6, 24) for m in ("00", "30")]
bookings = load_data()
current_date = str(st.session_state.sel_date)

for t in times:
    r_cols = st.columns(4)
    # Time Column
    r_cols[0].markdown(f"<div class='time-box'>{t}</div>", unsafe_allow_html=True)
    
    # Table Columns
    for i, tab_name in enumerate(["T1", "T2", "T3"]):
        slot = bookings[(bookings["date"] == current_date) & (bookings["table"] == tab_name) & (bookings["time"] == t)]
        
        if not slot.empty:
            booked_by = slot.iloc[0]["user"].split("@")[0]
            can_cancel = (slot.iloc[0]["user"] == st.session_state.user) or (st.session_state.role == "admin")
            btn_label = f"X {booked_by}" if can_cancel else "🔒"
            # Booked = Red (Primary)
            if r_cols[i+1].button(btn_label, key=f"{t}_{tab_name}", type="primary"):
                if can_cancel:
                    toggle_booking(current_date, tab_name, t)
                    st.rerun()
        else:
            # Free = Green (Secondary)
            if r_cols[i+1].button("+", key=f"{t}_{tab_name}", type="secondary"):
                toggle_booking(current_date, tab_name, t)
                st.rerun()

st.markdown('</div>', unsafe_allow_html=True)

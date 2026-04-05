import os
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

# 1. SETUP
st.set_page_config(page_title="Pool Booking", layout="wide", initial_sidebar_state="collapsed")

# 2. DATA
USERS_FILE = "users.csv"
BOOKINGS_FILE = "bookings.csv"

def load_data(file, columns):
    if os.path.exists(file): return pd.read_csv(file, dtype=str)
    return pd.DataFrame(columns=columns)

def save_data(df, file): df.to_csv(file, index=False)

users = load_data(USERS_FILE, ["Email", "Name", "Password", "Role"])
bookings = load_data(BOOKINGS_FILE, ["User", "Name", "Date", "Table", "Time"])

# 3. SESSION STATE
if "user" not in st.session_state: st.session_state.user = None
if "role" not in st.session_state: st.session_state.role = None
if "sel_date" not in st.session_state: st.session_state.sel_date = str(datetime.now().date())
if "pending_cancel" not in st.session_state: st.session_state.pending_cancel = None

# 4. THE "ULTRA-NARROW" CSS FIX
st.markdown("""
<style>
/* 1. THE GRID SYSTEM: Kill Streamlit's default stacking and padding */
[data-testid="stHorizontalBlock"] {
    display: flex !important;
    flex-direction: row !important;
    flex-wrap: nowrap !important;
    justify-content: flex-start !important;
    gap: 1px !important; /* Minimal gap between columns */
}

/* 2. FIXED COLUMN WIDTHS */
/* Time column */
.data-row [data-testid="column"]:nth-child(1) {
    flex: 0 0 45px !important;
    min-width: 45px !important;
}
/* Table columns */
.data-row [data-testid="column"]:not(:nth-child(1)) {
    flex: 0 0 75px !important; /* Narrow columns for tables */
    min-width: 75px !important;
}

/* 3. BUTTONS: 1.9x Height Increase & Smaller Font */
.stButton > button {
    width: 100% !important;
    height: 80px !important; /* 1.9x increase from standard 42px */
    padding: 2px !important;
    font-size: 9px !important; /* Smaller text to fit narrow column */
    border-radius: 2px !important;
    line-height: 1.1 !important;
}

/* 4. HEADERS & LABELS */
.header-box {
    background: #000; color: #fff; text-align: center;
    font-size: 10px; padding: 4px 0; border-radius: 2px;
    width: 75px; 
}
.time-label { font-size: 11px; font-weight: bold; text-align: center; line-height: 80px; color: #333; }

/* 5. DATE GRID (7 wide) */
.date-grid [data-testid="column"] {
    flex: 0 0 44px !important;
    min-width: 44px !important;
}

/* 6. LOGIN BUTTON: Fixed size */
.login-box .stButton > button { width: 140px !important; height: 45px !important; margin: 0 auto; font-size: 14px !important; }

/* COLORS */
div.stButton > button:not(:disabled) { background-color: #f6ffed !important; color: #389e0d !important; border: 1px solid #b7eb8f !important; }
div.stButton > button:disabled { background-color: #fff1f0 !important; color: #cf1322 !important; border: 1px solid #ffa39e !important; opacity: 1 !important; }

/* CLEANUP PADDING */
[data-testid="stAppViewBlockContainer"] { padding: 0.5rem 0.2rem !important; }
</style>
""", unsafe_allow_html=True)

# 5. LOGIN
if st.session_state.user is None:
    st.title("🎱 POOL RESERVE")
    e = st.text_input("Email").lower().strip()
    p = st.text_input("Password", type="password")
    st.markdown('<div class="login-box">', unsafe_allow_html=True)
    if st.button("Login"):
        match = users[(users["Email"] == e) & (users["Password"] == p)]
        if not match.empty:
            st.session_state.user, st.session_state.role = e, match.iloc[0]["Role"]
            st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# 6. ADMIN/OWNER CANCEL DIALOGUE
if st.session_state.pending_cancel:
    idx, b_name = st.session_state.pending_cancel
    st.error(f"Cancel booking for {b_name}?")
    if st.button("Confirm Cancellation"):
        bookings = bookings.drop(idx)
        save_data(bookings, BOOKINGS_FILE)
        st.session_state.pending_cancel = None
        st.rerun()
    if st.button("Back"):
        st.session_state.pending_cancel = None
        st.rerun()
    st.stop()

# 7. DATE PICKER (2 rows of 7)
st.write("### 📅 Dates")
today = datetime.now().date()
for r in range(2):
    st.markdown('<div class="date-grid">', unsafe_allow_html=True)
    cols = st.columns(7)
    for i in range(7):
        d = today + timedelta(days=i + (r * 7))
        d_str = str(d)
        with cols[i]:
            lbl = d.strftime("%a\n%d")
            is_sel = (st.session_state.sel_date == d_str)
            if st.button(lbl, key=f"d_{d_str}", type="primary" if is_sel else "secondary"):
                st.session_state.sel_date = d_str
                st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

st.divider()

# 8. BOOKING TABLE
st.markdown('<div class="data-row">', unsafe_allow_html=True)
h_cols = st.columns(4)
t_names = ["Table 1", "Table 2", "Table 3"]
for i in range(3):
    h_cols[i+1].markdown(f'<div class="header-box">{t_names[i]}</div>', unsafe_allow_html=True)

# Hours from 08:00
HOURS = [f"{h:02d}:{m}" for h in (list(range(8, 24)) + list(range(0, 3))) for m in ["00", "30"]]

for t in HOURS:
    r_cols = st.columns(4)
    # Clock
    r_cols[0].markdown(f'<div class="time-label">{t}</div>', unsafe_allow_html=True)
    # Tables
    for i in range(3):
        t_n = f"Table {i+1}"
        match = bookings[(bookings["Table"] == t_n) & (bookings["Time"] == t) & (bookings["Date"] == st.session_state.sel_date)]
        with r_cols[i+1]:
            if not match.empty:
                b_user, b_name = match.iloc[0]["User"], match.iloc[0]["Name"]
                if st.session_state.role == "admin" or b_user == st.session_state.user:
                    if st.button(f"❌\n{b_name[:6]}", key=f"b_{t}_{i}"):
                        st.session_state.pending_cancel = (match.index, b_name)
                        st.rerun()
                else:
                    st.button(f"🔒\n{b_name[:6]}", key=f"b_{t}_{i}", disabled=True)
            else:
                if st.button("🟢\nFree", key=f"b_{t}_{i}"):
                    new_b = pd.DataFrame([{"User":st.session_state.user, "Name":"User", "Date":st.session_state.sel_date, "Table":t_n, "Time":t}])
                    save_data(pd.concat([bookings, new_b]), BOOKINGS_FILE)
                    st.rerun()
st.markdown('</div>', unsafe_allow_html=True)

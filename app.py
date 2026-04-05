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
    if os.path.exists(file):
        return pd.read_csv(file, dtype=str)
    return pd.DataFrame(columns=columns)

def save_data(df, file):
    df.to_csv(file, index=False)

users = load_data(USERS_FILE, ["Email", "Name", "Password", "Role"])
bookings = load_data(BOOKINGS_FILE, ["User", "Name", "Date", "Table", "Time"])

# 3. SESSION STATE
if "user" not in st.session_state: st.session_state.user = None
if "role" not in st.session_state: st.session_state.role = None
if "name" not in st.session_state: st.session_state.name = None
if "sel_date" not in st.session_state: st.session_state.sel_date = str(datetime.now().date())
if "pending_cancel" not in st.session_state: st.session_state.pending_cancel = None

# 4. FIXED GRID CSS
st.markdown("""
<style>
/* 4-COLUMN DATA GRID (Time + 3 Tables) */
.main-grid div[data-testid="stHorizontalBlock"] {
    display: grid !important;
    grid-template-columns: 50px repeat(3, 1fr) !important;
    gap: 2px !important;
    width: 100% !important;
    align-items: center;
}

/* 7-COLUMN DATE GRID */
.date-grid div[data-testid="stHorizontalBlock"] {
    display: grid !important;
    grid-template-columns: repeat(7, 1fr) !important;
    gap: 3px !important;
}

/* BUTTONS */
.stButton > button {
    width: 100% !important;
    height: 44px !important;
    padding: 0px !important;
    margin-bottom: -12px !important;
    border-radius: 4px !important;
}

/* FONT LOGIC */
.time-text { font-size: 13px; font-weight: bold; text-align: center; color: #444; }
.book-text { font-size: 11px !important; } /* 2px smaller than time */

/* HEADERS */
.header-box {
    background: #000; color: #fff; text-align: center;
    font-size: 10px; padding: 5px 0; border-radius: 4px;
}

/* COLORS */
div.stButton > button:not(:disabled) { background-color: #f6ffed !important; color: #389e0d !important; border: 1px solid #b7eb8f !important; }
div.stButton > button:disabled { background-color: #fff1f0 !important; color: #cf1322 !important; border: 1px solid #ffa39e !important; opacity: 1 !important; }
</style>
""", unsafe_allow_html=True)

# 5. ADMIN CANCEL DIALOGUE
if st.session_state.pending_cancel:
    idx, b_name = st.session_state.pending_cancel
    st.error(f"⚠️ Cancel booking for {b_name}?")
    c1, c2 = st.columns(2)
    if c1.button("Confirm Cancel"):
        bookings = bookings.drop(idx)
        save_data(bookings, BOOKINGS_FILE)
        st.session_state.pending_cancel = None
        st.rerun()
    if c2.button("Keep It"):
        st.session_state.pending_cancel = None
        st.rerun()
    st.stop()

# 6. LOGIN (Standard)
if st.session_state.user is None:
    # ... Insert Login Logic Here ...
    st.title("🎱 RESERVE")
    st.stop()

# 7. TWO-WEEK DATE PICKER (7x2 GRID)
st.markdown("### 📅 Select Date")
today_obj = datetime.now().date()
today_str = str(today_obj)

for row in range(2):
    st.markdown("<div class='date-grid'>", unsafe_allow_html=True)
    d_cols = st.columns(7)
    for i in range(7):
        d = today_obj + timedelta(days=i + (row * 7))
        d_str = str(d)
        with d_cols[i]:
            # Highlight Logic
            is_today = d_str == today_str
            is_selected = d_str == st.session_state.sel_date
            
            # Label with "TODAY" indicator
            lbl = d.strftime("%a\n%d")
            if is_today: lbl = f"TODAY\n{d.day}"
            
            # Use Primary color (Blue/Red depending on theme) for the selected day
            if st.button(lbl, key=f"date_{d_str}", type="primary" if is_selected else "secondary"):
                st.session_state.sel_date = d_str
                st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

st.divider()

# 8. THE BOOKING TABLE
st.markdown("<div class='main-grid'>", unsafe_allow_html=True)
h_cols = st.columns(4)
with h_cols[0]: st.write("") # Time column header
t_names = ["Table 1", "Table 2", "Table 3"]
for i in range(3):
    h_cols[i+1].markdown(f"<div class='header-box'>{t_names[i]}</div>", unsafe_allow_html=True)

HOURS = [f"{h:02d}:{m}" for h in (list(range(8, 24)) + list(range(0, 3))) for m in ["00", "30"]]

for t in HOURS:
    row_cols = st.columns(4)
    # Col 0: Clock
    row_cols[0].markdown(f"<div class='time-text'>{t}</div>", unsafe_allow_html=True)
    
    # Col 1-3: Tables
    for i in range(3):
        t_name = t_names[i]
        match = bookings[(bookings["Table"] == t_name) & (bookings["Time"] == t) & (bookings["Date"] == st.session_state.sel_date)]
        key = f"btn_{i}_{t}"
        
        with row_cols[i+1]:
            if not match.empty:
                b_user, b_name = match.iloc[0]["User"], match.iloc[0]["Name"]
                # Symbol + Name (Clock is already on the left)
                label = f"❌ {b_name[:6]}"
                if st.session_state.role == "admin" or b_user == st.session_state.user:
                    if st.button(label, key=key):
                        st.session_state.pending_cancel = (match.index, b_name)
                        st.rerun()
                else:
                    st.button(f"🔒 {b_name[:6]}", key=key, disabled=True)
            else:
                if st.button("🟢 Free", key=key):
                    new_b = pd.DataFrame([{"User":st.session_state.user, "Name":st.session_state.name, "Date":st.session_state.sel_date, "Table":t_name, "Time":t}])
                    save_data(pd.concat([bookings, new_b]), BOOKINGS_FILE)
                    st.rerun()
st.markdown("</div>", unsafe_allow_html=True)

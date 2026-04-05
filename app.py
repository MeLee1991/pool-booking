import os
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

# 1. PAGE CONFIG
st.set_page_config(page_title="Pool Booking", layout="wide", initial_sidebar_state="collapsed")

# 2. DATA HANDLER
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

# 4. THE ULTIMATE CSS (FORCED GRIDS)
st.markdown("""
<style>
/* --- DATE GRID: FORCE 7 COLUMNS --- */
.date-section [data-testid="stHorizontalBlock"] {
    display: grid !important;
    grid-template-columns: repeat(7, 1fr) !important;
    gap: 2px !important;
    margin-bottom: -15px !important;
}

/* --- BOOKING GRID: FORCE 4 COLUMNS (Time + 3 Tables) --- */
.booking-section [data-testid="stHorizontalBlock"] {
    display: grid !important;
    grid-template-columns: 50px 1fr 1fr 1fr !important;
    gap: 1px !important;
    margin-bottom: -18px !important;
}

/* --- BUTTON STYLING (Low Highness, High Width) --- */
.stButton > button {
    width: 100% !important;
    height: 32px !important; /* Shrunk height as requested */
    padding: 0px !important;
    font-size: 10px !important;
    border-radius: 2px !important;
}

/* Selected Date Indicator (Blue) vs Others (Gray) */
button[kind="primary"] { background-color: #007bff !important; color: white !important; }

/* Labels */
.time-label { font-size: 11px; font-weight: bold; line-height: 32px; text-align: center; }
.header-box { background: #000; color: #fff; text-align: center; font-size: 9px; padding: 2px 0; border-radius: 2px; }

/* Colors for Booking Status */
div.stButton > button:not(:disabled):not([kind="primary"]) { background-color: #f6ffed !important; color: #389e0d !important; border: 1px solid #b7eb8f !important; }
div.stButton > button:disabled { background-color: #fff1f0 !important; color: #cf1322 !important; border: 1px solid #ffa39e !important; opacity: 1 !important; }

/* Login Button */
.login-box .stButton > button { width: 120px !important; height: 40px !important; margin: 0 auto; }

/* Eliminate Streamlit gaps */
[data-testid="stAppViewBlockContainer"] { padding: 0.5rem 0.2rem !important; }
</style>
""", unsafe_allow_html=True)

# 5. LOGIN
if st.session_state.user is None:
    st.title("🎱 RESERVE")
    e = st.text_input("Email")
    p = st.text_input("Password", type="password")
    st.markdown('<div class="login-box">', unsafe_allow_html=True)
    if st.button("Login"):
        match = users[(users["Email"] == e.lower().strip()) & (users["Password"] == p)]
        if not match.empty:
            st.session_state.user, st.session_state.name, st.session_state.role = e, match.iloc[0]["Name"], match.iloc[0]["Role"]
            st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# 6. DATE PICKER (2 Rows of 7)
st.write("### 📅 Dates")
today = datetime.now().date()
for row in range(2):
    st.markdown('<div class="date-section">', unsafe_allow_html=True)
    cols = st.columns(7)
    for i in range(7):
        d = today + timedelta(days=i + (row * 7))
        d_str = str(d)
        with cols[i]:
            lbl = d.strftime("%a\n%d")
            is_active = (st.session_state.sel_date == d_str)
            # kind="primary" makes the selected day stay a different color (Blue)
            if st.button(lbl, key=f"d_{d_str}", type="primary" if is_active else "secondary"):
                st.session_state.sel_date = d_str
                st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

st.divider()

# 7. MAIN BOOKING TABLE (4-Columns: Time | T1 | T2 | T3)
st.markdown('<div class="booking-section">', unsafe_allow_html=True)
h_cols = st.columns(4)
h_cols[0].write("") # Empty corner
t_names = ["T1", "T2", "T3"]
for i, name in enumerate(t_names):
    h_cols[i+1].markdown(f'<div class="header-box">{name}</div>', unsafe_allow_html=True)

# 08:00 to 03:00 schedule
HOURS = [f"{h:02d}:{m}" for h in (list(range(8, 24)) + list(range(0, 3))) for m in ["00", "30"]]

for t in HOURS:
    r_cols = st.columns(4)
    # Col 1: Time
    r_cols[0].markdown(f'<div class="time-label">{t}</div>', unsafe_allow_html=True)
    
    # Col 2-4: Tables
    for i in range(3):
        t_name = f"Table {i+1}"
        match = bookings[(bookings["Table"] == t_name) & (bookings["Time"] == t) & (bookings["Date"] == st.session_state.sel_date)]
        with r_cols[i+1]:
            if not match.empty:
                b_user, b_name = match.iloc[0]["User"], match.iloc[0]["Name"]
                # Admin or owner can delete
                if st.session_state.role == "admin" or b_user == st.session_state.user:
                    if st.button(f"❌ {b_name[:4]}", key=f"b_{t}_{i}"):
                        bookings = bookings.drop(match.index)
                        save_data(bookings, BOOKINGS_FILE)
                        st.rerun()
                else:
                    st.button(f"🔒 {b_name[:4]}", key=f"b_{t}_{i}", disabled=True)
            else:
                if st.button("🟢 Free", key=f"b_{t}_{i}"):
                    new_b = pd.DataFrame([{"User":st.session_state.user, "Name":st.session_state.name, "Date":st.session_state.sel_date, "Table":t_name, "Time":t}])
                    save_data(pd.concat([bookings, new_b]), BOOKINGS_FILE)
                    st.rerun()
st.markdown('</div>', unsafe_allow_html=True)

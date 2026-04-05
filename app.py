import os
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

# 1. PAGE SETUP
st.set_page_config(page_title="Pool", layout="wide", initial_sidebar_state="collapsed")

# 2. DATA HANDLING
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

# 4. THE "LOCKED" CSS (Forcing narrow columns & zero gaps)
st.markdown("""
<style>
/* 1. COMPLETELY REMOVE PADDING FROM COLUMNS */
[data-testid="column"] { padding: 0px !important; flex: none !important; }

/* 2. DATE GRID (7 columns, 42px each) */
.date-section [data-testid="stHorizontalBlock"] {
    display: grid !important;
    grid-template-columns: repeat(7, 42px) !important;
    gap: 2px !important;
    justify-content: start !important;
    margin-bottom: -15px !important;
}

/* 3. MAIN TABLE GRID (4 columns: Time + 3 Tables) */
/* This forces narrow 60px columns even in landscape */
.booking-section [data-testid="stHorizontalBlock"] {
    display: grid !important;
    grid-template-columns: 42px 60px 60px 60px !important; 
    gap: 1px !important;
    justify-content: start !important;
    margin-bottom: -22px !important;
}

/* 4. BUTTONS: Ultra Shrunk Height */
.stButton > button {
    width: 100% !important;
    height: 28px !important; /* Shrunk height */
    padding: 0px !important;
    font-size: 9px !important;
    border-radius: 2px !important;
}

/* Selected Date Color (Blue) */
button[kind="primary"] { background-color: #1a73e8 !important; color: white !important; }

/* Labels & Black Headers (Matched to column width) */
.header-box { background: #000; color: #fff; text-align: center; font-size: 8px; padding: 2px 0; border-radius: 1px; width: 60px; }
.time-label { font-size: 10px; font-weight: bold; line-height: 28px; text-align: center; color: #444; }

/* Fixed Login Size */
.login-box .stButton > button { width: 100px !important; height: 35px !important; margin: 0 auto; }

/* Global App Cleanup */
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

# 6. DATES (Separate Grid, 2 Rows of 7)
st.write("### 📅 Dates")
today = datetime.now().date()
for r in range(2):
    st.markdown('<div class="date-section">', unsafe_allow_html=True)
    cols = st.columns(7)
    for i in range(7):
        d = today + timedelta(days=i + (r * 7))
        d_str = str(d)
        with cols[i]:
            lbl = f"{d.strftime('%a')}\n{d.day}"
            is_active = (st.session_state.sel_date == d_str)
            if st.button(lbl, key=f"d_{d_str}", type="primary" if is_active else "secondary"):
                st.session_state.sel_date = d_str
                st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

st.divider()

# 7. BOOKING TABLE (LOCKED 4-COLUMN GRID)
st.markdown('<div class="booking-section">', unsafe_allow_html=True)
h_cols = st.columns(4)
t_labels = ["T1", "T2", "T3"]
for i, name in enumerate(t_labels):
    h_cols[i+1].markdown(f'<div class="header-box">{name}</div>', unsafe_allow_html=True)

HOURS = [f"{h:02d}:{m}" for h in (list(range(8, 24)) + list(range(0, 3))) for m in ["00", "30"]]

for t in HOURS:
    r_cols = st.columns(4)
    r_cols[0].markdown(f'<div class="time-label">{t}</div>', unsafe_allow_html=True)
    for i in range(3):
        t_n = f"Table {i+1}"
        match = bookings[(bookings["Table"] == t_n) & (bookings["Time"] == t) & (bookings["Date"] == st.session_state.sel_date)]
        with r_cols[i+1]:
            if not match.empty:
                b_user, b_name = match.iloc[0]["User"], match.iloc[0]["Name"]
                if st.session_state.role == "admin" or b_user == st.session_state.user:
                    if st.button(f"❌{b_name[:3]}", key=f"b_{t}_{i}"):
                        bookings = bookings.drop(match.index); save_data(bookings, BOOKINGS_FILE); st.rerun()
                else: st.button(f"🔒{b_name[:3]}", key=f"b_{t}_{i}", disabled=True)
            else:
                if st.button("Free", key=f"b_{t}_{i}"):
                    new_b = pd.DataFrame([{"User":st.session_state.user, "Name":st.session_state.name, "Date":st.session_state.sel_date, "Table":t_n, "Time":t}])
                    save_data(pd.concat([bookings, new_b]), BOOKINGS_FILE); st.rerun()
st.markdown('</div>', unsafe_allow_html=True)

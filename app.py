import os
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

# 1. SETUP
st.set_page_config(page_title="Pool", layout="wide", initial_sidebar_state="collapsed")

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

# 4. THE "TIGHT GRID" CSS
st.markdown("""
<style>
/* 1. KILL ALL COLUMN PADDING (The "Too Apart" Fix) */
[data-testid="column"] {
    padding: 0px !important;
    flex: none !important;
}

/* 2. DATE GRID: Fixed 45px per day, 7 columns */
.date-section [data-testid="stHorizontalBlock"] {
    display: grid !important;
    grid-template-columns: repeat(7, 45px) !important;
    gap: 2px !important;
    margin-bottom: -15px !important;
    justify-content: start !important;
}

/* 3. MAIN TABLE: Fixed widths, no stretching */
.table-section [data-testid="stHorizontalBlock"] {
    display: grid !important;
    grid-template-columns: 45px 75px 75px 75px !important; /* TIME | T1 | T2 | T3 */
    gap: 2px !important;
    justify-content: start !important;
    margin-bottom: -22px !important;
}

/* 4. SHRUNK BUTTONS */
.stButton > button {
    width: 100% !important;
    height: 30px !important;
    padding: 0px !important;
    font-size: 10px !important;
    border-radius: 2px !important;
}

/* 5. INDICATOR: Active Date Color */
button[kind="primary"] { 
    background-color: #2e7d32 !important; /* Dark Green for active */
    color: white !important; 
    border: 2px solid #000 !important;
}

/* Labels */
.header-box { background: #000; color: #fff; text-align: center; font-size: 9px; padding: 2px 0; border-radius: 2px; }
.time-label { font-size: 11px; font-weight: bold; line-height: 30px; text-align: center; }

/* Fixed Login */
.login-box .stButton > button { width: 120px !important; height: 40px !important; margin: 0 auto; }

/* Strip Streamlit page padding */
[data-testid="stAppViewBlockContainer"] { padding: 0.5rem 0.2rem !important; }
</style>
""", unsafe_allow_html=True)

# 5. LOGIN
if st.session_state.user is None:
    st.title("🎱 POOL")
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

# 6. DATES (2 Rows, 7 Columns)
st.write("### 📅 Dates")
today = datetime.now().date()
for row_idx in range(2):
    st.markdown('<div class="date-section">', unsafe_allow_html=True)
    cols = st.columns(7)
    for i in range(7):
        d = today + timedelta(days=i + (row_idx * 7))
        d_str = str(d)
        with cols[i]:
            # Day Name (Mon) + Day Number (06)
            lbl = f"{d.strftime('%a')}\n{d.day}"
            is_active = (st.session_state.sel_date == d_str)
            if st.button(lbl, key=f"d_{d_str}", type="primary" if is_active else "secondary"):
                st.session_state.sel_date = d_str
                st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

st.divider()

# 7. MAIN TABLE (Time + 3 Tables)
st.markdown('<div class="table-section">', unsafe_allow_html=True)
h_cols = st.columns(4)
h_cols[0].write("") # Corner
t_names = ["T1", "T2", "T3"]
for i, name in enumerate(t_names):
    h_cols[i+1].markdown(f'<div class="header-box">{name}</div>', unsafe_allow_html=True)

# Schedule
HOURS = [f"{h:02d}:{m}" for h in (list(range(8, 24)) + list(range(0, 3))) for m in ["00", "30"]]

for t in HOURS:
    r_cols = st.columns(4)
    # Time
    r_cols[0].markdown(f'<div class="time-label">{t}</div>', unsafe_allow_html=True)
    # Tables
    for i in range(3):
        t_n = f"Table {i+1}"
        match = bookings[(bookings["Table"] == t_n) & (bookings["Time"] == t) & (bookings["Date"] == st.session_state.sel_date)]
        with r_cols[i+1]:
            if not match.empty:
                b_user, b_name = match.iloc[0]["User"], match.iloc[0]["Name"]
                if st.session_state.role == "admin" or b_user == st.session_state.user:
                    if st.button(f"❌{b_name[:3]}", key=f"b_{t}_{i}"):
                        bookings = bookings.drop(match.index)
                        save_data(bookings, BOOKINGS_FILE)
                        st.rerun()
                else:
                    st.button(f"🔒{b_name[:3]}", key=f"b_{t}_{i}", disabled=True)
            else:
                if st.button("Free", key=f"b_{t}_{i}"):
                    new_b = pd.DataFrame([{"User":st.session_state.user, "Name":st.session_state.name, "Date":st.session_state.sel_date, "Table":t_n, "Time":t}])
                    save_data(pd.concat([bookings, new_b]), BOOKINGS_FILE)
                    st.rerun()
st.markdown('</div>', unsafe_allow_html=True)

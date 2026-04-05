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
if "sel_date" not in st.session_state: st.session_state.sel_date = str(datetime.now().date())

# 4. FIXED GRID CSS
st.markdown("""
<style>
/* FORCE 4-COLUMN ALIGNMENT */
[data-testid="stHorizontalBlock"] {
    display: grid !important;
    grid-template-columns: 45px 65px 65px 65px !important;
    gap: 0px !important;
    width: fit-content !important;
    align-items: center !important;
}

/* REMOVE ALL PADDING */
[data-testid="column"] { padding: 0px !important; flex: none !important; }

/* ROW WRAPPER: Full width background and border */
.row-container {
    display: flex !important;
    border-bottom: 1px solid #eee;
    border-right: 1px solid #eee;
}

/* ALTERNATING COLORS (Whole Row) */
.bg-even { background-color: #f7f7f7 !important; }
.bg-odd { background-color: #ffffff !important; }

/* BUTTONS: Shrunk & Locked */
.stButton > button {
    width: 63px !important;
    height: 30px !important;
    font-size: 10px !important;
    padding: 0px !important;
    border-radius: 0px !important;
    border: 1px solid #ddd !important;
    margin: 0px !important;
}

/* TIME LABEL: Locked to same height as buttons */
.time-box {
    width: 45px;
    height: 30px;
    line-height: 30px;
    font-size: 10px;
    font-weight: bold;
    text-align: center;
    border-left: 1px solid #eee;
}

/* HEADERS: Fixed Black Boxes */
.header-box { 
    background: #000; color: #fff; text-align: center; 
    font-size: 9px; height: 20px; line-height: 20px;
    width: 65px; border: 1px solid #333;
}

/* DATES: 7-Column Grid */
.date-section [data-testid="stHorizontalBlock"] {
    grid-template-columns: repeat(7, 45px) !important;
    margin-bottom: -10px !important;
}
.date-section .stButton > button { width: 43px !important; height: 35px !important; border-radius: 4px !important; }

/* Global Cleanup */
[data-testid="stAppViewBlockContainer"] { padding: 0.5rem 0.2rem !important; }
</style>
""", unsafe_allow_html=True)

# 5. LOGIN
if st.session_state.user is None:
    st.title("🎱 RESERVE")
    e = st.text_input("Email").lower().strip()
    p = st.text_input("Password", type="password")
    if st.button("Login"):
        match = users[(users["Email"] == e) & (users["Password"] == p)]
        if not match.empty:
            st.session_state.user, st.session_state.name, st.session_state.role = e, match.iloc[0]["Name"], match.iloc[0]["Role"]
            st.rerun()
    st.stop()

# 6. DATES (7 Columns, 2 Rows)
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
                st.session_state.sel_date = d_str; st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

st.divider()

# 7. TABLE
# Header
st.markdown('<div class="row-container">', unsafe_allow_html=True)
h_cols = st.columns(4)
h_cols[0].write("") # Corner
for i, name in enumerate(["T1", "T2", "T3"]):
    h_cols[i+1].markdown(f'<div class="header-box">{name}</div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# Rows
HOURS = [f"{h:02d}:{m}" for h in (list(range(8, 24)) + list(range(0, 3))) for m in ["00", "30"]]

for idx, t in enumerate(HOURS):
    # Whole row background toggle every hour (2 slots)
    bg_style = "bg-even" if (idx // 2) % 2 == 0 else "bg-odd"
    
    st.markdown(f'<div class="row-container {bg_style}">', unsafe_allow_html=True)
    r_cols = st.columns(4)
    
    # Time
    with r_cols[0]:
        st.markdown(f'<div class="time-box">{t}</div>', unsafe_allow_html=True)
        
    # Tables
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

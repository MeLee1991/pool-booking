import os
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

# 1. PAGE SETUP
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

# 4. ADVANCED CSS (FORCING HORIZONTAL & ALTERNATING COLORS)
st.markdown("""
<style>
/* --- FORCE HORIZONTAL LAYOUT IN PORTRAIT --- */
[data-testid="stHorizontalBlock"] {
    display: flex !important;
    flex-direction: row !important;
    flex-wrap: nowrap !important;
    align-items: center !important;
    justify-content: flex-start !important;
    gap: 1px !important;
}

[data-testid="column"] {
    flex: 0 0 auto !important;
    min-width: 0px !important;
    padding: 0px !important;
}

/* --- DATES: Fixed Widths --- */
.date-section [data-testid="column"] { width: 42px !important; }

/* --- TABLE: Fixed Widths (Time + 3 Tables) --- */
.table-section [data-testid="column"]:nth-child(1) { width: 45px !important; } /* Time */
.table-section [data-testid="column"]:not(:nth-child(1)) { width: 62px !important; } /* Tables */

/* --- BUTTONS: Shrunk & Tight --- */
.stButton > button {
    width: 100% !important;
    height: 30px !important;
    font-size: 9px !important;
    padding: 0px !important;
    border-radius: 2px !important;
}

/* --- ALTERNATING HOUR BACKGROUNDS --- */
.time-bg-grey { background-color: #f0f2f6; border-radius: 2px; }
.time-bg-white { background-color: transparent; }

.time-label {
    font-size: 10px; font-weight: bold; line-height: 30px; 
    text-align: center; width: 100%; display: block;
}

/* Black Headers */
.header-box { background: #000; color: #fff; text-align: center; font-size: 8px; padding: 2px 0; border-radius: 1px; }

/* Fixed Login */
.login-box .stButton > button { width: 120px !important; height: 40px !important; margin: 0 auto; }

/* Global Cleanup */
[data-testid="stAppViewBlockContainer"] { padding: 0.5rem 0.2rem !important; }
</style>
""", unsafe_allow_html=True)

# 5. LOGIN
if st.session_state.user is None:
    st.title("🎱 POOL")
    e = st.text_input("Email").lower().strip()
    p = st.text_input("Password", type="password")
    st.markdown('<div class="login-box">', unsafe_allow_html=True)
    if st.button("Login"):
        match = users[(users["Email"] == e) & (users["Password"] == p)]
        if not match.empty:
            st.session_state.user, st.session_state.name, st.session_state.role = e, match.iloc[0]["Name"], match.iloc[0]["Role"]
            st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# 6. DATES (2 Rows of 7, Horizontal)
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

# 7. BOOKING TABLE (4 Columns: Time | T1 | T2 | T3)
st.markdown('<div class="table-section">', unsafe_allow_html=True)
# Headers
h_cols = st.columns(4)
t_labels = ["T1", "T2", "T3"]
for i, name in enumerate(t_labels):
    h_cols[i+1].markdown(f'<div class="header-box">{name}</div>', unsafe_allow_html=True)

# Hours 08:00 to 03:00
HOURS = [f"{h:02d}:{m}" for h in (list(range(8, 24)) + list(range(0, 3))) for m in ["00", "30"]]

for idx, t in enumerate(HOURS):
    # Logic: Toggle background every 2 rows (every hour)
    bg_class = "time-bg-grey" if (idx // 2) % 2 == 0 else "time-bg-white"
    
    r_cols = st.columns(4)
    # Column 1: Time with alternating background
    r_cols[0].markdown(f'<div class="{bg_class}"><span class="time-label">{t}</span></div>', unsafe_allow_html=True)
    
    # Columns 2-4: Tables
    for i in range(3):
        t_n = f"Table {i+1}"
        match = bookings[(bookings["Table"] == t_n) & (bookings["Time"] == t) & (bookings["Date"] == st.session_state.sel_date)]
        with r_cols[i+1]:
            if not match.empty:
                b_user, b_name = match.iloc[0]["User"], match.iloc[0]["Name"]
                btn_label = f"❌{b_name[:3]}"
                if st.session_state.role == "admin" or b_user == st.session_state.user:
                    if st.button(btn_label, key=f"b_{t}_{i}"):
                        bookings = bookings.drop(match.index); save_data(bookings, BOOKINGS_FILE); st.rerun()
                else: st.button(f"🔒{b_name[:3]}", key=f"b_{t}_{i}", disabled=True)
            else:
                if st.button("Free", key=f"b_{t}_{i}"):
                    new_b = pd.DataFrame([{"User":st.session_state.user, "Name":st.session_state.name, "Date":st.session_state.sel_date, "Table":t_n, "Time":t}])
                    save_data(pd.concat([bookings, new_b]), BOOKINGS_FILE); st.rerun()
st.markdown('</div>', unsafe_allow_html=True)

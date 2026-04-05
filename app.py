import os
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

# 1. PAGE SETUP
st.set_page_config(page_title="Pool Booking", layout="wide", initial_sidebar_state="collapsed")

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
if "name" not in st.session_state: st.session_state.name = None
if "role" not in st.session_state: st.session_state.role = None
if "sel_date" not in st.session_state: st.session_state.sel_date = str(datetime.now().date())
if "pending_cancel" not in st.session_state: st.session_state.pending_cancel = None

# 4. CSS TO FORCE HORIZONTAL COLUMNS ON MOBILE
st.markdown("""
<style>
/* FORCE COLUMNS TO STAY SIDE-BY-SIDE (NO STACKING) */
[data-testid="stHorizontalBlock"] {
    display: flex !important;
    flex-direction: row !important;
    flex-wrap: nowrap !important;
    align-items: center !important;
    gap: 2px !important;
}

/* DATE GRID: 7 items per row */
.date-section [data-testid="column"] {
    flex: 1 1 0% !important;
    min-width: 0px !important;
}

/* DATA GRID: Time (fixed) + 3 Tables (equal) */
.data-section [data-testid="column"]:nth-child(1) {
    flex: 0 0 50px !important;
    min-width: 50px !important;
}
.data-section [data-testid="column"]:not(:nth-child(1)) {
    flex: 1 1 0% !important;
    min-width: 0px !important;
}

/* BUTTONS STYLING */
.stButton > button {
    width: 100% !important;
    height: 42px !important;
    padding: 0px !important;
    font-size: 10px !important;
    border-radius: 4px !important;
}

/* LOGIN BUTTON: Fixed size, not expanding */
.login-btn-container .stButton > button {
    width: 120px !important;
    margin: 0 auto !important;
    display: block !important;
}

.time-label { font-size: 12px; font-weight: bold; text-align: center; }
.header-box { background: #000; color: #fff; text-align: center; font-size: 9px; padding: 4px 0; border-radius: 4px; }

/* COLORS */
div.stButton > button:not(:disabled) { background-color: #f6ffed !important; color: #389e0d !important; border: 1px solid #b7eb8f !important; }
div.stButton > button:disabled { background-color: #fff1f0 !important; color: #cf1322 !important; border: 1px solid #ffa39e !important; opacity: 1 !important; }

/* APP PADDING */
[data-testid="stAppViewBlockContainer"] { padding: 1rem 0.3rem !important; }
</style>
""", unsafe_allow_html=True)

# 5. LOGIN SCREEN
if st.session_state.user is None:
    st.title("🎱 POOL RESERVE")
    email = st.text_input("Email").lower().strip()
    password = st.text_input("Password", type="password")
    st.markdown('<div class="login-btn-container">', unsafe_allow_html=True)
    if st.button("Login"):
        match = users[(users["Email"] == email) & (users["Password"] == password)]
        if not match.empty:
            st.session_state.user = email
            st.session_state.name = match.iloc[0]["Name"]
            st.session_state.role = match.iloc[0]["Role"]
            st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# 6. ADMIN CANCELLATION OVERLAY
if st.session_state.pending_cancel:
    idx, b_name = st.session_state.pending_cancel
    st.warning(f"Cancel booking for: {b_name}?")
    if st.button("YES, CANCEL"):
        bookings = bookings.drop(idx)
        save_data(bookings, BOOKINGS_FILE)
        st.session_state.pending_cancel = None
        st.rerun()
    if st.button("Back"):
        st.session_state.pending_cancel = None
        st.rerun()
    st.stop()

# 7. DATE PICKER (2 rows of 7 columns)
st.write("### 📅 Select Date")
today = datetime.now().date()
for row_idx in range(2):
    st.markdown('<div class="date-section">', unsafe_allow_html=True)
    cols = st.columns(7)
    for i in range(7):
        d = today + timedelta(days=i + (row_idx * 7))
        d_str = str(d)
        with cols[i]:
            lbl = d.strftime("%a\n%d")
            if d_str == str(today): lbl = f"Today\n{d.day}"
            is_sel = (st.session_state.sel_date == d_str)
            if st.button(lbl, key=f"d_{d_str}", type="primary" if is_sel else "secondary"):
                st.session_state.sel_date = d_str
                st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

st.divider()

# 8. BOOKING TABLE (Time | Table 1 | Table 2 | Table 3)
st.markdown('<div class="data-section">', unsafe_allow_html=True)
h_cols = st.columns(4)
h_cols[0].write("") # Empty corner
t_names = ["Tbl 1", "Tbl 2", "Tbl 3"]
for i in range(3):
    h_cols[i+1].markdown(f'<div class="header-box">{t_names[i]}</div>', unsafe_allow_html=True)

# Time slots from 08:00
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
                    if st.button(f"❌ {b_name[:5]}", key=f"b_{t}_{i}"):
                        st.session_state.pending_cancel = (match.index, b_name)
                        st.rerun()
                else:
                    st.button(f"🔒 {b_name[:5]}", key=f"b_{t}_{i}", disabled=True)
            else:
                if st.button("🟢 Free", key=f"b_{t}_{i}"):
                    new_b = pd.DataFrame([{"User":st.session_state.user, "Name":st.session_state.name, "Date":st.session_state.sel_date, "Table":t_n, "Time":t}])
                    save_data(pd.concat([bookings, new_b]), BOOKINGS_FILE)
                    st.rerun()
st.markdown('</div>', unsafe_allow_html=True)

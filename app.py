import os
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

# 1. PAGE SETUP
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
if "name" not in st.session_state: st.session_state.name = None
if "sel_date" not in st.session_state: st.session_state.sel_date = str(datetime.now().date())
if "pending_cancel" not in st.session_state: st.session_state.pending_cancel = None

# 4. HARDCORE CSS GRID (The "No-Stack" Solution)
st.markdown("""
<style>
/* FORCE DATE GRID: 7 Columns wide */
.date-grid [data-testid="stHorizontalBlock"] {
    display: grid !important;
    grid-template-columns: repeat(7, 1fr) !important;
    gap: 2px !important;
}

/* FORCE DATA GRID: 4 Columns wide (Time + 3 Tables) */
.data-grid [data-testid="stHorizontalBlock"] {
    display: grid !important;
    grid-template-columns: 60px 1fr 1fr 1fr !important;
    gap: 2px !important;
    align-items: center;
}

/* Fix Streamlit column stretching */
[data-testid="column"] { width: auto !important; flex: unset !important; min-width: 0px !important; }

/* BUTTONS */
.stButton > button {
    width: 100% !important;
    height: 48px !important;
    padding: 0px !important;
    margin-bottom: -12px !important;
    border-radius: 4px !important;
    font-size: 11px !important;
}

/* LABELS */
.time-col { font-size: 14px; font-weight: bold; text-align: center; color: #333; }
.name-small { font-size: 11px !important; } /* 2px smaller than clock */
.header-box { background: #000; color: #fff; text-align: center; font-size: 10px; padding: 5px 0; border-radius: 4px; }

/* COLORS */
div.stButton > button:not(:disabled) { background-color: #f6ffed !important; color: #389e0d !important; border: 1px solid #b7eb8f !important; }
div.stButton > button:disabled { background-color: #fff1f0 !important; color: #cf1322 !important; border: 1px solid #ffa39e !important; opacity: 1 !important; }
</style>
""", unsafe_allow_html=True)

# 5. AUTHENTICATION (Skip styling for Login)
if st.session_state.user is None:
    st.title("🎱 RESERVE")
    auth = st.radio("", ["Login", "Register"], horizontal=True)
    e = st.text_input("Email").lower().strip()
    p = st.text_input("Password", type="password")
    if auth == "Login":
        if st.button("Log In"):
            m = users[(users["Email"] == e) & (users["Password"] == p)]
            if not m.empty:
                st.session_state.user, st.session_state.name, st.session_state.role = e, m.iloc[0]["Name"], m.iloc[0]["Role"]
                st.rerun()
            else: st.error("Invalid credentials")
    else:
        n = st.text_input("Name")
        if st.button("Register"):
            r = "admin" if users.empty else "user"
            save_data(pd.concat([users, pd.DataFrame([{"Email":e,"Name":n,"Password":p,"Role":r}])]), USERS_FILE)
            st.rerun()
    st.stop()

# 6. ADMIN CANCELLATION
if st.session_state.pending_cancel:
    idx, b_name = st.session_state.pending_cancel
    st.warning(f"⚠️ Cancel {b_name}?")
    if st.button("Yes, Cancel Booking"):
        bookings = bookings.drop(idx)
        save_data(bookings, BOOKINGS_FILE)
        st.session_state.pending_cancel = None
        st.rerun()
    if st.button("No, Keep"):
        st.session_state.pending_cancel = None
        st.rerun()
    st.stop()

# 7. TWO-WEEK DATE PICKER (2 Rows x 7 Columns)
st.write("### 📅 Dates")
today = datetime.now().date()
for row in range(2):
    with st.container(border=False):
        st.markdown('<div class="date-grid">', unsafe_allow_html=True)
        cols = st.columns(7)
        for i in range(7):
            d = today + timedelta(days=i + (row * 7))
            d_str = str(d)
            with cols[i]:
                lbl = d.strftime("%a\n%d")
                if d_str == str(today): lbl = f"TODAY\n{d.day}"
                is_sel = (st.session_state.sel_date == d_str)
                if st.button(lbl, key=f"dt_{d_str}", type="primary" if is_sel else "secondary"):
                    st.session_state.sel_date = d_str
                    st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

st.divider()

# 8. THE BOOKING TABLE (4 Columns: Time | Tbl1 | Tbl2 | Tbl3)
st.markdown('<div class="data-grid">', unsafe_allow_html=True)
h_cols = st.columns(4)
h_cols[0].write("") # Time header empty
t_names = ["Table 1", "Table 2", "Table 3"]
for i in range(3):
    h_cols[i+1].markdown(f'<div class="header-box">{t_names[i]}</div>', unsafe_allow_html=True)

# Hours starting at 06:00
HOURS = [f"{h:02d}:{m}" for h in (list(range(6, 24)) + list(range(0, 3))) for m in ["00", "30"]]

for t in HOURS:
    row_cols = st.columns(4)
    # Col 1: TIME
    row_cols[0].markdown(f'<div class="time-col">{t}</div>', unsafe_allow_html=True)
    
    # Col 2-4: TABLES
    for i in range(3):
        t_n = t_names[i]
        match = bookings[(bookings["Table"] == t_n) & (bookings["Time"] == t) & (bookings["Date"] == st.session_state.sel_date)]
        key = f"slot_{t}_{i}"
        
        with row_cols[i+1]:
            if not match.empty:
                b_user, b_name = match.iloc[0]["User"], match.iloc[0]["Name"]
                # Display Symbol + Name (Clock is already on the left)
                if st.session_state.role == "admin" or b_user == st.session_state.user:
                    if st.button(f"❌ {b_name[:6]}", key=key):
                        st.session_state.pending_cancel = (match.index, b_name)
                        st.rerun()
                else:
                    st.button(f"🔒 {b_name[:6]}", key=key, disabled=True)
            else:
                if st.button("🟢 Free", key=key):
                    new_b = pd.DataFrame([{"User": st.session_state.user, "Name": st.session_state.name, "Date": st.session_state.sel_date, "Table": t_n, "Time": t}])
                    save_data(pd.concat([bookings, new_b]), BOOKINGS_FILE)
                    st.rerun()
st.markdown('</div>', unsafe_allow_html=True)

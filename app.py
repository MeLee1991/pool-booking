import os
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

# 1. SETUP
st.set_page_config(page_title="Pool Booking", layout="wide", initial_sidebar_state="collapsed")

# 2. DATA LOADERS
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

# 4. THE "NO-STACK" CSS OVERRIDE
st.markdown("""
<style>
/* 1. DATE GRID: Force 7 Columns */
.date-section [data-testid="stHorizontalBlock"] {
    display: grid !important;
    grid-template-columns: repeat(7, 1fr) !important;
    gap: 2px !important;
    width: 100% !important;
}

/* 2. DATA GRID: Force 4 Columns (Time + 3 Tables) */
.data-section [data-testid="stHorizontalBlock"] {
    display: grid !important;
    grid-template-columns: 55px 1fr 1fr 1fr !important;
    gap: 2px !important;
    width: 100% !important;
    align-items: center;
}

/* 3. BUTTONS & FONTS */
.stButton > button {
    width: 100% !important;
    height: 48px !important;
    padding: 0px !important;
    margin-bottom: -12px !important;
    border-radius: 4px !important;
}
.time-label { font-size: 13px; font-weight: bold; text-align: center; color: #333; }
.header-box { background: #000; color: #fff; text-align: center; font-size: 10px; padding: 5px 0; border-radius: 4px; }

/* 4. COLORS */
div.stButton > button:not(:disabled) { background-color: #f6ffed !important; color: #389e0d !important; border: 1px solid #b7eb8f !important; }
div.stButton > button:disabled { background-color: #fff1f0 !important; color: #cf1322 !important; border: 1px solid #ffa39e !important; opacity: 1 !important; }

/* Prevent Streamlit from adding side padding on mobile */
[data-testid="stAppViewBlockContainer"] { padding: 1rem 0.5rem !important; }
</style>
""", unsafe_allow_html=True)

# 5. AUTH (Simplified for speed)
if st.session_state.user is None:
    st.title("🎱 RESERVE")
    auth = st.radio("", ["Login", "Register"], horizontal=True)
    e = st.text_input("Email").lower().strip()
    p = st.text_input("Pass", type="password")
    if auth == "Login" and st.button("Go"):
        m = users[(users["Email"] == e) & (users["Password"] == p)]
        if not m.empty:
            st.session_state.user, st.session_state.name, st.session_state.role = e, m.iloc[0]["Name"], m.iloc[0]["Role"]
            st.rerun()
        else: st.error("Invalid credentials")
    elif auth == "Register" and st.button("Create"):
        n = st.text_input("Name")
        save_data(pd.concat([users, pd.DataFrame([{"Email":e,"Name":n,"Password":p,"Role":"user"}])]), USERS_FILE)
        st.rerun()
    st.stop()

# 6. ADMIN CANCEL DIALOGUE
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

# 7. DATE PICKER (Independent 7-Column Rows)
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
            if d_str == str(today): lbl = f"⭐\n{d.day}"
            is_sel = (st.session_state.sel_date == d_str)
            if st.button(lbl, key=f"d_{d_str}", type="primary" if is_sel else "secondary"):
                st.session_state.sel_date = d_str
                st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

st.divider()

# 8. THE MAIN TABLE (Headers: Time | T1 | T2 | T3)
st.markdown('<div class="data-section">', unsafe_allow_html=True)
h_cols = st.columns(4)
t_names = ["Table 1", "Table 2", "Table 3"]
for i in range(3):
    h_cols[i+1].markdown(f'<div class="header-box">{t_names[i]}</div>', unsafe_allow_html=True)

HOURS = [f"{h:02d}:{m}" for h in (list(range(6, 24)) + list(range(0, 3))) for m in ["00", "30"]]

for t in HOURS:
    r_cols = st.columns(4)
    r_cols[0].markdown(f'<div class="time-label">{t}</div>', unsafe_allow_html=True)
    for i in range(3):
        t_n = t_names[i]
        match = bookings[(bookings["Table"] == t_n) & (bookings["Time"] == t) & (bookings["Date"] == st.session_state.sel_date)]
        with r_cols[i+1]:
            if not match.empty:
                b_user, b_name = match.iloc[0]["User"], match.iloc[0]["Name"]
                # Symbol + Name
                if st.session_state.role == "admin" or b_user == st.session_state.user:
                    if st.button(f"❌ {b_name[:5]}", key=f"bt_{t}_{i}"):
                        st.session_state.pending_cancel = (match.index, b_name)
                        st.rerun()
                else:
                    st.button(f"🔒 {b_name[:5]}", key=f"bt_{t}_{i}", disabled=True)
            else:
                if st.button("🟢 Free", key=f"bt_{t}_{i}"):
                    new_b = pd.DataFrame([{"User":st.session_state.user, "Name":st.session_state.name, "Date":st.session_state.sel_date, "Table":t_n, "Time":t}])
                    save_data(pd.concat([bookings, new_b]), BOOKINGS_FILE)
                    st.rerun()
st.markdown('</div>', unsafe_allow_html=True)

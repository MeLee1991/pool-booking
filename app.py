import os
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

# 1. PAGE CONFIG
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

# 4. CONDITIONAL CSS
# We only apply the tight grid CSS IF the user is logged in.
if st.session_state.user:
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
    .stButton > button {
        width: 100% !important;
        height: 48px !important;
        padding: 0px !important;
        margin-bottom: -12px !important;
        border-radius: 4px !important;
    }
    .time-text { font-size: 13px; font-weight: bold; text-align: center; color: #444; }
    .header-box {
        background: #000; color: #fff; text-align: center;
        font-size: 10px; padding: 5px 0; border-radius: 4px;
    }
    /* COLORS */
    div.stButton > button:not(:disabled) { background-color: #f6ffed !important; color: #389e0d !important; border: 1px solid #b7eb8f !important; }
    div.stButton > button:disabled { background-color: #fff1f0 !important; color: #cf1322 !important; border: 1px solid #ffa39e !important; opacity: 1 !important; }
    /* SELECTED DATE BUTTON */
    button[kind="primary"] { background-color: #007bff !important; color: white !important; }
    </style>
    """, unsafe_allow_html=True)

# 5. LOGIN SCREEN (Full Width, no custom grid)
if st.session_state.user is None:
    st.title("🎱 RESERVE")
    auth_choice = st.radio("Welcome", ["Login", "Register"], horizontal=True)
    
    with st.container():
        email = st.text_input("Email").lower().strip()
        password = st.text_input("Password", type="password")
        
        if auth_choice == "Login":
            if st.button("Log In", use_container_width=True):
                match = users[(users["Email"] == email) & (users["Password"] == password)]
                if not match.empty:
                    st.session_state.user = email
                    st.session_state.name = match.iloc[0]["Name"]
                    st.session_state.role = match.iloc[0]["Role"]
                    st.rerun()
                else:
                    st.error("Invalid credentials")
        else:
            new_name = st.text_input("Full Name")
            if st.button("Create Account", use_container_width=True):
                if email and password and new_name:
                    role = "admin" if users.empty else "user"
                    new_user = pd.DataFrame([{"Email": email, "Name": new_name, "Password": password, "Role": role}])
                    save_data(pd.concat([users, new_user]), USERS_FILE)
                    st.success("Registration complete! Please Login.")
    st.stop()

# 6. ADMIN CANCEL OVERLAY
if st.session_state.pending_cancel:
    idx, b_name = st.session_state.pending_cancel
    st.warning(f"⚠️ Cancel {b_name}'s booking?")
    c1, c2 = st.columns(2)
    if c1.button("Confirm"):
        bookings = bookings.drop(idx)
        save_data(bookings, BOOKINGS_FILE)
        st.session_state.pending_cancel = None
        st.rerun()
    if c2.button("Keep"):
        st.session_state.pending_cancel = None
        st.rerun()
    st.stop()

# 7. LOGOUT
st.sidebar.button("Logout", on_click=lambda: st.session_state.clear())

# 8. DATE PICKER (2 Rows of 7)
st.write("### 📅 Dates")
today = datetime.now().date()
for row_idx in range(2):
    st.markdown("<div class='date-grid'>", unsafe_allow_html=True)
    d_cols = st.columns(7)
    for i in range(7):
        current_d = today + timedelta(days=i + (row_idx * 7))
        d_str = str(current_d)
        with d_cols[i]:
            # Indicator Logic
            label = current_d.strftime("%a\n%d")
            if d_str == str(today): label = f"TODAY\n{current_d.day}"
            
            is_sel = (st.session_state.sel_date == d_str)
            if st.button(label, key=f"date_{d_str}", type="primary" if is_sel else "secondary"):
                st.session_state.sel_date = d_str
                st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

st.divider()

# 9. BOOKING TABLE (4 Columns: Time + Table 1-3)
st.markdown("<div class='main-grid'>", unsafe_allow_html=True)
h_cols = st.columns(4)
with h_cols[0]: st.write("") # Header for Time col
tables = ["Table 1", "Table 2", "Table 3"]
for i, t_name in enumerate(tables):
    h_cols[i+1].markdown(f"<div class='header-box'>{t_name}</div>", unsafe_allow_html=True)

HOURS = [f"{h:02d}:{m}" for h in (list(range(8, 24)) + list(range(0, 3))) for m in ["00", "30"]]

for t in HOURS:
    row = st.columns(4)
    # Column 1: Time
    row[0].markdown(f"<div class='time-text'>{t}</div>", unsafe_allow_html=True)
    
    # Columns 2-4: Tables
    for i, t_name in enumerate(tables):
        match = bookings[(bookings["Table"] == t_name) & (bookings["Time"] == t) & (bookings["Date"] == st.session_state.sel_date)]
        btn_key = f"b_{t}_{i}"
        
        with row[i+1]:
            if not match.empty:
                b_user, b_name = match.iloc[0]["User"], match.iloc[0]["Name"]
                # Symbol + Name (2px smaller than time)
                if st.session_state.role == "admin" or b_user == st.session_state.user:
                    if st.button(f"❌ {b_name[:6]}", key=btn_key):
                        st.session_state.pending_cancel = (match.index, b_name)
                        st.rerun()
                else:
                    st.button(f"🔒 {b_name[:6]}", key=btn_key, disabled=True)
            else:
                if st.button("🟢 Free", key=btn_key):
                    new_booking = pd.DataFrame([{"User": st.session_state.user, "Name": st.session_state.name, "Date": st.session_state.sel_date, "Table": t_name, "Time": t}])
                    save_data(pd.concat([bookings, new_booking]), BOOKINGS_FILE)
                    st.rerun()
st.markdown("</div>", unsafe_allow_html=True)

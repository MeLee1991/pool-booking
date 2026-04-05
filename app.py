import os
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

# 1. SETUP & MOBILE OPTIMIZATION
st.set_page_config(page_title="Pool Booking", layout="wide", initial_sidebar_state="collapsed")

# 2. DATA LOADERS
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
if "tables" not in st.session_state: st.session_state.tables = ["Table 1", "Table 2", "Table 3"]

# 4. "ZERO-GAP" CSS FOR 3-COLUMN MOBILE VIEW
st.markdown("""
<style>
/* 1. REMOVE ALL STREAMLIT PADDING/GAPS */
[data-testid="stHorizontalBlock"] {
    gap: 0px !important; 
    display: flex !important;
    flex-direction: row !important;
    flex-wrap: nowrap !important;
}
[data-testid="column"] {
    padding: 0 1px !important; /* Tiny 1px gap for visual separation */
    flex: 1 1 33.3% !important;
    min-width: 0 !important;
}

/* 2. FANCY BUTTON DESIGN */
.stButton > button {
    width: 100% !important;
    height: 48px !important;
    font-size: 11px !important;
    padding: 0 !important;
    margin-bottom: -15px !important;
    border-radius: 4px !important;
    border: 1px solid #ddd !important;
    white-space: pre-wrap !important;
}

/* 3. COLOR PALETTE */
div.stButton > button:not(:disabled) { background-color: #f6ffed !important; color: #389e0d !important; } /* Green */
div.stButton > button:disabled { background-color: #fff1f0 !important; color: #cf1322 !important; opacity: 1 !important; } /* Red */

.tbl-header {
    background: #000; color: #fff; text-align: center; 
    font-size: 11px; padding: 4px 0; border-radius: 2px; margin-bottom: 15px;
}
</style>
""", unsafe_allow_html=True)

# 5. AUTH FLOW
if st.session_state.user is None:
    st.title("RESERVE TABLE")
    auth_tab = st.radio("Select", ["Login", "Register"], horizontal=True)
    e = st.text_input("Email").strip().lower()
    p = st.text_input("Password", type="password").strip()
    
    if auth_tab == "Login":
        if st.button("Log In", use_container_width=True):
            match = users[(users["Email"] == e) & (users["Password"] == p)]
            if not match.empty:
                st.session_state.user, st.session_state.name, st.session_state.role = e, match.iloc[0]["Name"], match.iloc[0]["Role"]
                st.rerun()
            else: st.error("Wrong credentials")
    else:
        n = st.text_input("Full Name").strip()
        if st.button("Create Account", use_container_width=True):
            if e and p and n:
                role = "admin" if users.empty else "user"
                new_u = pd.DataFrame([{"Email":e, "Name":n, "Password":p, "Role":role}])
                save_data(pd.concat([users, new_u]), USERS_FILE)
                st.success("Registered! Switch to Login tab.")
    st.stop()

# 6. MAIN INTERFACE
st.sidebar.button("Logout", on_click=lambda: st.session_state.clear())
st.title("🎱 BOOKING")

# --- THE FANCY DATE PICKER ---
# This opens a calendar/month view when clicked. Much cosier!
sel_date_obj = st.date_input(
    "📅 Pick a Date", 
    value=datetime.now().date(),
    min_value=datetime.now().date(),
    max_value=datetime.now().date() + timedelta(days=30)
)
sel_date = str(sel_date_obj)

# Render Table Headers
h_cols = st.columns(3)
for i in range(3):
    h_cols[i].markdown(f"<div class='tbl-header'>{st.session_state.tables[i]}</div>", unsafe_allow_html=True)

# THE GRID
HOURS = [f"{h:02d}:{m}" for h in (list(range(8, 24)) + list(range(0, 3))) for m in ["00", "30"]]

for t in HOURS:
    t_cols = st.columns(3)
    for i in range(3):
        t_name = st.session_state.tables[i]
        match = bookings[(bookings["Table"] == t_name) & (bookings["Time"] == t) & (bookings["Date"] == sel_date)]
        key = f"b_{i}_{t}_{sel_date}"
        
        with t_cols[i]:
            if not match.empty:
                b_user, b_name = match.iloc[0]["User"], match.iloc[0]["Name"]
                
                # ADMIN or OWNER can delete
                if b_user == st.session_state.user or st.session_state.role == "admin":
                    if st.button(f"{t}\n❌ {b_name[:6]}", key=key):
                        bookings = bookings.drop(match.index)
                        save_data(bookings, BOOKINGS_FILE)
                        st.rerun()
                else:
                    # Others just see locked
                    st.button(f"{t}\n🔒 {b_name[:6]}", key=key, disabled=True)
            else:
                # Free slot
                if st.button(f"{t}\n🟢 Free", key=key):
                    new_b = pd.DataFrame([{"User": st.session_state.user, "Name": st.session_state.name, 
                                           "Date": sel_date, "Table": t_name, "Time": t}])
                    save_data(pd.concat([bookings, new_b]), BOOKINGS_FILE)
                    st.rerun()

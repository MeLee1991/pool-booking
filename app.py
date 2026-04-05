import os
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

# 1. PAGE CONFIG & MOBILE-FIRST SETTINGS
st.set_page_config(page_title="Pool Booking", layout="wide", initial_sidebar_state="collapsed")

# 2. DATABASE HELPERS (Forcing String Type for Login Stability)
USERS_FILE = "users.csv"
BOOKINGS_FILE = "bookings.csv"

def load_data(file, columns):
    if os.path.exists(file):
        return pd.read_csv(file, dtype=str) # CRITICAL: dtype=str fixes the login bug
    return pd.DataFrame(columns=columns)

def save_data(df, file):
    df.to_csv(file, index=False)

# Load data at startup
users = load_data(USERS_FILE, ["Email", "Name", "Password", "Role"])
bookings = load_data(BOOKINGS_FILE, ["User", "Name", "Date", "Table", "Time"])

# 3. SESSION STATE
if "user" not in st.session_state: st.session_state.user = None
if "role" not in st.session_state: st.session_state.role = None
if "name" not in st.session_state: st.session_state.name = None
if "tables" not in st.session_state: st.session_state.tables = ["Table 1", "Table 2", "Table 3"]

# 4. THE "NO-STACK" CSS
st.markdown("""
<style>
/* FORCE 3 COLUMNS SIDE-BY-SIDE ON ALL SCREENS */
[data-testid="stHorizontalBlock"] {
    display: flex !important;
    flex-wrap: nowrap !important; 
    gap: 2px !important;
}
[data-testid="column"] {
    flex: 1 1 33.33% !important;
    min-width: 0 !important;
}

/* BUTTON "SLOTS" - 2 ROWS OF TEXT */
.stButton > button {
    width: 100% !important;
    height: 46px !important;
    font-size: 10px !important;
    padding: 0px !important;
    line-height: 1.1 !important;
    white-space: pre-wrap !important;
    border: 1px solid #ddd !important;
    border-radius: 4px !important;
    margin-bottom: -12px !important;
}

/* COLORS */
div.stButton > button:not(:disabled) { background-color: #e8f5e9 !important; color: #1b5e20 !important; } /* Green */
div.stButton > button:disabled { background-color: #ffebee !important; color: #b71c1c !important; opacity: 1 !important; } /* Red */

.header-box {
    background: #000; color: #fff; text-align: center; font-weight: bold;
    font-size: 11px; padding: 5px 0; border-radius: 4px; margin-bottom: 20px;
}
</style>
""", unsafe_allow_html=True)

# 5. LOGIN / REGISTRATION FLOW
if st.session_state.user is None:
    st.title("🎱 RESERVE TABLE")
    tab1, tab2 = st.tabs(["Login", "Register"])
    
    with tab1:
        e_in = st.text_input("Email", key="l_e").strip().lower()
        p_in = st.text_input("Password", type="password", key="l_p").strip()
        if st.button("Log In", use_container_width=True):
            # Strict string comparison to avoid data type mismatch
            match = users[(users["Email"] == e_in) & (users["Password"] == p_in)]
            if not match.empty:
                st.session_state.user = match.iloc[0]["Email"]
                st.session_state.name = match.iloc[0]["Name"]
                st.session_state.role = match.iloc[0]["Role"]
                st.rerun()
            else: st.error("Login failed. Check your email/password.")

    with tab2:
        reg_e = st.text_input("Email", key="r_e").strip().lower()
        reg_n = st.text_input("Name", key="r_n").strip()
        reg_p = st.text_input("Password", type="password", key="r_p").strip()
        if st.button("Create Account", use_container_width=True):
            if reg_e and reg_p:
                if not users[users["Email"] == reg_e].empty:
                    st.error("User already exists!")
                else:
                    new_role = "admin" if users.empty else "user"
                    new_u = pd.DataFrame([[reg_e, reg_n, reg_p, new_role]], columns=users.columns)
                    save_data(pd.concat([users, new_u]), USERS_FILE)
                    st.success("Success! Now go to Login.")
    st.stop()

# 6. MAIN BOOKING INTERFACE
st.sidebar.write(f"Logged in: **{st.session_state.name}** ({st.session_state.role})")
if st.sidebar.button("Logout"):
    st.session_state.user = None
    st.rerun()

# Admin table renaming
if st.session_state.role == "admin":
    with st.sidebar.expander("Rename Tables"):
        for i in range(3):
            st.session_state.tables[i] = st.text_input(f"Table {i+1}", st.session_state.tables[i])

st.title("RESERVE TABLE")

# Professional Date Selectbox (Best for mobile stability)
today = datetime.now().date()
d_range = [today + timedelta(days=i) for i in range(14)]
d_labels = [d.strftime("%A, %d %b") for d in d_range]
sel_label = st.selectbox("📅 Choose Day", d_labels)
sel_date = str(d_range[d_labels.index(sel_label)])

# Table Headers
h_cols = st.columns(3)
for i in range(3):
    h_cols[i].markdown(f"<div class='header-box'>{st.session_state.tables[i]}</div>", unsafe_allow_html=True)

# Generate Grid
HOURS = [f"{h:02d}:{m}" for h in (list(range(8,24)) + list(range(0,3))) for m in ["00","30"]]

for t in HOURS:
    t_cols = st.columns(3)
    for i in range(3):
        t_name = st.session_state.tables[i]
        match = bookings[(bookings["Table"] == t_name) & (bookings["Time"] == t) & (bookings["Date"] == sel_date)]
        key = f"{i}_{t}_{sel_date}"
        
        with t_cols[i]:
            if not match.empty:
                b_user = match.iloc[0]["User"]
                b_name = match.iloc[0]["Name"]
                
                # PERMISSION LOGIC: Can I edit this?
                if b_user == st.session_state.user or st.session_state.role == "admin":
                    # It's mine OR I'm admin -> RED BUTTON WITH ❌ (Clickable to release)
                    if st.button(f"{t}\n❌ {b_name[:6]}", key=key):
                        bookings = bookings.drop(match.index)
                        save_data(bookings, BOOKINGS_FILE)
                        st.rerun()
                else:
                    # Locked for regular users
                    st.button(f"{t}\n🔒 {b_name[:6]}", key=key, disabled=True)
            else:
                # FREE SLOT -> GREEN BUTTON
                if st.button(f"{t}\n🟢 Free", key=key):
                    new_b = pd.DataFrame([[st.session_state.user, st.session_state.name, sel_date, t_name, t]], columns=bookings.columns)
                    save_data(pd.concat([bookings, new_b]), BOOKINGS_FILE)
                    st.rerun()

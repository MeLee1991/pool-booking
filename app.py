import os
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

# 1. PAGE CONFIG (Force Wide and hide Sidebar by default)
st.set_page_config(page_title="Pool Booking", layout="wide", initial_sidebar_state="collapsed")

# 2. DATABASE HELPERS (Forcing String to fix login bugs)
USERS_FILE = "users.csv"
BOOKINGS_FILE = "bookings.csv"

def load_data(file, columns):
    if os.path.exists(file):
        return pd.read_csv(file, dtype=str)
    return pd.DataFrame(columns=columns)

def save_data(df, file):
    df.to_csv(file, index=False)

# Load data
users = load_data(USERS_FILE, ["Email", "Name", "Password", "Role"])
bookings = load_data(BOOKINGS_FILE, ["User", "Name", "Date", "Table", "Time"])

# 3. SESSION STATE
if "user" not in st.session_state: st.session_state.user = None
if "role" not in st.session_state: st.session_state.role = None
if "name" not in st.session_state: st.session_state.name = None
if "tables" not in st.session_state: st.session_state.tables = ["Table 1", "Table 2", "Table 3"]

# 4. CSS (STRICT 3-COLUMN FIX + PROFESSIONAL BUTTONS)
st.markdown("""
<style>
/* REMOVE ALL PADDING TO FIT 3 COLUMNS ON MOBILE */
[data-testid="stHorizontalBlock"] {
    display: flex !important;
    flex-wrap: nowrap !important;
    gap: 2px !important;
}
[data-testid="column"] {
    flex: 1 1 33.33% !important;
    min-width: 0 !important;
    padding: 0px !important;
}

/* BUTTONS: TWO-ROW LAYOUT */
.stButton > button {
    width: 100% !important;
    height: 46px !important;
    font-size: 10px !important;
    padding: 0px !important;
    line-height: 1.1 !important;
    white-space: pre-wrap !important;
    border-radius: 6px !important;
    border: 1px solid #ddd !important;
    margin-bottom: -14px !important;
}

/* COLORS */
div.stButton > button:not(:disabled) { background-color: #f0fff4 !important; color: #22543d !important; border-color: #c6f6d5 !important; }
div.stButton > button:disabled { background-color: #fff5f5 !important; color: #c53030 !important; border-color: #fed7d7 !important; opacity: 1 !important; }

/* HEADERS */
.header-box {
    background: #1a202c; color: white; text-align: center; font-weight: bold;
    font-size: 11px; padding: 6px 0; border-radius: 4px; margin-bottom: 20px;
}
</style>
""", unsafe_allow_html=True)

# 5. LOGIN / REGISTER UI
if st.session_state.user is None:
    st.title("🎱 RESERVE TABLE")
    tab1, tab2 = st.tabs(["Login", "Register"])
    
    with tab1:
        e_in = st.text_input("Email", key="l_e").strip().lower()
        p_in = st.text_input("Password", type="password", key="l_p").strip()
        if st.button("Log In", use_container_width=True):
            match = users[(users["Email"] == e_in) & (users["Password"] == p_in)]
            if not match.empty:
                st.session_state.user = match.iloc[0]["Email"]
                st.session_state.name = match.iloc[0]["Name"]
                st.session_state.role = match.iloc[0]["Role"]
                st.rerun()
            else: st.error("Invalid credentials.")

    with tab2:
        reg_e = st.text_input("Email", key="r_e").strip().lower()
        reg_n = st.text_input("Name", key="r_n").strip()
        reg_p = st.text_input("Password", type="password", key="r_p").strip()
        if st.button("Register", use_container_width=True):
            if reg_e and reg_p:
                if not users[users["Email"] == reg_e].empty: st.error("Exists!")
                else:
                    role = "admin" if users.empty else "user"
                    new_u = pd.DataFrame([{"Email": reg_e, "Name": reg_n, "Password": reg_p, "Role": role}])
                    save_data(pd.concat([users, new_u]), USERS_FILE)
                    st.success("Registered! Login now.")
    st.stop()

# 6. MAIN INTERFACE
st.sidebar.write(f"User: **{st.session_state.name}**")
if st.sidebar.button("Log Out"):
    st.session_state.user = None
    st.rerun()

# Admin Tools
if st.session_state.role == "admin":
    with st.sidebar.expander("⚙️ Admin Settings"):
        for i in range(3):
            st.session_state.tables[i] = st.text_input(f"Name {i+1}", st.session_state.tables[i])

st.title("RESERVE TABLE")

# Date Picker (Selectbox is best for mobile spacing)
today = datetime.now().date()
d_range = [today + timedelta(days=i) for i in range(14)]
d_labels = [d.strftime("%a, %d %b") for d in d_range]
sel_label = st.selectbox("📅 Select Date", d_labels)
sel_date = str(d_range[d_labels.index(sel_label)])

# Table Headers
h_cols = st.columns(3)
for i in range(3):
    h_cols[i].markdown(f"<div class='header-box'>{st.session_state.tables[i]}</div>", unsafe_allow_html=True)

# THE GRID
HOURS = [f"{h:02d}:{m}" for h in (list(range(8,24)) + list(range(0,3))) for m in ["00","30"]]

for t in HOURS:
    t_cols = st.columns(3)
    for i in range(3):
        t_name = st.session_state.tables[i]
        match = bookings[(bookings["Table"] == t_name) & (bookings["Time"] == t) & (bookings["Date"] == sel_date)]
        key = f"b_{i}_{t}_{sel_date}"
        
        with t_cols[i]:
            if not match.empty:
                b_user = match.iloc[0]["User"]
                b_name = match.iloc[0]["Name"]
                
                # PERMISSIONS LOGIC
                if b_user == st.session_state.user or st.session_state.role == "admin":
                    # My booking OR I am Admin: Click to release
                    if st.button(f"{t}\n❌ {b_name[:6]}", key=key):
                        bookings = bookings.drop(match.index)
                        save_data(bookings, BOOKINGS_FILE)
                        st.rerun()
                else:
                    # Someone else's booking: Locked for users
                    st.button(f"{t}\n🔒 {b_name[:6]}", key=key, disabled=True)
            else:
                # FREE SLOT
                if st.button(f"{t}\n🟢 Free", key=key):
                    new_entry = pd.DataFrame([{
                        "User": st.session_state.user, 
                        "Name": st.session_state.name, 
                        "Date": sel_date, 
                        "Table": t_name, 
                        "Time": t
                    }])
                    save_data(pd.concat([bookings, new_entry]), BOOKINGS_FILE)
                    st.rerun()

import os
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

# 1. MOBILE OPTIMIZATION
st.set_page_config(page_title="Pool Booking", layout="centered", initial_sidebar_state="collapsed")

# 2. DATABASE
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

# 3. SESSION
if "user" not in st.session_state: st.session_state.user = None
if "role" not in st.session_state: st.session_state.role = None
if "name" not in st.session_state: st.session_state.name = None
if "tables" not in st.session_state: st.session_state.tables = ["Table 1", "Table 2", "Table 3"]

# 4. CSS: GIANT BUTTONS & TIGHT COLUMNS
st.markdown("""
<style>
/* FORCE COLUMNS TO SHRINK TO DATA WIDTH */
[data-testid="stHorizontalBlock"] {
    justify-content: center !important; /* Centers the narrow table */
    gap: 5px !important;
}
[data-testid="column"] {
    flex: 0 1 auto !important; /* Only as wide as content */
    width: 30% !important;     /* Prevents them from getting too wide */
    min-width: 90px !important; 
}

/* GIANT BUTTONS (Twice the previous size) */
.stButton > button {
    width: 100% !important;
    height: 90px !important;  /* DOUBLE HEIGHT */
    font-size: 13px !important;
    font-weight: bold !important;
    padding: 0 !important;
    margin-bottom: -10px !important;
    border-radius: 10px !important;
    border: 2px solid #eee !important;
    white-space: pre-wrap !important;
    box-shadow: 0 2px 4px rgba(0,0,0,0.05);
}

/* COLORS */
div.stButton > button:not(:disabled) { background-color: #f6ffed !important; color: #389e0d !important; border-color: #b7eb8f !important; }
div.stButton > button:disabled { background-color: #fff1f0 !important; color: #cf1322 !important; border-color: #ffa39e !important; opacity: 1 !important; }

/* FANCY DATE PICKER STYLING */
div[data-testid="stDateInput"] {
    background: #f8f9fa;
    border-radius: 10px;
    padding: 5px;
}

.header-label {
    background: #1a202c; color: white; text-align: center; 
    font-size: 12px; padding: 10px 0; border-radius: 8px; margin-bottom: 20px;
}
</style>
""", unsafe_allow_html=True)

# 5. LOGIN (Standard Logic)
if st.session_state.user is None:
    st.title("🎱 RESERVE")
    tab = st.radio("", ["Login", "Register"], horizontal=True)
    e = st.text_input("Email").strip().lower()
    p = st.text_input("Password", type="password").strip()
    if tab == "Login":
        if st.button("Log In", use_container_width=True):
            match = users[(users["Email"] == e) & (users["Password"] == p)]
            if not match.empty:
                st.session_state.user, st.session_state.name, st.session_state.role = e, match.iloc[0]["Name"], match.iloc[0]["Role"]
                st.rerun()
            else: st.error("Invalid Login")
    else:
        n = st.text_input("Name").strip()
        if st.button("Register", use_container_width=True):
            if e and p and n:
                role = "admin" if users.empty else "user"
                new_u = pd.DataFrame([{"Email":e, "Name":n, "Password":p, "Role":role}])
                save_data(pd.concat([users, new_u]), USERS_FILE)
                st.success("Registered!")
    st.stop()

# 6. APP
st.sidebar.button("Logout", on_click=lambda: st.session_state.clear())

# FANCY CALENDAR PICKER
st.markdown("### 📅 Select Date")
sel_date_obj = st.date_input(
    "Choose a day from the month view",
    value=datetime.now().date(),
    min_value=datetime.now().date()
)
sel_date = str(sel_date_obj)

# HEADERS
h_cols = st.columns(3)
for i in range(3):
    h_cols[i].markdown(f"<div class='header-label'>{st.session_state.tables[i]}</div>", unsafe_allow_html=True)

# THE GRID
HOURS = [f"{h:02d}:{m}" for h in (list(range(8, 24)) + list(range(0, 3))) for m in ["00", "30"]]

for t in HOURS:
    t_cols = st.columns(3)
    for i in range(3):
        t_name = st.session_state.tables[i]
        match = bookings[(bookings["Table"] == t_name) & (bookings["Time"] == t) & (bookings["Date"] == sel_date)]
        key = f"btn_{i}_{t}_{sel_date}"
        
        with t_cols[i]:
            if not match.empty:
                b_user, b_name = match.iloc[0]["User"], match.iloc[0]["Name"]
                # ADMIN/OWNER PERMISSIONS
                if b_user == st.session_state.user or st.session_state.role == "admin":
                    if st.button(f"{t}\n❌\n{b_name[:6]}", key=key):
                        bookings = bookings.drop(match.index)
                        save_data(bookings, BOOKINGS_FILE)
                        st.rerun()
                else:
                    st.button(f"{t}\n🔒\n{b_name[:6]}", key=key, disabled=True)
            else:
                if st.button(f"{t}\n🟢\nFree", key=key):
                    new_b = pd.DataFrame([{"User": st.session_state.user, "Name": st.session_state.name, 
                                           "Date": sel_date, "Table": t_name, "Time": t}])
                    save_data(pd.concat([bookings, new_b]), BOOKINGS_FILE)
                    st.rerun()

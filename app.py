import os
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

# 1. FORCED MOBILE LAYOUT
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
if "sel_date" not in st.session_state: st.session_state.sel_date = str(datetime.now().date())

# 4. STRICT CSS: 3-COLUMNS + BIG BUTTONS + TIGHT HEADERS
st.markdown("""
<style>
/* FORCE 3 COLUMNS SIDE-BY-SIDE */
[data-testid="stHorizontalBlock"] {
    display: flex !important;
    flex-direction: row !important;
    flex-wrap: nowrap !important;
    gap: 4px !important;
}
[data-testid="column"] {
    flex: 1 1 33% !important;
    min-width: 0 !important;
}

/* BIG CLICKABLE BUTTONS */
.stButton > button {
    width: 100% !important;
    height: 75px !important;
    font-size: 11px !important;
    font-weight: bold !important;
    padding: 2px !important;
    margin-bottom: -15px !important;
    border-radius: 8px !important;
    white-space: pre-wrap !important;
}

/* COMPACT HEADERS */
.tbl-header {
    background: #1a202c; color: white; text-align: center; 
    font-size: 11px; padding: 6px 0; border-radius: 4px; margin-bottom: 10px;
}

/* DATE STRIP BUTTONS */
.date-btn > div > button { height: 45px !important; font-size: 10px !important; }

/* COLORS */
div.stButton > button:not(:disabled) { background-color: #f6ffed !important; color: #389e0d !important; border: 1px solid #b7eb8f !important; }
div.stButton > button:disabled { background-color: #fff1f0 !important; color: #cf1322 !important; border: 1px solid #ffa39e !important; opacity: 1 !important; }
</style>
""", unsafe_allow_html=True)

# 5. AUTHENTICATION
if st.session_state.user is None:
    st.title("🎱 RESERVE")
    t1, t2 = st.tabs(["Login", "Register"])
    with t1:
        e = st.text_input("Email", key="le").lower()
        p = st.text_input("Password", type="password", key="lp")
        if st.button("Log In"):
            match = users[(users["Email"] == e) & (users["Password"] == p)]
            if not match.empty:
                st.session_state.user, st.session_state.name, st.session_state.role = e, match.iloc[0]["Name"], match.iloc[0]["Role"]
                st.rerun()
    with t2:
        re, rn, rp = st.text_input("Email", key="re"), st.text_input("Name"), st.text_input("Pass", type="password")
        if st.button("Register"):
            role = "admin" if users.empty else "user"
            save_data(pd.concat([users, pd.DataFrame([{"Email":re,"Name":rn,"Password":rp,"Role":role}])]), USERS_FILE)
            st.success("Registered!")
    st.stop()

# 6. APP MAIN
st.sidebar.button("Logout", on_click=lambda: st.session_state.clear())

# --- 2-WEEK DIRECT DATE PICKER ---
st.write("### 📅 Select Date")
date_cols = st.columns(7) # 7 days per row
for i in range(14):
    d = datetime.now().date() + timedelta(days=i)
    d_str = str(d)
    with date_cols[i % 7]:
        label = d.strftime("%a\n%d")
        # Highlight selected date
        if st.button(label, key=f"date_{d_str}", use_container_width=True, type="primary" if st.session_state.sel_date == d_str else "secondary"):
            st.session_state.sel_date = d_str
            st.rerun()

st.divider()

# --- THE 3-COLUMN GRID ---
# Table Headers
h_cols = st.columns(3)
tables = ["Table 1", "Table 2", "Table 3"]
for i in range(3):
    h_cols[i].markdown(f"<div class='tbl-header'>{tables[i]}</div>", unsafe_allow_html=True)

# Time Slots
HOURS = [f"{h:02d}:{m}" for h in (list(range(8, 24)) + list(range(0, 3))) for m in ["00", "30"]]

for t in HOURS:
    t_cols = st.columns(3)
    for i in range(3):
        t_name = tables[i]
        match = bookings[(bookings["Table"] == t_name) & (bookings["Time"] == t) & (bookings["Date"] == st.session_state.sel_date)]
        key = f"b_{i}_{t}_{st.session_state.sel_date}"
        
        with t_cols[i]:
            if not match.empty:
                b_user, b_name = match.iloc[0]["User"], match.iloc[0]["Name"]
                # Admin or Owner can delete
                if b_user == st.session_state.user or st.session_state.role == "admin":
                    if st.button(f"{t}\n❌\n{b_name[:6]}", key=key):
                        bookings = bookings.drop(match.index)
                        save_data(bookings, BOOKINGS_FILE)
                        st.rerun()
                else:
                    st.button(f"{t}\n🔒\n{b_name[:6]}", key=key, disabled=True)
            else:
                if st.button(f"{t}\n🟢\nFree", key=key):
                    new_b = pd.DataFrame([{"User":st.session_state.user, "Name":st.session_state.name, "Date":st.session_state.sel_date, "Table":t_name, "Time":t}])
                    save_data(pd.concat([bookings, new_b]), BOOKINGS_FILE)
                    st.rerun()

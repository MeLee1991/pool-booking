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

# 4. CUSTOM CSS: SHRINK WIDTH & LOCK BUTTON SIZES
st.markdown("""
<style>
/* 1. SHRINK THE ENTIRE TABLE AREA */
[data-testid="stHorizontalBlock"] {
    display: flex !important;
    flex-direction: row !important;
    flex-wrap: nowrap !important;
    justify-content: flex-start !important;
    gap: 2px !important;
    width: min-content !important; /* Forces columns to hug the buttons */
}

/* 2. FIXED COLUMN WIDTH (Shrinks the table) */
[data-testid="column"] {
    flex: 0 0 85px !important; /* Fixed width: adjust this number to go even smaller */
    min-width: 85px !important;
    max-width: 85px !important;
    padding: 0px !important;
}

/* 3. LOCKED BUTTON SIZE (Same for Free or Booked) */
.stButton > button {
    width: 85px !important;
    height: 70px !important; /* Tall enough for 3 lines, but uniform */
    font-size: 10px !important;
    font-weight: bold !important;
    padding: 0px !important;
    margin-bottom: -12px !important;
    border-radius: 6px !important;
    white-space: pre-wrap !important;
    display: block !important;
}

/* 4. HEADERS */
.tbl-header {
    background: #000; color: #fff; text-align: center; 
    font-size: 10px; padding: 4px 0; border-radius: 4px; margin-bottom: 10px;
    width: 85px !important;
}

/* 5. COLORS */
/* Free */
div.stButton > button:not(:disabled) { background-color: #f6ffed !important; color: #389e0d !important; border: 1px solid #b7eb8f !important; }
/* Booked */
div.stButton > button:disabled { background-color: #fff1f0 !important; color: #cf1322 !important; border: 1px solid #ffa39e !important; opacity: 1 !important; }

/* DATE STRIP STYLING */
.date-row [data-testid="column"] {
    flex: 0 0 45px !important;
    min-width: 45px !important;
}
.date-row button {
    height: 40px !important;
    width: 45px !important;
    font-size: 9px !important;
}
</style>
""", unsafe_allow_html=True)

# 5. AUTH FLOW (Standard Logic)
if st.session_state.user is None:
    st.title("🎱 LOGIN")
    t1, t2 = st.tabs(["Login", "Register"])
    with t1:
        e = st.text_input("Email", key="le").lower()
        p = st.text_input("Password", type="password", key="lp")
        if st.button("Log In"):
            m = users[(users["Email"] == e) & (users["Password"] == p)]
            if not m.empty:
                st.session_state.user, st.session_state.name, st.session_state.role = e, m.iloc[0]["Name"], m.iloc[0]["Role"]
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

# --- SMALLER DATE PICKER (2 WEEKS) ---
st.write("### 📅 Select Date")
today_str = str(datetime.now().date())

# Row 1 (Week 1)
d_cols1 = st.columns(7)
# Row 2 (Week 2)
d_cols2 = st.columns(7)

for i in range(14):
    d = datetime.now().date() + timedelta(days=i)
    d_str = str(d)
    target_cols = d_cols1 if i < 7 else d_cols2
    with target_cols[i % 7]:
        label = d.strftime("%a\n%d")
        
        # Determine Color Logic
        is_sel = st.session_state.sel_date == d_str
        is_today = d_str == today_str
        
        # Primary for selected, Today has special text in this version
        btn_type = "primary" if is_sel else "secondary"
        btn_label = f"⭐\n{label}" if is_today else label
        
        if st.button(btn_label, key=f"d_{d_str}", use_container_width=True, type=btn_type):
            st.session_state.sel_date = d_str
            st.rerun()

st.divider()

# --- THE NARROW 3-COLUMN GRID ---
h_cols = st.columns(3)
tables = ["Table 1", "Table 2", "Table 3"]
for i in range(3):
    h_cols[i].markdown(f"<div class='tbl-header'>{tables[i]}</div>", unsafe_allow_html=True)

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
                    # LOCKED SIZE: 3 lines of text to match "Free" button height
                    if st.button(f"{t}\n❌\n{b_name[:6]}", key=key):
                        bookings = bookings.drop(match.index)
                        save_data(bookings, BOOKINGS_FILE)
                        st.rerun()
                else:
                    st.button(f"{t}\n🔒\n{b_name[:6]}", key=key, disabled=True)
            else:
                # LOCKED SIZE: 3 lines of text to match "Booked" button height
                if st.button(f"{t}\n🟢\nFree", key=key):
                    new_b = pd.DataFrame([{"User":st.session_state.user, "Name":st.session_state.name, "Date":st.session_state.sel_date, "Table":t_name, "Time":t}])
                    save_data(pd.concat([bookings, new_b]), BOOKINGS_FILE)
                    st.rerun()

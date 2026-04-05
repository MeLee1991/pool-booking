import os
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

# 1. SETUP
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
if "confirm_delete" not in st.session_state: st.session_state.confirm_delete = None

# 4. CUSTOM CSS: THE "TIGHT FIT" FIX
st.markdown("""
<style>
/* 1. FORCE THE 3 TABLE COLUMNS TO BE TIGHTLY PACKED */
[data-testid="column"] {
    flex: 0 0 105px !important; /* Fixed width to keep them close */
    min-width: 105px !important;
    max-width: 105px !important;
    padding: 1px !important;
}

/* 2. CENTER THE WHOLE GRID AREA */
[data-testid="stHorizontalBlock"] {
    justify-content: center !important;
    gap: 2px !important;
}

/* 3. BUTTON STYLING (Clock | Symbol | Name) */
.stButton > button {
    width: 105px !important;
    height: 50px !important;
    padding: 0px 4px !important;
    margin-bottom: -15px !important;
    border-radius: 4px !important;
    display: flex !important;
    align-items: center !important;
    justify-content: space-between !important;
    white-space: nowrap !important;
    overflow: hidden !important;
}

/* FONT LOGIC: Hour vs Name */
.btn-text-hour { font-size: 13px !important; font-weight: bold; }
.btn-text-name { font-size: 11px !important; opacity: 0.9; } /* 2px smaller than hour */
.btn-symbol { font-size: 14px !important; }

/* 4. HEADERS */
.tbl-header {
    background: #000; color: #fff; text-align: center; 
    font-size: 11px; padding: 4px 0; border-radius: 4px; margin-bottom: 10px;
    width: 105px;
}

/* 5. INDEPENDENT DATE GRID (7 columns) */
.date-section [data-testid="column"] {
    flex: 0 0 44px !important;
    min-width: 44px !important;
}
.date-section button {
    height: 42px !important;
    width: 44px !important;
    font-size: 10px !important;
}

/* COLORS */
div.stButton > button:not(:disabled) { background-color: #f6ffed !important; color: #389e0d !important; border: 1px solid #b7eb8f !important; }
div.stButton > button:disabled { background-color: #fff1f0 !important; color: #cf1322 !important; border: 1px solid #ffa39e !important; opacity: 1 !important; }
</style>
""", unsafe_allow_html=True)

# 5. AUTH / LOGIN (Standard logic from your previous steps)
if st.session_state.user is None:
    st.title("🎱 RESERVE")
    auth = st.radio("", ["Login", "Register"], horizontal=True)
    e = st.text_input("Email").lower().strip()
    p = st.text_input("Pass", type="password")
    if auth == "Login":
        if st.button("Go"):
            m = users[(users["Email"] == e) & (users["Password"] == p)]
            if not m.empty:
                st.session_state.user, st.session_state.name, st.session_state.role = e, m.iloc[0]["Name"], m.iloc[0]["Role"]
                st.rerun()
    else:
        n = st.text_input("Name")
        if st.button("Register"):
            role = "admin" if users.empty else "user"
            save_data(pd.concat([users, pd.DataFrame([{"Email":e,"Name":n,"Password":p,"Role":role}])]), USERS_FILE)
            st.rerun()
    st.stop()

# 6. ADMIN CONFIRMATION DIALOGUE
if st.session_state.confirm_delete:
    idx, b_name = st.session_state.confirm_delete
    st.warning(f"⚠️ Cancel {b_name}?")
    c1, c2 = st.columns(2)
    if c1.button("Confirm Cancel"):
        bookings = bookings.drop(idx)
        save_data(bookings, BOOKINGS_FILE)
        st.session_state.confirm_delete = None
        st.rerun()
    if c2.button("Keep"):
        st.session_state.confirm_delete = None
        st.rerun()
    st.stop()

# 7. MAIN INTERFACE
st.sidebar.button("Logout", on_click=lambda: st.session_state.clear())

# DATE PICKER GRID (Independent 7-column grid)
st.write("### 📅 Dates")
today_str = str(datetime.now().date())
with st.container():
    for row_idx in range(2):
        d_cols = st.columns(7)
        for i in range(7):
            d = datetime.now().date() + timedelta(days=i + (row_idx * 7))
            d_str = str(d)
            with d_cols[i]:
                # Custom label for Today
                lbl = d.strftime("%a\n%d")
                if d_str == today_str: lbl = f"⭐\n{d.strftime('%d')}"
                if st.button(lbl, key=f"dt_{d_str}", type="primary" if st.session_state.sel_date == d_str else "secondary"):
                    st.session_state.sel_date = d_str
                    st.rerun()

st.divider()

# TABLE DATA GRID (Closer Columns)
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
        key = f"slot_{i}_{t}_{st.session_state.sel_date}"
        
        with t_cols[i]:
            if not match.empty:
                b_user, b_name = match.iloc[0]["User"], match.iloc[0]["Name"]
                # HTML injection inside button label

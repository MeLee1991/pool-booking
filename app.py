import os
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

# 1. PAGE SETUP
st.set_page_config(page_title="Pool Booking", layout="wide", initial_sidebar_state="collapsed")

# 2. DATA PERSISTENCE
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

# 4. HARDCORE CSS FOR 3-COLUMN MOBILE GRID
st.markdown("""
<style>
/* FORCE 3 COLUMNS TO STAY SIDE-BY-SIDE ON ALL SCREENS */
div[data-testid="stHorizontalBlock"] {
    display: grid !important;
    grid-template-columns: repeat(3, 1fr) !important;
    gap: 2px !important;
    width: 100% !important;
}

/* LOCK COLUMN WIDTH */
div[data-testid="column"] {
    width: 100% !important;
    min-width: 0px !important;
}

/* BUTTON STYLING: CLOCK | ICON | NAME */
.stButton > button {
    width: 100% !important;
    height: 48px !important;
    padding: 2px 5px !important;
    margin-bottom: -12px !important;
    border-radius: 4px !important;
    display: flex !important;
    justify-content: space-between !important;
    align-items: center !important;
}

/* FONT SIZES */
.stButton button p {
    display: flex !important;
    width: 100% !important;
    justify-content: space-between !important;
    align-items: center !important;
}

/* COLORS */
div.stButton > button:not(:disabled) { background-color: #f6ffed !important; color: #389e0d !important; border: 1px solid #b7eb8f !important; }
div.stButton > button:disabled { background-color: #fff1f0 !important; color: #cf1322 !important; border: 1px solid #ffa39e !important; opacity: 1 !important; }

/* TABLE HEADERS */
.header-box {
    background: #000; color: #fff; text-align: center;
    font-size: 10px; padding: 5px 0; border-radius: 4px;
}
</style>
""", unsafe_allow_html=True)

# 5. AUTHENTICATION
if st.session_state.user is None:
    st.title("🎱 RESERVE")
    tab = st.radio("", ["Login", "Register"], horizontal=True)
    e = st.text_input("Email").lower().strip()
    p = st.text_input("Pass", type="password")
    if tab == "Login":
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

# 6. ADMIN CANCELLATION DIALOGUE
if st.session_state.pending_cancel:
    idx, b_name = st.session_state.pending_cancel
    st.error(f"⚠️ Cancel {b_name}'s booking?")
    c1, c2 = st.columns(2)
    if c1.button("Confirm Cancellation"):
        bookings = bookings.drop(idx)
        save_data(bookings, BOOKINGS_FILE)
        st.session_state.pending_cancel = None
        st.rerun()
    if c2.button("Keep Booking"):
        st.session_state.pending_cancel = None
        st.rerun()
    st.stop()

# 7. MAIN INTERFACE
st.sidebar.button("Logout", on_click=lambda: st.session_state.clear())

# COMPACT DATE PICKER (2x7 GRID)
st.write("### 📅 Dates")
today_str = str(datetime.now().date())
for row in range(2):
    d_cols = st.columns(7)
    for i in range(7):
        d = datetime.now().date() + timedelta(days=i + (row * 7))
        d_str = str(d)
        with d_cols[i]:
            lbl = d.strftime("%a\n%d")
            if d_str == today_str: lbl = f"⭐\n{d.strftime('%d')}"
            if st.button(lbl, key=f"d_{d_str}", type="primary" if st.session_state.sel_date == d_str else "secondary"):
                st.session_state.sel_date = d_str
                st.rerun()

st.divider()

# TABLE HEADERS
h_cols = st.columns(3)
t_names = ["Table 1", "Table 2", "Table 3"]
for i in range(3):
    h_cols[i].markdown(f"<div class='header-box'>{t_names[i]}</div>", unsafe_allow_html=True)

# TIME SLOTS
HOURS = [f"{h:02d}:{m}" for h in (list(range(8, 24)) + list(range(0, 3))) for m in ["00", "30"]]

for t in HOURS:
    t_cols = st.columns(3)
    for i in range(3):
        t_name = t_names[i]
        match = bookings[(bookings["Table"] == t_name) & (bookings["Time"] == t) & (bookings["Date"] == st.session_state.sel_date)]
        key = f"slot_{i}_{t}_{st.session_state.sel_date}"
        
        with t_cols[i]:
            if not match.empty:
                b_user, b_name = match.iloc[0]["User"], match.iloc[0]["Name"]
                # Display: Hour | Icon | Small Name
                label = f"{t} ❌ {b_name[:5]}"
                
                if st.session_state.role == "admin" or b_user == st.session_state.user:
                    if st.button(label, key=key):
                        st.session_state.pending_cancel = (match.index, b_name)
                        st.rerun()
                else:
                    st.button(f"{t} 🔒 {b_name[:5]}", key=key, disabled=True)
            else:
                if st.button(f"{t} 🟢 Free", key=key):
                    new_b = pd.DataFrame([{"User":st.session_state.user, "Name":st.session_state.name, "Date":st.session_state.sel_date, "Table":t_name, "Time":t}])
                    save_data(pd.concat([bookings, new_b]), BOOKINGS_FILE)
                    st.rerun()

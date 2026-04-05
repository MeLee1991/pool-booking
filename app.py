import os
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

st.set_page_config(page_title="Pool Booking", layout="wide")

# =========================
# 1. DATABASE SETUP
# =========================
USERS_FILE = "users.csv"
BOOKINGS_FILE = "bookings.csv"

def load_data(file, columns):
    if os.path.exists(file): return pd.read_csv(file)
    return pd.DataFrame(columns=columns)

def save_data(df, file):
    df.to_csv(file, index=False)

# =========================
# 2. SESSION STATE
# =========================
if "user" not in st.session_state: st.session_state.user = None
if "role" not in st.session_state: st.session_state.role = None
if "table_names" not in st.session_state: st.session_state.table_names = ["Table 1", "Table 2", "Table 3"]

# =========================
# 3. CSS (PROFESSIONAL FIX)
# =========================
st.markdown("""
<style>
/* FORCE 3 COLUMNS WITHOUT OVERFLOW */
[data-testid="stHorizontalBlock"] {
    display: flex !important;
    flex-direction: row !important;
    flex-wrap: nowrap !important;
    justify-content: center !important;
    width: 100% !important;
    gap: 4px !important;
}

[data-testid="column"] {
    flex: 1 1 30% !important;
    min-width: 0px !important;
    max-width: 110px !important;
}

/* SLOTS: 2-ROW DESIGN */
.stButton button {
    width: 100% !important;
    height: 44px !important;
    font-size: 10px !important;
    border-radius: 6px !important;
    border: 1px solid #e0e0e0 !important;
    white-space: pre-wrap !important;
    line-height: 1.2 !important;
    margin-bottom: -12px !important;
}

/* BOOKED SLOT (LIGHT RED) */
div.stButton > button:disabled {
    background-color: #ffebee !important;
    color: #c62828 !important;
    border-color: #ffcdd2 !important;
    opacity: 1 !important;
}

/* AVAILABLE SLOT (LIGHT GREEN) */
div.stButton > button:not(:disabled) {
    background-color: #e8f5e9 !important;
    color: #2e7d32 !important;
    border-color: #c8e6c9 !important;
}

/* HORIZONTAL DATE PILLS */
div[data-testid="stExpander"] { border: none !important; }
.date-container {
    display: flex;
    overflow-x: auto;
    gap: 10px;
    padding: 10px 0;
}

.table-header {
    text-align: center;
    font-weight: bold;
    font-size: 10px;
    background: black;
    color: white;
    padding: 6px 0;
    border-radius: 4px;
    margin-bottom: 25px;
}
</style>
""", unsafe_allow_html=True)

# =========================
# 4. LOGIN LOGIC (FIRST)
# =========================
users = load_data(USERS_FILE, ["Email","Name","Password","Role"])

if st.session_state.user is None:
    st.title("RESERVE TABLE")
    with st.container():
        st.subheader("Login / Register")
        email = st.text_input("Email").lower()
        password = st.text_input("Password", type="password")
        col1, col2 = st.columns(2)
        
        if col1.button("Login", use_container_width=True):
            u = users[(users["Email"]==email) & (users["Password"]==password)]
            if not u.empty:
                st.session_state.user = email
                st.session_state.name = u.iloc[0]["Name"]
                st.session_state.role = u.iloc[0]["Role"]
                st.rerun()
            else: st.error("Invalid credentials")
            
        if col2.button("Register", use_container_width=True):
            if email and password:
                role = "admin" if users.empty else "pending"
                new_u = pd.DataFrame([[email, "Guest", password, role]], columns=users.columns)
                save_data(pd.concat([users, new_u]), USERS_FILE)
                st.success("Registered! Now Login.")
    st.stop()

# =========================
# 5. MAIN CONTENT (AFTER LOGIN)
# =========================
bookings = load_data(BOOKINGS_FILE, ["User","Name","Date","Table","Time"])

# Sidebar for Stats/Admin
st.sidebar.title(f"Hi, {st.session_state.name}")
if st.sidebar.button("Logout"):
    st.session_state.user = None
    st.rerun()

if st.session_state.role == "admin":
    view = st.sidebar.selectbox("Navigate", ["Grid", "Users", "Stats"])
    if view == "Users":
        st.title("User Admin")
        save_data(st.data_editor(users), USERS_FILE)
        st.stop()
    if view == "Stats":
        st.title("Stats")
        st.bar_chart(bookings["Table"].value_counts())
        st.stop()

# Grid View
st.title("RESERVE TABLE")

# Professional Date Picker (Selectbox used for mobile stability)
today = datetime.now().date()
date_options = [(today + timedelta(days=i)) for i in range(14)]
date_labels = [d.strftime("%a %d %b") for d in date_options]
selected_date_label = st.selectbox("Select Date", date_labels)
sel_date = str(date_options[date_labels.index(selected_date_label)])

# Table Headers
h_cols = st.columns(3)
for i, col in enumerate(h_cols):
    col.markdown(f"<div class='table-header'>{st.session_state.table_names[i]}</div>", unsafe_allow_html=True)

# Grid
HOURS = [f"{h:02d}:{m}" for h in (list(range(8,24)) + list(range(0,3))) for m in ["00","30"]]
for t in HOURS:
    t_cols = st.columns(3)
    for i, col in enumerate(t_cols):
        t_name = st.session_state.table_names[i]
        match = bookings[(bookings["Table"] == t_name) & (bookings["Time"] == t) & (bookings["Date"] == sel_date)]
        key = f"s_{i}_{t}_{sel_date}"
        
        if not match.empty:
            name = match.iloc[0]["Name"]
            col.button(f"{t}\n{name[:7]}", key=key, disabled=True)
        else:
            if col.button(f"{t}\n🟢", key=key):
                new_b = pd.DataFrame([[st.session_state.user, st.session_state.name, sel_date, t_name, t]], columns=bookings.columns)
                save_data(pd.concat([bookings, new_b]), BOOKINGS_FILE)
                st.rerun()

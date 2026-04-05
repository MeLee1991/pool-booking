import os
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

st.set_page_config(page_title="Pool Booking", layout="wide")

# =========================
# 1. DATABASE FUNCTIONS
# =========================
USERS_FILE = "users.csv"
BOOKINGS_FILE = "bookings.csv"

def load_data(file, columns):
    if os.path.exists(file):
        return pd.read_csv(file)
    return pd.DataFrame(columns=columns)

def save_data(df, file):
    df.to_csv(file, index=False)

# =========================
# 2. SESSION INITIALIZATION
# =========================
if "user" not in st.session_state:
    st.session_state.user = None
if "role" not in st.session_state:
    st.session_state.role = None
if "table_names" not in st.session_state:
    st.session_state.table_names = ["Table 1", "Table 2", "Table 3"]

# =========================
# 3. CSS (PRO PILL DATES & NARROW GRID)
# =========================
st.markdown("""
<style>
/* PROFESSIONAL DATE PILLS */
[data-testid="stRadio"] > div {
    display: flex !important;
    overflow-x: auto !important;
    white-space: nowrap !important;
    gap: 10px !important;
    padding: 5px !important;
}
[data-testid="stRadio"] label {
    background-color: #f0f2f6;
    padding: 5px 15px !important;
    border-radius: 20px !important;
    border: 1px solid #ddd !important;
    font-size: 11px !important;
    cursor: pointer;
}
[data-testid="stRadio"] div[data-baseweb="radio"] div:first-child { display: none; }

/* STRICT 3-COLUMN NARROW GRID */
[data-testid="stHorizontalBlock"] {
    display: grid !important;
    grid-template-columns: repeat(3, 85px) !important;
    justify-content: center !important;
    gap: 4px !important;
}

[data-testid="column"] {
    width: 85px !important;
    flex: none !important;
}

/* BUTTON SLOTS (2 ROWS) */
.stButton button {
    width: 82px !important; 
    height: 42px !important;
    font-size: 10px !important;
    border: 1px solid #bbbbbb !important;
    white-space: pre-wrap !important;
    margin-bottom: -15px !important;
    border-radius: 4px !important;
}

/* COLORS */
div.stButton > button:not(:disabled) { background-color: #f0fdf4 !important; color: #166534 !important; border-color: #bef264 !important; }
div.stButton > button:disabled { background-color: #fff1f2 !important; color: #be123c !important; border-color: #fecaca !important; opacity: 1 !important; }

/* HEADER */
.table-header {
    text-align: center;
    font-weight: bold;
    font-size: 10px;
    background: #000;
    color: #fff;
    padding: 5px 0;
    margin-bottom: 30px;
    border-radius: 4px;
}
</style>
""", unsafe_allow_html=True)

# =========================
# 4. LOGIN / SIDEBAR
# =========================
users = load_data(USERS_FILE, ["Email","Name","Password","Role"])

st.sidebar.title("🔐 Access")
if st.session_state.user is None:
    mode = st.sidebar.radio("Mode", ["Login","Register"])
    email = st.sidebar.text_input("Email").strip().lower()
    pw = st.sidebar.text_input("Password", type="password")
    
    if mode == "Register":
        reg_name = st.sidebar.text_input("Name")
        if st.sidebar.button("Go"):
            role = "admin" if users.empty else "pending"
            new_u = pd.DataFrame([[email, reg_name, pw, role]], columns=["Email","Name","Password","Role"])
            save_data(pd.concat([users, new_u]), USERS_FILE)
            st.sidebar.success("Registered! Please Login.")
    else:
        if st.sidebar.button("Go"):
            u = users[(users["Email"]==email) & (users["Password"]==pw)]
            if not u.empty:
                st.session_state.user = email
                st.session_state.name = u.iloc[0]["Name"]
                st.session_state.role = u.iloc[0]["Role"]
                st.rerun()
            else:
                st.sidebar.error("Invalid Login")
    st.stop()

# =========================
# 5. ADMIN SECTION
# =========================
bookings = load_data(BOOKINGS_FILE, ["User","Name","Date","Table","Time"])

if st.session_state.role == "admin":
    admin_action = st.sidebar.selectbox("Admin Menu", ["Booking Grid", "Users", "Stats"])
    if admin_action == "Users":
        st.title("User Management")
        edited = st.data_editor(users)
        if st.button("Update Users"):
            save_data(edited, USERS_FILE)
        st.stop()
    elif admin_action == "Stats":
        st.title("Booking Stats")
        st.bar_chart(bookings["Table"].value_counts())
        st.stop()

# =========================
# 6. MAIN BOOKING GRID
# =========================
st.title("RESERVE TABLE")

# Professional Date Picker
today = datetime.now().date()
dates = [today + timedelta(days=i) for i in range(14)]
labels = [d.strftime("%a %d") for d in dates]
selected_label = st.radio("", labels, horizontal=True)
sel_date = str(dates[labels.index(selected_label)])

# Rename Tables (Admin only)
if st.session_state.role == "admin":
    with st.expander("⚙️ Rename Tables"):
        for i in range(3):
            st.session_state.table_names[i] = st.text_input(f"Name {i+1}", st.session_state.table_names[i])

# Headers
h_cols = st.columns(3)
for i, col in enumerate(h_cols):
    col.markdown(f"<div class='table-header'>{st.session_state.table_names[i]}</div>", unsafe_allow_html=True)

# Time Slots
HOURS = [f"{h:02d}:{m}" for h in (list(range(8,24)) + list(range(0,3))) for m in ["00","30"]]

for t in HOURS:
    t_cols = st.columns(3)
    for i, col in enumerate(t_cols):
        t_name = st.session_state.table_names[i]
        match = bookings[(bookings["Table"] == t_name) & (bookings["Time"] == t) & (bookings["Date"] == sel_date)]
        
        if not match.empty:
            u_name = match.iloc[0]["Name"]
            col.button(f"{t}\n{u_name[:7]}", key=f"slot_{i}_{t}_{sel_date}", disabled=True)
        else:
            if col.button(f"{t}\n🟢", key=f"slot_{i}_{t}_{sel_date}"):
                new_b = pd.DataFrame([[st.session_state.user, st.session_state.name, sel_date, t_name, t]], 
                                     columns=["User","Name","Date","Table","Time"])
                save_data(pd.concat([bookings, new_b]), BOOKINGS_FILE)
                st.rerun()

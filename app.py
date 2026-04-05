import os
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

# 1. PAGE CONFIG
st.set_page_config(page_title="Pool Booking", layout="wide", initial_sidebar_state="collapsed")

# 2. DATABASE HELPERS
USERS_FILE = "users.csv"
BOOKINGS_FILE = "bookings.csv"

def load_data(file, columns):
    if os.path.exists(file):
        return pd.read_csv(file, dtype=str) # Force string to avoid login errors
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

# 4. ADVANCED CSS: THE "MOBILE GRID" FIX
st.markdown("""
<style>
/* FORCE 3 COLUMNS TO STAY SIDE-BY-SIDE ON MOBILE */
[data-testid="stHorizontalBlock"] {
    display: flex !important;
    flex-direction: row !important;
    flex-wrap: nowrap !important;
    gap: 4px !important;
    width: 100% !important;
}

[data-testid="column"] {
    flex: 1 1 33.33% !important;
    min-width: 0 !important;
    padding: 0px !important;
}

/* PROFESSIONAL BUTTONS */
.stButton > button {
    width: 100% !important;
    height: 50px !important; /* Fixed height for uniform look */
    font-size: 11px !important;
    font-weight: 500 !important;
    padding: 0px !important;
    line-height: 1.2 !important;
    white-space: pre-wrap !important;
    border-radius: 8px !important;
    border: 1px solid #e0e0e0 !important;
    margin-bottom: -10px !important;
}

/* COLOR SCHEME */
div.stButton > button:not(:disabled) { 
    background-color: #f6ffed !important; 
    color: #389e0d !important; 
    border-color: #b7eb8f !important; 
}
div.stButton > button:disabled { 
    background-color: #fff1f0 !important; 
    color: #cf1322 !important; 
    border-color: #ffa39e !important; 
    opacity: 1 !important; 
}

/* HEADERS */
.header-label {
    background: #001529;
    color: white;
    text-align: center;
    font-weight: bold;
    font-size: 12px;
    padding: 8px 0;
    border-radius: 4px;
    margin-bottom: 20px;
}
</style>
""", unsafe_allow_html=True)

# 5. LOGIN / REGISTER
if st.session_state.user is None:
    st.title("🎱 POOL RESERVE")
    choice = st.radio("Access", ["Login", "Register"], horizontal=True)
    
    with st.container():
        email = st.text_input("Email").strip().lower()
        pwd = st.text_input("Password", type="password").strip()
        
        if choice == "Login":
            if st.button("Log In", use_container_width=True):
                u = users[(users["Email"] == email) & (users["Password"] == pwd)]
                if not u.empty:
                    st.session_state.user = email
                    st.session_state.name = u.iloc[0]["Name"]
                    st.session_state.role = u.iloc[0]["Role"]
                    st.rerun()
                else: st.error("Wrong email or password.")
        else:
            name = st.text_input("Name").strip()
            if st.button("Register Account", use_container_width=True):
                if email and pwd and name:
                    role = "admin" if users.empty else "user"
                    new_u = pd.DataFrame([{"Email": email, "Name": name, "Password": pwd, "Role": role}])
                    save_data(pd.concat([users, new_u]), USERS_FILE)
                    st.success("Success! Please switch to Login.")
    st.stop()

# 6. MAIN BOOKING INTERFACE
st.sidebar.write(f"Logged in: **{st.session_state.name}**")
if st.sidebar.button("Logout"):
    st.session_state.user = None
    st.rerun()

st.title("RESERVE TABLE")

# Professional Date Picker
today = datetime.now().date()
dates = [today + timedelta(days=i) for i in range(14)]
labels = [d.strftime("%A, %d %b") for d in dates]
sel_label = st.selectbox("📅 Select Booking Date", labels)
sel_date = str(dates[labels.index(sel_label)])

# Table Headers (Fixed 3-Column)
h_cols = st.columns(3)
table_list = ["Table 1", "Table 2", "Table 3"]
for i in range(3):
    h_cols[i].markdown(f"<div class='header-label'>{table_list[i]}</div>", unsafe_allow_html=True)

# Grid Generation
HOURS = [f"{h:02d}:{m}" for h in (list(range(8, 24)) + list(range(0, 3))) for m in ["00", "30"]]

for t in HOURS:
    t_cols = st.columns(3)
    for i in range(3):
        t_name = table_list[i]
        match = bookings[(bookings["Table"] == t_name) & (bookings["Time"] == t) & (bookings["Date"] == sel_date)]
        key = f"slot_{i}_{t}_{sel_date}"
        
        with t_cols[i]:
            if not match.empty:
                booked_user = match.iloc[0]["User"]
                booked_name = match.iloc[0]["Name"]
                
                # Logic: Can I delete this?
                if st.session_state.role == "admin" or booked_user == st.session_state.user:
                    if st.button(f"{t}\n❌ {booked_name[:7]}", key=key):
                        bookings = bookings.drop(match.index)
                        save_data(bookings, BOOKINGS_FILE)
                        st.rerun()
                else:
                    # Locked slot
                    st.button(f"{t}\n🔒 {booked_name[:7]}", key=key, disabled=True)
            else:
                # Free slot
                if st.button(f"{t}\n🟢 Free", key=key):
                    new_b = pd.DataFrame([{
                        "User": st.session_state.user,
                        "Name": st.session_state.name,
                        "Date": sel_date,
                        "Table": t_name,
                        "Time": t
                    }])
                    save_data(pd.concat([bookings, new_b]), BOOKINGS_FILE)
                    st.rerun()

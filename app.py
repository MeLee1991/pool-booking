import os
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

# Set page to wide to maximize screen space
st.set_page_config(page_title="Pool Booking", layout="wide", initial_sidebar_state="collapsed")

# =========================
# 1. DATABASE HELPERS
# =========================
USERS_FILE = "users.csv"
BOOKINGS_FILE = "bookings.csv"

def load_data(file, columns):
    if os.path.exists(file):
        return pd.read_csv(file)
    return pd.DataFrame(columns=columns)

def save_data(df, file):
    df.to_csv(file, index=False)

# Initialize data
users = load_data(USERS_FILE, ["Email", "Name", "Password", "Role"])
bookings = load_data(BOOKINGS_FILE, ["User", "Name", "Date", "Table", "Time"])

# =========================
# 2. SESSION STATE
# =========================
if "user" not in st.session_state: st.session_state.user = None
if "role" not in st.session_state: st.session_state.role = None
if "name" not in st.session_state: st.session_state.name = None
if "table_names" not in st.session_state: st.session_state.table_names = ["Table 1", "Table 2", "Table 3"]

# =========================
# 3. STRICT MOBILE CSS
# =========================
st.markdown("""
<style>
/* 1. FORCE 3 COLUMNS TO FIT SCREEN WIDTH EXACTLY */
[data-testid="stHorizontalBlock"] {
    display: flex !important;
    flex-direction: row !important;
    flex-wrap: nowrap !important; /* absolutely prevents vertical stacking */
    gap: 2px !important;
    width: 100% !important;
    padding: 0 !important;
}

/* 2. FORCE EACH COLUMN TO BE EXACTLY 33% */
[data-testid="column"] {
    flex: 1 1 33.33% !important;
    width: 33.33% !important;
    min-width: 0 !important; /* Critical for narrow screens */
    padding: 0 2px !important;
}

/* 3. BUTTON DESIGN (FIXED HEIGHT, 2 ROWS) */
.stButton > button {
    width: 100% !important;
    height: 45px !important;
    font-size: 11px !important;
    line-height: 1.2 !important;
    padding: 0 !important;
    margin-bottom: -10px !important; /* Pulls rows tighter vertically */
    border-radius: 4px !important;
    border: 1px solid #ccc !important;
    white-space: pre-wrap !important;
    overflow: hidden !important;
}

/* 4. BUTTON COLORS BASED ON STATE */
div.stButton > button:disabled {
    background-color: #f8d7da !important; /* Red for locked */
    color: #721c24 !important;
    opacity: 1 !important;
}
div.stButton > button:not(:disabled) {
    background-color: #d4edda !important; /* Green for free / clickable */
    color: #155724 !important;
}

/* 5. HEADER DESIGN */
.tbl-header {
    background-color: #212529;
    color: white;
    text-align: center;
    font-weight: bold;
    font-size: 12px;
    padding: 5px 0;
    border-radius: 3px;
    margin-bottom: 15px;
}
</style>
""", unsafe_allow_html=True)

# =========================
# 4. LOGIN & AUTH FLOW
# =========================
if st.session_state.user is None:
    st.title("🎱 Pool Booking")
    st.subheader("Login or Register")
    
    tab1, tab2 = st.tabs(["Login", "Register"])
    
    with tab1:
        # Added strip() to prevent hidden spaces from breaking login
        email_in = st.text_input("Email").strip().lower()
        pass_in = st.text_input("Password", type="password").strip()
        
        if st.button("Log In", use_container_width=True):
            # Find user
            match = users[(users["Email"] == email_in) & (users["Password"] == pass_in)]
            if not match.empty:
                st.session_state.user = match.iloc[0]["Email"]
                st.session_state.name = match.iloc[0]["Name"]
                st.session_state.role = match.iloc[0]["Role"]
                st.rerun()
            else:
                st.error("Invalid credentials. Please try again.")

    with tab2:
        new_email = st.text_input("New Email").strip().lower()
        new_name = st.text_input("Full Name").strip()
        new_pass = st.text_input("New Password", type="password").strip()
        
        if st.button("Register", use_container_width=True):
            if new_email and new_name and new_pass:
                # First user becomes admin, others become user
                assigned_role = "admin" if users.empty else "user"
                new_row = pd.DataFrame([[new_email, new_name, new_pass, assigned_role]], columns=users.columns)
                users = pd.concat([users, new_row], ignore_index=True)
                save_data(users, USERS_FILE)
                st.success("Registered! You can now log in.")
            else:
                st.warning("Please fill in all fields.")
    st.stop() # Stops the rest of the app from loading until logged in

# =========================
# 5. MAIN APP UI
# =========================
# Sidebar Controls
st.sidebar.markdown(f"👤 **{st.session_state.name}** ({st.session_state.role})")
if st.sidebar.button("Log Out"):
    st.session_state.user = None
    st.session_state.role = None
    st.rerun()

# Admin Actions
if st.session_state.role == "admin":
    st.sidebar.divider()
    st.sidebar.markdown("🛠️ **Admin Controls**")
    if st.sidebar.checkbox("Show Users Database"):
        st.write("### User Management")
        edited_users = st.data_editor(users)
        if st.button("Save User Changes"):
            save_data(edited_users, USERS_FILE)
            st.success("Users updated.")

st.title("RESERVE TABLE")

# Date Selector (Selectbox is completely bug-proof on mobile)
today = datetime.now().date()
date_list = [today + timedelta(days=i) for i in range(14)]
date_strings = [d.strftime("%A, %d %b") for d in date_list]

selected_date_str = st.selectbox("📅 Choose Date", date_strings)
selected_date = str(date_list[date_strings.index(selected_date_str)])

# =========================
# 6. THE 3-COLUMN GRID
# =========================
# Render headers
h_cols = st.columns(3)
for i in range(3):
    h_cols[i].markdown(f"<div class='tbl-header'>{st.session_state.table_names[i]}</div>", unsafe_allow_html=True)

# Generate Time Slots
HOURS = []
for h in list(range(8, 24)) + list(range(0, 3)):
    for m in ["00", "30"]:
        HOURS.append(f"{h:02d}:{m}")

# Render rows
for t in HOURS:
    t_cols = st.columns(3)
    for i in range(3):
        t_name = st.session_state.table_names[i]
        
        # Check if slot is booked
        match = bookings[(bookings["Table"] == t_name) & (bookings["Time"] == t) & (bookings["Date"] == selected_date)]
        key = f"btn_{i}_{t}_{selected_date}"
        
        with t_cols[i]:
            if not match.empty:
                b_user = match.iloc[0]["User"]
                b_name = match.iloc[0]["Name"]
                
                # PERMISSIONS LOGIC
                if b_user == st.session_state.user or st.session_state.role == "admin":
                    # I booked it OR I am admin -> Click to CANCEL/RELEASE
                    if st.button(f"{t}\n❌ {b_name[:6]}", key=key):
                        bookings = bookings.drop(match.index) # Remove the booking
                        save_data(bookings, BOOKINGS_FILE)
                        st.rerun()
                else:
                    # Someone else booked it -> Locked
                    st.button(f"{t}\n🔒 {b_name[:6]}", key=key, disabled=True)
            else:
                # SLOT IS FREE
                if st.button(f"{t}\n🟢 Free", key=key):
                    # Create new booking
                    new_b = pd.DataFrame([[st.session_state.user, st.session_state.name, selected_date, t_name, t]], 
                                         columns=["User","Name","Date","Table","Time"])
                    bookings = pd.concat([bookings, new_b], ignore_index=True)
                    save_data(bookings, BOOKINGS_FILE)
                    st.rerun()

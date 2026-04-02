import os

# ==========================================
# 0. THE "KILL DARK MODE" SCRIPT
# ==========================================
if not os.path.exists('.streamlit'):
    os.makedirs('.streamlit')
with open('.streamlit/config.toml', 'w') as f:
    f.write('''
[theme]
base="light"
primaryColor="#dc3545"
backgroundColor="#f8f9fa"
secondaryBackgroundColor="#e9ecef"
textColor="#212529"
font="sans serif"
''')

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

st.set_page_config(page_title="Poolhall Reservations", layout="wide")

# ==========================================
# 1. CSS: STICKY HEADERS & SCROLLABLE GRID
# ==========================================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Roboto', sans-serif !important;
    }

    .block-container {
        max-width: 750px !important; 
        margin: 0 auto !important;
        padding-top: 1rem !important;
    }

    /* ---------------------------------------------------
       SCROLLABLE TABLE SECTION
       --------------------------------------------------- */
    /* This makes the area below headers scrollable */
    .scroll-container {
        height: 65vh; /* Adjust height for phone screens */
        overflow-y: auto;
        overflow-x: hidden;
        padding-right: 5px;
        border-bottom: 1px solid #dee2e6;
    }

    /* ---------------------------------------------------
       UI COMPONENTS
       --------------------------------------------------- */
    .table-header {
        text-align: center !important;
        font-size: 14px !important;
        font-weight: 700 !important;
        text-transform: uppercase !important;
        color: #ffffff !important; 
        background-color: #343a40 !important; 
        padding: 10px 0;
        border-radius: 4px !important;
        margin-bottom: 5px !important; 
    }

    [data-testid="column"] .stButton > button {
        width: 100% !important;
        border-radius: 4px !important; 
        border: 1px solid #dee2e6 !important; 
        padding: 6px 2px !important; 
        min-height: 42px !important; 
        margin-bottom: 4px !important; 
        font-size: 13px !important; 
        background-color: #ffffff !important; 
    }
    
    /* Alternating row colors */
    [data-testid="column"] > div:nth-child(4n) button,
    [data-testid="column"] > div:nth-child(4n+1) button {
        background-color: #f8f9fa !important; 
    }

    /* RESERVED RED */
    .stButton > button[kind="primary"] {
        background-color: #ff4b4b !important;
        border: 1px solid #ff4b4b !important;
        color: #ffffff !important;
    }
    
    .stButton > button[kind="primary"] p {
        color: #ffffff !important;
    }

    .admin-panel {
        background-color: #fff5f5;
        border: 2px solid #ff4b4b;
        border-radius: 8px;
        padding: 12px;
        margin-bottom: 10px;
    }
    
    /* Date Ribbon Styling */
    section[data-testid="stMain"] [data-testid="stRadio"] > div[role="radiogroup"] {
        display: flex !important;
        overflow-x: auto !important;
        gap: 8px !important;
        padding-bottom: 10px !important;
    }
    div[role="radiogroup"] div[role="radio"] > div:first-child { display: none !important; }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 2. DATABASE HELPERS
# ==========================================
USERS_FILE, BOOKINGS_FILE, AUDIT_FILE = 'users.csv', 'bookings.csv', 'audit.csv'
OWNER_EMAIL = "tomazbratina@gmail.com"

for f_path, cols in [(USERS_FILE, ['Email', 'Name', 'Password', 'Role']), 
                     (BOOKINGS_FILE, ['User', 'Date', 'Table', 'Time', 'Duration']), 
                     (AUDIT_FILE, ['Timestamp', 'Action', 'Performed_By', 'Target_User', 'Details'])]:
    if not os.path.exists(f_path): pd.DataFrame(columns=cols).to_csv(f_path, index=False)

def load_users(): return pd.read_csv(USERS_FILE)
def save_users(df): df.to_csv(USERS_FILE, index=False)
def load_bookings(): return pd.read_csv(BOOKINGS_FILE)
def save_bookings(df): df.to_csv(BOOKINGS_FILE, index=False)

# ==========================================
# 3. AUTHENTICATION
# ==========================================
if 'logged_in_user' not in st.session_state: st.session_state.logged_in_user = None
if 'admin_selected_slot' not in st.session_state: st.session_state.admin_selected_slot = None

st.sidebar.title("🔐 Access")
if st.session_state.logged_in_user is None:
    auth_mode = st.sidebar.radio("Mode", ["Login", "Register"])
    email = st.sidebar.text_input("Email").strip().lower()
    name = st.sidebar.text_input("Short Name") if auth_mode == "Register" else ""
    pwd = st.sidebar.text_input("Password", type="password")
    if st.sidebar.button("Go"):
        u_df = load_users()
        if auth_mode == "Register":
            role = 'admin' if email == OWNER_EMAIL else 'pending'
            save_users(pd.concat([u_df, pd.DataFrame([[email, name, pwd, role]], columns=['Email', 'Name', 'Password', 'Role'])]))
            st.sidebar.success("Done!")
        else:
            match = u_df[(u_df['Email'] == email) & (u_df['Password'] == pwd)]
            if not match.empty:
                st.session_state.logged_in_user, st.session_state.logged_in_name, st.session_state.user_role = email, match.iloc[0]['Name'], match.iloc[0]['Role']
                st.rerun()
    st.stop()

if st.sidebar.button("Logout"): st.session_state.logged_in_user = None; st.rerun()
view_mode = st.sidebar.radio("Menu", ["📅 Schedule", "⚙️ Admin Dashboard"]) if st.session_state.user_role == 'admin' else "📅 Schedule"

# ==========================================
# 4. ADMIN DASHBOARD
# ==========================================
if view_mode == "⚙️ Admin Dashboard":
    st.title("⚙️ Admin")
    u_df = load_users()
    edited = st.data_editor(u_df, use_container_width=True)
    if st.button("Save"): save_users(edited); st.rerun()
    st.stop()

# ==========================================
# 5. THE SCHEDULER
# ==========================================
st.markdown("### RESERVE TABLE")

# 14-Day Selector
today = datetime.now().date()
dates = [today + timedelta(days=i) for i in range(14)]
labels = [d.strftime("%a %d") for d in dates]
sel_date = st.radio("Date", labels, horizontal=True, label_visibility="collapsed")
view_date = dates[labels.index(sel_date)]

bookings_df = load_bookings()
relevant = bookings_df[bookings_df['Date'] == str(view_date)]
name_lookup = dict(zip(load_users()['Email'], load_users()['Name']))

# --- REMOVAL / ADMIN PANEL ---
if st.session_state.admin_selected_slot:
    slot = st.session_state.admin_selected_slot
    with st.container():
        st.markdown(f"<div class='admin-panel'><b>Action:</b> {slot['Time']} ({slot['Display_Name']})</div>", unsafe_allow_html=True)
        c1, c2, c3 = st.columns(3)
        if c1.button("🗑️ REMOVE", type="primary"):
            bookings_df = bookings_df[~((bookings_df['Table'] == slot['Table']) & (bookings_df['Time'] == slot['Time']) & (bookings_df['Date'] == str(view_date)))]
            save_bookings(bookings_df); st.session_state.admin_selected_slot = None; st.rerun()
        
        if st.session_state.user_role == 'admin' and c2.button("✏️ EDIT NAME"):
            st.session_state.admin_edit_mode = True
        
        if c3.button("Close"): st.session_state.admin_selected_slot = None; st.rerun()
        
        if getattr(st.session_state, 'admin_edit_mode', False):
            new_n = st.text_input("New Name:")
            if st.button("Save Name"):
                bookings_df.loc[(bookings_df['Table'] == slot['Table']) & (bookings_df['Time'] == slot['Time']) & (bookings_df['Date'] == str(view_date)), 'User'] = new_n
                save_bookings(bookings_df); st.session_state.admin_edit_mode = False; st.session_state.admin_selected_slot = None; st.rerun()

# --- TABLE HEADERS (Fixed) ---
h_cols = st.columns(3)
for i, h_col in enumerate(h_cols):
    h_col.markdown(f"<div class='table-header'>Tbl {i+1}</div>", unsafe_allow_html=True)

# --- SCROLLABLE GRID AREA ---
HOURS = [f"{h:02d}:{m}" for h in range(8, 24) for m in ("00", "30")] 

st.markdown('<div class="scroll-container">', unsafe_allow_html=True)
cols = st.columns(3)
for i, col in enumerate(cols):
    t_id = f"Table {i+1}"
    for time_str in HOURS:
        booked = relevant[(relevant['Table'] == t_id) & (relevant['Time'] == time_str)]
        key = f"b_{t_id}_{time_str}_{view_date}"
        
        if not booked.empty:
            user_val = booked.iloc[0]['User']
            disp_name = name_lookup.get(user_val, user_val)
            
            # Clickable for Admin OR current User
            if st.session_state.user_role == 'admin' or user_val == st.session_state.logged_in_user:
                if col.button(f"{time_str} {disp_name}", key=key, type="primary", use_container_width=True):
                    st.session_state.admin_selected_slot = {'Table': t_id, 'Time': time_str, 'Display_Name': disp_name, 'User': user_val}
                    st.rerun()
            else:
                col.button(f"{time_str} 🔒 {disp_name}", key=key, disabled=True, use_container_width=True)
        else:
            if col.button(f"{time_str} 🟢 FREE", key=key, use_container_width=True):
                new_row = pd.DataFrame([[st.session_state.logged_in_user, str(view_date), t_id, time_str, 0.5]], columns=['User', 'Date', 'Table', 'Time', 'Duration'])
                save_bookings(pd.concat([bookings_df, new_row], ignore_index=True)); st.rerun()
st.markdown('</div>', unsafe_allow_html=True)

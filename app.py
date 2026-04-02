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
''')

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

st.set_page_config(page_title="Poolhall Reservations", layout="wide")

# ==========================================
# 1. CLEAN STRUCTURAL CSS
# ==========================================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Roboto', sans-serif !important;
        font-weight: 300 !important;
    }
    
    h1, h2, h3, h4 {
        font-family: 'Roboto', sans-serif !important;
        font-weight: 500 !important;
        text-align: center;
    }

    .block-container {
        max-width: 750px !important; 
        margin: 0 auto !important;
        padding-top: 1.5rem !important;
    }

    /* ---------------------------------------------------
       MAIN AREA: SWIPEABLE DATE RIBBON
       --------------------------------------------------- */
    section[data-testid="stMain"] [data-testid="stRadio"] > div[role="radiogroup"] {
        display: grid !important;
        grid-template-columns: max-content repeat(7, max-content) !important;
        grid-template-rows: auto auto !important;
        gap: 12px 8px !important; 
        padding: 10px 5px 15px 5px !important;
        border-bottom: 1px solid #dee2e6; 
        margin-bottom: 20px !important;
        overflow-x: auto !important; 
        scrollbar-width: none; 
        align-items: center;
    }
    
    section[data-testid="stMain"] [data-testid="stRadio"] label {
        background-color: #ffffff !important;
        border: 1px solid #ced4da !important;
        border-radius: 6px !important;
        padding: 6px 12px !important;
        min-width: max-content; 
        cursor: pointer;
    }
    
    section[data-testid="stMain"] [data-testid="stRadio"] label[data-checked="true"] {
        background-color: #007bff !important; 
        border-color: #007bff !important;
    }
    section[data-testid="stMain"] [data-testid="stRadio"] label[data-checked="true"] p {
        color: #ffffff !important;
    }
    
    div[role="radiogroup"] div[role="radio"] > div:first-child {
        display: none !important;
    }

    /* ---------------------------------------------------
       MAIN AREA: TABLES & HOUR BANDING
       --------------------------------------------------- */
    [data-testid="stHorizontalBlock"] {
        gap: 10px !important; 
        justify-content: center !important;
    }

    .table-header {
        text-align: center !important;
        font-size: 14px !important;
        font-weight: 700 !important;
        text-transform: uppercase !important;
        color: #ffffff !important; 
        background-color: #343a40 !important; 
        padding: 8px 0;
        border-radius: 4px !important;
        margin-bottom: 10px !important; 
    }

    /* Base Grid Button Style */
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
    
    /* Banding for rows */
    [data-testid="column"] > div:nth-child(4n) button,
    [data-testid="column"] > div:nth-child(4n+1) button {
        background-color: #f8f9fa !important; 
    }

    /* BRIGHT RED for all reserved slots (Admin click power) */
    .stButton > button[kind="primary"] {
        background-color: #ff4b4b !important; /* Bright Red */
        border: 1px solid #ff4b4b !important;
        color: #ffffff !important;
        font-weight: 500 !important;
    }
    .stButton > button[kind="primary"] p {
        color: #ffffff !important;
    }

    /* Taken but Locked (Normal User View) */
    [data-testid="column"] button:disabled {
        background-color: #e9ecef !important; 
        border: 1px solid #ced4da !important;
        color: #6c757d !important;
    }

    .admin-panel {
        background-color: #fff5f5;
        border: 2px solid #ff4b4b;
        border-radius: 8px;
        padding: 15px;
        margin-bottom: 20px;
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 2. DATABASE & LOGGING SETUP
# ==========================================
USERS_FILE = 'users.csv'
BOOKINGS_FILE = 'bookings.csv'
AUDIT_FILE = 'audit.csv'
OWNER_EMAIL = "tomazbratina@gmail.com" 

if not os.path.exists(USERS_FILE):
    pd.DataFrame(columns=['Email', 'Name', 'Password', 'Role']).to_csv(USERS_FILE, index=False)
if not os.path.exists(BOOKINGS_FILE):
    pd.DataFrame(columns=['User', 'Date', 'Table', 'Time', 'Duration']).to_csv(BOOKINGS_FILE, index=False)
if not os.path.exists(AUDIT_FILE):
    pd.DataFrame(columns=['Timestamp', 'Action', 'Performed_By', 'Target_User', 'Details']).to_csv(AUDIT_FILE, index=False)

def load_users(): 
    try:
        df = pd.read_csv(USERS_FILE)
        return df
    except:
        return pd.DataFrame(columns=['Email', 'Name', 'Password', 'Role'])

def save_users(df): df.to_csv(USERS_FILE, index=False)
def load_bookings(): return pd.read_csv(BOOKINGS_FILE)
def save_bookings(df): df.to_csv(BOOKINGS_FILE, index=False)

def log_action(action, performed_by, target_user, details):
    audit_df = pd.read_csv(AUDIT_FILE)
    new_log = pd.DataFrame([[datetime.now().strftime("%Y-%m-%d %H:%M:%S"), action, performed_by, target_user, details]], 
                           columns=['Timestamp', 'Action', 'Performed_By', 'Target_User', 'Details'])
    pd.concat([audit_df, new_log], ignore_index=True).to_csv(AUDIT_FILE, index=False)

# ==========================================
# 3. AUTHENTICATION & STATE
# ==========================================
if 'logged_in_user' not in st.session_state:
    st.session_state.logged_in_user = None
if 'user_role' not in st.session_state:
    st.session_state.user_role = None

if 'admin_selected_slot' not in st.session_state:
    st.session_state.admin_selected_slot = None
if 'admin_edit_mode' not in st.session_state:
    st.session_state.admin_edit_mode = False

st.sidebar.markdown("<h2>🔐 Access</h2>", unsafe_allow_html=True)

if st.session_state.logged_in_user is None:
    auth_mode = st.sidebar.radio("Mode", ["Login", "Register"])
    email_input = st.sidebar.text_input("Email").strip().lower()
    if auth_mode == "Register":
        display_name = st.sidebar.text_input("Short Name")
    password = st.sidebar.text_input("Password", type="password")
    
    if st.sidebar.button("Go", use_container_width=True):
        users = load_users()
        if auth_mode == "Register":
            if email_input in users['Email'].values: st.sidebar.error("Exists!")
            else:
                role = 'admin' if email_input == OWNER_EMAIL else 'pending'
                new_user = pd.DataFrame([[email_input, display_name, password, role]], columns=['Email', 'Name', 'Password', 'Role'])
                save_users(pd.concat([users, new_user], ignore_index=True))
                st.sidebar.success("Done! Login now.")
        else:
            user_match = users[(users['Email'] == email_input) & (users['Password'] == password)]
            if not user_match.empty:
                st.session_state.logged_in_user = email_input
                st.session_state.logged_in_name = user_match.iloc[0]['Name']
                st.session_state.user_role = user_match.iloc[0]['Role']
                st.rerun()
            else: st.sidebar.error("Wrong details.")
    st.stop()

# --- Post-Login ---
st.sidebar.success(f"User: {st.session_state.logged_in_name}")
if st.sidebar.button("Logout"):
    st.session_state.logged_in_user = None
    st.rerun()

view_mode = "📅 Schedule"
if st.session_state.user_role == 'admin':
    view_mode = st.sidebar.radio("Menu", ["📅 Schedule", "⚙️ Admin Dashboard"])

if view_mode == "⚙️ Admin Dashboard":
    st.title("⚙️ Club Admin")
    t1, t2, t3 = st.tabs(["Users", "Bookings", "Logs"])
    with t1:
        u_df = load_users()
        edited = st.data_editor(u_df, use_container_width=True)
        if st.button("Save Changes"): save_users(edited); st.rerun()
    with t2: st.dataframe(load_bookings(), use_container_width=True)
    with t3: st.dataframe(pd.read_csv(AUDIT_FILE) if st.session_state.logged_in_user == OWNER_EMAIL else "Denied", use_container_width=True)
    st.stop()

# ==========================================
# 4. THE BOOKING SYSTEM
# ==========================================
st.markdown("<h1>RESERVE <span style='color: #dc3545;'>TABLE</span></h1>", unsafe_allow_html=True)

HOURS = [f"{h:02d}:{m}" for h in range(8, 24) for m in ("00", "30")] 
today = datetime.now().date()
upcoming_dates = [today + timedelta(days=i) for i in range(14)]
date_labels = ["Today" if d == today else "Tomorrow" if d == today + timedelta(days=1) else d.strftime("%a %d") for d in upcoming_dates]
selected_date_label = st.radio("Date", date_labels, horizontal=True, label_visibility="collapsed")
view_date = upcoming_dates[date_labels.index(selected_date_label)]

# Auto-close admin panel on date change
if 'last_date' not in st.session_state: st.session_state.last_date = view_date
if st.session_state.last_date != view_date:
    st.session_state.admin_selected_slot = None
    st.session_state.last_date = view_date

bookings_df = load_bookings()
relevant = bookings_df[bookings_df['Date'] == str(view_date)]
users_df = load_users()
name_lookup = dict(zip(users_df['Email'], users_df['Name']))

# --- ADMIN PANEL ---
if st.session_state.user_role == 'admin' and st.session_state.admin_selected_slot:
    slot = st.session_state.admin_selected_slot
    with st.container():
        st.markdown(f"<div class='admin-panel'><b>Admin Control:</b> {slot['Table']} at {slot['Time']} ({slot['Display_Name']})</div>", unsafe_allow_html=True)
        if st.session_state.admin_edit_mode:
            new_name = st.text_input("Change Name to:", value=slot['Display_Name'])
            c1, c2 = st.columns(2)
            if c1.button("💾 Save"):
                bookings_df.loc[(bookings_df['Table'] == slot['Table']) & (bookings_df['Time'] == slot['Time']) & (bookings_df['Date'] == str(view_date)), 'User'] = new_name
                save_bookings(bookings_df); st.session_state.admin_selected_slot = None; st.rerun()
            if c2.button("Cancel"): st.session_state.admin_edit_mode = False; st.rerun()
        else:
            c1, c2, c3 = st.columns(3)
            if c1.button("🗑️ FREE SLOT", type="primary"):
                bookings_df = bookings_df[~((bookings_df['Table'] == slot['Table']) & (bookings_df['Time'] == slot['Time']) & (bookings_df['Date'] == str(view_date)))]
                save_bookings(bookings_df); st.session_state.admin_selected_slot = None; st.rerun()
            if c2.button("✏️ EDIT NAME"): st.session_state.admin_edit_mode = True; st.rerun()
            if c3.button("Close"): st.session_state.admin_selected_slot = None; st.rerun()

# --- THE GRID ---
cols = st.columns(3)
for i, col in enumerate(cols):
    t_id = f"Table {i+1}"
    col.markdown(f"<div class='table-header'>Tbl {i+1}</div>", unsafe_allow_html=True)
    for time_str in HOURS:
        booked = relevant[(relevant['Table'] == t_id) & (relevant['Time'] == time_str)]
        key = f"btn_{t_id}_{time_str}_{view_date}"
        
        if not booked.empty:
            user_val = booked.iloc[0]['User']
            disp_name = name_lookup.get(user_val, user_val)
            
            # ADMIN sees EVERYTHING in BRIGHT RED (Primary)
            if st.session_state.user_role == 'admin':
                if col.button(f"{time_str} ⚙️ {disp_name}", key=key, type="primary", use_container_width=True):
                    st.session_state.admin_selected_slot = {'Table': t_id, 'Time': time_str, 'Display_Name': disp_name, 'User': user_val}
                    st.rerun()
            # OWNER can only cancel their OWN slots (Email matches)
            elif user_val == st.session_state.logged_in_user:
                if col.button(f"{time_str} ❌ {disp_name}", key=key, type="primary", use_container_width=True):
                    bookings_df = bookings_df[~((bookings_df['Table'] == t_id) & (bookings_df['Time'] == time_str) & (bookings_df['Date'] == str(view_date)))]
                    save_bookings(bookings_df); st.rerun()
            # LOCKED for others
            else:
                col.button(f"{time_str} 🔒 {disp_name}", key=key, disabled=True, use_container_width=True)
        else:
            # FREE SLOT
            if col.button(f"{time_str} 🟢 FREE", key=key, use_container_width=True):
                new_row = pd.DataFrame([[st.session_state.logged_in_user, str(view_date), t_id, time_str, 0.5]], columns=['User', 'Date', 'Table', 'Time', 'Duration'])
                save_bookings(pd.concat([bookings_df, new_row], ignore_index=True)); st.rerun()

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import os

st.set_page_config(page_title="Poolhall Reservations", layout="wide")

# ==========================================
# 0. CLEAN STANDARD UI (Roboto Light)
# ==========================================
st.markdown("""
<style>
    /* Import Roboto Font */
    @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500&display=swap');

    /* Global Font & Standard Light Theme */
    html, body, .stApp, [data-testid="stSidebar"], [data-testid="stHeader"] {
        background-color: #f8f9fa !important; /* Standard off-white */
        font-family: 'Roboto', sans-serif !important;
        font-weight: 300 !important; /* Roboto Light */
        color: #212529 !important; /* Standard dark text */
    }
    
    p, span, div, label, li {
        font-family: 'Roboto', sans-serif !important;
        font-weight: 300 !important;
        color: #212529 !important;
    }
    
    h1, h2, h3, h4, h5, h6 {
        font-family: 'Roboto', sans-serif !important;
        font-weight: 400 !important; /* Slightly bolder for headings, but still clean */
        color: #212529 !important;
    }
    
    h1 {
        text-align: center;
        margin-bottom: 10px !important;
    }

    /* ---------------------------------------------------
       STANDARD LOGIN INPUTS (Fixes the black boxes)
       --------------------------------------------------- */
    div[data-baseweb="input"] > div {
        background-color: #ffffff !important; /* Strictly white background */
        border: 1px solid #ced4da !important; /* Standard gray border */
        border-radius: 4px !important;
    }
    div[data-baseweb="input"] input {
        color: #495057 !important; /* Standard gray text */
        font-family: 'Roboto', sans-serif !important;
        font-weight: 300 !important;
        background-color: transparent !important;
    }
    
    /* Standardize Sidebar Radio Buttons */
    [data-testid="stSidebar"] [data-testid="stRadio"] label {
        background-color: transparent !important;
        border: none !important;
        box-shadow: none !important;
        padding: 0 !important;
    }
    
    /* Standard Login Button */
    [data-testid="stSidebar"] .stButton > button {
        background-color: #28a745 !important; /* Standard Success Green */
        color: #ffffff !important;
        border-radius: 4px !important;
        border: none !important;
        font-weight: 400 !important;
        width: 100%;
        min-height: 40px;
    }
    [data-testid="stSidebar"] .stButton > button p {
        color: #ffffff !important;
    }

    /* ---------------------------------------------------
       MAIN AREA: CLEAN DATE RIBBON
       --------------------------------------------------- */
    section[data-testid="stMain"] [data-testid="stRadio"] > div[role="radiogroup"] {
        display: flex !important;
        flex-wrap: nowrap !important; 
        overflow-x: auto !important; 
        gap: 10px !important;
        padding: 10px 0 !important;
        border-bottom: 1px solid #dee2e6; 
        margin-bottom: 15px !important;
        -webkit-overflow-scrolling: touch; 
        scrollbar-width: none; 
    }
    section[data-testid="stMain"] [data-testid="stRadio"] > div[role="radiogroup"]::-webkit-scrollbar {
        display: none;
    }
    section[data-testid="stMain"] [data-testid="stRadio"] label {
        background-color: #ffffff !important;
        border: 1px solid #ced4da !important;
        border-radius: 4px !important;
        padding: 8px 16px !important;
        min-width: max-content; 
        cursor: pointer;
    }
    /* Selected Date (Clean Blue) */
    section[data-testid="stMain"] [data-testid="stRadio"] label[data-checked="true"] {
        background-color: #007bff !important; 
        border-color: #007bff !important;
        color: #ffffff !important;
    }
    section[data-testid="stMain"] [data-testid="stRadio"] label[data-checked="true"] p {
        color: #ffffff !important;
    }
    section[data-testid="stMain"] [data-testid="stRadio"] label span[data-baseweb="radio"] {
        display: none !important;
    }

    /* ---------------------------------------------------
       MAIN AREA: CLEAN SCHEDULE GRID
       --------------------------------------------------- */
    @media (max-width: 768px) {
        [data-testid="stHorizontalBlock"] {
            flex-direction: row !important;
            flex-wrap: nowrap !important;
            gap: 4px !important; 
        }
        [data-testid="column"] {
            width: 33.33% !important;
            flex: 1 1 33.33% !important;
            min-width: 30% !important;
            padding: 0 !important; 
        }
    }

    .table-header {
        text-align: center !important;
        font-size: 15px !important;
        font-weight: 500 !important;
        color: #495057 !important; 
        background-color: #e9ecef; /* Light gray header */
        padding: 8px 0;
        border: 1px solid #ced4da;
        border-bottom: none;
        margin-bottom: 0 !important;
    }

    [data-testid="column"] .stButton > button {
        width: 100%;
        border-radius: 0px !important; 
        border: 1px solid #ced4da !important; 
        background-color: #ffffff !important; 
        color: #495057 !important; 
        padding: 4px 2px !important; 
        min-height: 44px !important; 
        margin-bottom: -1px !important; 
        font-size: 12px !important; 
        line-height: 1.2 !important;
        font-weight: 300 !important; /* Roboto Light for grid text */
        text-align: center !important; 
    }
    [data-testid="column"] .stButton > button:hover {
        background-color: #f8f9fa !important; 
        border-color: #adb5bd !important;
        z-index: 2; 
    }
    
    /* Cancel Buttons (Clean Red) */
    [data-testid="column"] button[kind="primary"] {
        background-color: #fff3f3 !important; 
        border: 1px solid #dc3545 !important; 
        color: #dc3545 !important; 
    }
    [data-testid="column"] button[kind="primary"] p {
        color: #dc3545 !important; 
    }
    
    /* Taken Buttons (Grayed out) */
    [data-testid="column"] button:disabled {
        background-color: #e9ecef !important; 
        color: #6c757d !important; 
        border: 1px solid #ced4da !important;
    }
    [data-testid="column"] button:disabled p {
        color: #6c757d !important; 
    }
    
    .block-container {
        padding-top: 2rem !important;
        padding-left: 0.5rem !important;
        padding-right: 0.5rem !important;
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 1. DATABASE & LOGGING SETUP
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
        changed = False
        if 'Username' in df.columns:
            df = df.rename(columns={'Username': 'Email'})
            changed = True
        if 'Name' not in df.columns:
            df.insert(1, 'Name', df['Email'].apply(lambda x: str(x).split('@')[0]))
            changed = True
        if changed:
            df.to_csv(USERS_FILE, index=False)
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
# 2. AUTHENTICATION (Standard Clean Sidebar)
# ==========================================
if 'logged_in_user' not in st.session_state:
    st.session_state.logged_in_user = None
if 'logged_in_name' not in st.session_state:
    st.session_state.logged_in_name = None
if 'user_role' not in st.session_state:
    st.session_state.user_role = None

st.sidebar.markdown("<h2>🔐 Login / Register</h2>", unsafe_allow_html=True)

if st.session_state.logged_in_user is None:
    auth_mode = st.sidebar.radio("Choose Action", ["Login", "Register"])
    email_input = st.sidebar.text_input("Email Address").strip().lower()
    
    if auth_mode == "Register":
        display_name = st.sidebar.text_input("Display Name (e.g. Tomi)").strip()
        
    password = st.sidebar.text_input("Password", type="password")
    
    if auth_mode == "Register":
        if st.sidebar.button("Create Account"):
            users = load_users()
            if email_input in users['Email'].values:
                st.sidebar.error("Email already exists!")
            elif len(email_input) < 5 or "@" not in email_input:
                st.sidebar.error("Valid email required.")
            elif len(display_name) < 2:
                st.sidebar.error("Display name required.")
            else:
                role = 'admin' if email_input == OWNER_EMAIL else 'pending'
                new_user = pd.DataFrame([[email_input, display_name, password, role]], columns=['Email', 'Name', 'Password', 'Role'])
                save_users(pd.concat([users, new_user], ignore_index=True))
                st.sidebar.success("Account created! Switch to Login.")
                
    elif auth_mode == "Login":
        if st.sidebar.button("Login"):
            users = load_users()
            user_match = users[(users['Email'] == email_input) & (users['Password'] == password)]
            
            if not user_match.empty:
                role = user_match.iloc[0]['Role']
                if role == 'pending':
                    st.sidebar.error("Awaiting Admin approval.")
                else:
                    st.session_state.logged_in_user = email_input
                    st.session_state.logged_in_name = user_match.iloc[0]['Name']
                    st.session_state.user_role = role
                    st.rerun()
            else:
                st.sidebar.error("Incorrect email/password.")
                
    st.markdown("<h1>RESERVE TABLE</h1>", unsafe_allow_html=True)
    st.info("👈 Please use the sidebar menu to log in or register to view the schedule.")
    st.stop()

# --- Everything below this line only happens if logged in ---
st.sidebar.success(f"Playing as: \n**{st.session_state.logged_in_name}**")
if st.sidebar.button("Logout"):
    st.session_state.logged_in_user = None
    st.session_state.logged_in_name = None
    st.session_state.user_role = None
    st.rerun()

view_mode = "📅 Schedule"
if st.session_state.user_role == 'admin':
    st.sidebar.markdown("---")
    view_mode = st.sidebar.radio("Navigation", ["📅 Schedule", "⚙️ Admin Dashboard"])

# ==========================================
# 3. ADMIN DASHBOARD
# ==========================================
if view_mode == "⚙️ Admin Dashboard":
    st.title("⚙️ Club Administration")
    tab1, tab2, tab3 = st.tabs(["👥 User Management", "📊 Raw Database", "🕵️‍♂️ Security Audit Log"])
    
    with tab1:
        st.write("### Manage Users")
        users_df = load_users()
        edited_users = st.data_editor(
            users_df,
            column_config={
                "Role": st.column_config.SelectboxColumn("User Role", options=["pending", "user", "admin"], required=True),
                "Name": st.column_config.TextColumn("Display Name"), 
                "Email": st.column_config.TextColumn("Email Address", disabled=True), 
                "Password": st.column_config.TextColumn("Password", disabled=True)
            },
            hide_index=True, use_container_width=True
        )
        if st.button("💾 Save User Changes", type="primary"):
            save_users(edited_users)
            if st.session_state.logged_in_user in edited_users['Email'].values:
                updated_name = edited_users[edited_users['Email'] == st.session_state.logged_in_user].iloc[0]['Name']
                st.session_state.logged_in_name = updated_name
            st.success("Database updated successfully!")

    with tab2:
        st.write("### All Active Bookings")
        st.dataframe(load_bookings(), use_container_width=True)

    with tab3:
        st.write("### Master Action Log")
        if st.session_state.logged_in_user == OWNER_EMAIL:
            st.dataframe(pd.read_csv(AUDIT_FILE), use_container_width=True)
        else:
            st.error("⛔ Access Denied.")
    st.stop()

# ==========================================
# 4. THE BOOKING SYSTEM
# ==========================================
st.markdown("<h1>RESERVE TABLE</h1>", unsafe_allow_html=True)

HOURS = [f"{h:02d}:{m}" for h in range(8, 24) for m in ("00", "30")] 

today = datetime.now().date()
upcoming_dates = [today + timedelta(days=i) for i in range(14)]
def get_date_label(d):
    if d == today: return "Today"
    if d == today + timedelta(days=1): return "Tomorrow"
    return d.strftime("%a %d") 

date_labels = [get_date_label(d) for d in upcoming_dates]

selected_date_label_main = st.radio("Select Date:", date_labels, horizontal=True, label_visibility="collapsed")
view_date = upcoming_dates[date_labels.index(selected_date_label_main)]

bookings_df = load_bookings()
bookings_df['Date'] = bookings_df['Date'].astype(str) 
relevant_bookings = bookings_df[bookings_df['Date'] == str(view_date)]

user_today_hours = relevant_bookings[relevant_bookings['User'] == st.session_state.logged_in_user]['Duration'].sum()

if st.session_state.user_role != 'admin':
    st.caption(f"<div style='text-align:center;'>**Your booked time:** {user_today_hours} / 3.0h</div>", unsafe_allow_html=True)

users_df = load_users()
name_lookup = dict(zip(users_df['Email'], users_df['Name']))

cols = st.columns(3)

for i, col in enumerate(cols):
    t_name = f"Tbl {i+1}"
    col.markdown(f"<div class='table-header'>{t_name}</div>", unsafe_allow_html=True)
    
    for time_str in HOURS:
        booked = relevant_bookings[(relevant_bookings['Table'] == f"Table {i+1}") & (relevant_bookings['Time'] == time_str)]
        button_key = f"T{i+1}_{time_str}_{view_date}"
        
        if not booked.empty:
            booked_user_email = booked.iloc[0]['User']
            short_name = name_lookup.get(booked_user_email, str(booked_user_email).split('@')[0])
            
            if st.session_state.user_role == 'admin' or booked_user_email == st.session_state.logged_in_user:
                btn_label = f"{time_str}\n❌ {short_name}"
                if col.button(btn_label, key=f"del_{button_key}", type="primary"):
                    log_action("CANCELLED", st.session_state.logged_in_user, booked_user_email, f"Table {i+1} | {view_date} | {time_str}")
                    bookings_df = bookings_df[~((bookings_df['Table'] == f"Table {i+1}") & 
                                                (bookings_df['Time'] == time_str) & 
                                                (bookings_df['Date'] == str(view_date)))]
                    save_bookings(bookings_df)
                    st.rerun()
            else:
                btn_label = f"{time_str}\n🔒 {short_name}"
                col.button(btn_label, key=f"dis_{button_key}", disabled=True)
                
        else:
            btn_label = f"{time_str}\n🟢 FREE"
            if col.button(btn_label, key=f"add_{button_key}"):
                if user_today_hours + 0.5 > 3.0 and st.session_state.user_role != 'admin':
                    st.error("Limit reached! (3h/day)")
                else:
                    log_action("BOOKED", st.session_state.logged_in_user, st.session_state.logged_in_user, f"Table {i+1} | {view_date} | {time_str}")
                    new_row = pd.DataFrame([[st.session_state.logged_in_user, str(view_date), f"Table {i+1}", time_str, 0.5]], 
                                           columns=['User', 'Date', 'Table', 'Time', 'Duration'])
                    bookings_df = pd.concat([bookings_df, new_row], ignore_index=True)
                    save_bookings(bookings_df)
                    st.rerun()

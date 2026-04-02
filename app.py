import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import os

st.set_page_config(page_title="Poolhall Reservations", layout="wide")

# ==========================================
# 0. PREMIUM MOBILE UI (Dark Theme & Fixed Inputs)
# ==========================================
st.markdown("""
<style>
    /* Global App Theme */
    .stApp, .stApp > header {
        background-color: #0a0e14 !important; 
        color: #ffffff !important;
    }
    
    /* Force Sidebar Background to match */
    [data-testid="stSidebar"] {
        background-color: #111827 !important;
    }
    
    h1, h2 {
        text-align: center;
        font-weight: 800 !important;
        letter-spacing: 2px;
        margin-bottom: 5px !important;
        color: #ffffff !important;
    }
    
    /* ---------------------------------------------------
       FIXED TEXT INPUTS (Stops white backgrounds on phones)
       --------------------------------------------------- */
    div[data-baseweb="input"] > div {
        background-color: #111827 !important;
        border: 1px solid #374151 !important;
        border-radius: 6px !important;
    }
    div[data-baseweb="input"] input {
        color: #ffffff !important;
    }
    .stTextInput label, .stRadio label {
        color: #9ca3af !important;
    }

    /* ---------------------------------------------------
       MAIN UI BUTTONS (Login, Save, Create)
       --------------------------------------------------- */
    .stButton > button {
        background-color: #10b981 !important;
        color: #000000 !important;
        border-radius: 8px !important;
        font-weight: bold !important;
        border: none !important;
        transition: all 0.2s ease;
        min-height: 45px;
    }
    .stButton > button:hover {
        background-color: #059669 !important;
    }

    /* ---------------------------------------------------
       SWIPEABLE DATE RIBBON (Horizontal Scroll)
       --------------------------------------------------- */
    [data-testid="stRadio"] > div[role="radiogroup"] {
        display: flex !important;
        flex-wrap: nowrap !important; 
        overflow-x: auto !important; 
        justify-content: flex-start !important;
        gap: 12px !important;
        padding: 15px 5px !important;
        border-bottom: 1px solid #1f2937;
        margin-bottom: 15px !important;
        -webkit-overflow-scrolling: touch; 
        scrollbar-width: none; 
    }
    [data-testid="stRadio"] > div[role="radiogroup"]::-webkit-scrollbar {
        display: none;
    }
    
    [data-testid="stRadio"] label {
        background-color: #111827 !important;
        border: 1px solid #374151 !important;
        border-radius: 8px !important;
        padding: 10px 20px !important;
        min-width: max-content; 
        cursor: pointer;
        transition: all 0.2s ease;
        color: #ffffff !important;
    }
    [data-testid="stRadio"] label[data-checked="true"] {
        background-color: #10b981 !important;
        border-color: #10b981 !important;
        color: #000000 !important;
        box-shadow: 0 4px 12px rgba(16, 185, 129, 0.4); 
        font-weight: bold !important;
    }
    [data-testid="stRadio"] label span[data-baseweb="radio"] {
        display: none !important;
    }

    /* ---------------------------------------------------
       CENTERED GRID & MOBILE COLUMNS
       --------------------------------------------------- */
    @media (max-width: 768px) {
        [data-testid="stHorizontalBlock"] {
            flex-direction: row !important;
            flex-wrap: nowrap !important;
            gap: 6px !important; 
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
        font-size: 16px !important;
        font-weight: bold !important;
        color: #10b981 !important;
        background-color: #111827;
        padding: 8px 0;
        border-radius: 6px 6px 0 0;
        margin-bottom: 0 !important;
        border: 1px solid #1f2937;
        border-bottom: none;
    }
    
    /* OVERRIDE BUTTONS IN THE GRID (To make them spreadsheet frames) */
    [data-testid="column"] .stButton > button {
        width: 100%;
        border-radius: 0px !important; 
        border: 1px solid #1f2937 !important; 
        background-color: #111827 !important; 
        color: #e5e7eb !important; 
        padding: 6px 2px !important; 
        min-height: 48px !important; 
        margin-bottom: -1px !important; 
        font-size: 11px !important; 
        line-height: 1.3 !important;
        font-weight: 500 !important;
        text-align: center !important; 
    }
    [data-testid="column"] .stButton > button:hover {
        border-color: #10b981 !important;
        color: #10b981 !important;
    }
    [data-testid="column"] button[kind="primary"] {
        background-color: #3f1416 !important; 
        border: 1px solid #ef4444 !important; 
        color: #fca5a5 !important; 
    }
    [data-testid="column"] button[kind="primary"]:hover {
        background-color: #ef4444 !important;
        color: #ffffff !important;
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
# 2. AUTHENTICATION & LOGIN SYSTEM (Moved to Main Screen)
# ==========================================
if 'logged_in_user' not in st.session_state:
    st.session_state.logged_in_user = None
if 'logged_in_name' not in st.session_state:
    st.session_state.logged_in_name = None
if 'user_role' not in st.session_state:
    st.session_state.user_role = None

# If not logged in, show the login form right in the middle of the screen
if st.session_state.logged_in_user is None:
    st.markdown("<h2>🎱 POOLHALL LOGIN</h2>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Use columns to center the login box
    col1, col2, col3 = st.columns([1, 10, 1])
    with col2:
        auth_mode = st.radio("Choose Action", ["Login", "Register"], horizontal=True)
        email_input = st.text_input("Email Address").strip().lower()
        
        if auth_mode == "Register":
            display_name = st.text_input("Display Name (e.g. Tomi)").strip()
            
        password = st.text_input("Password", type="password")
        st.markdown("<br>", unsafe_allow_html=True)
        
        if auth_mode == "Register":
            if st.button("Create Account", use_container_width=True):
                users = load_users()
                if email_input in users['Email'].values:
                    st.error("Email already exists!")
                elif len(email_input) < 5 or "@" not in email_input:
                    st.error("Valid email required.")
                elif len(display_name) < 2:
                    st.error("Display name required.")
                else:
                    role = 'admin' if email_input == OWNER_EMAIL else 'pending'
                    new_user = pd.DataFrame([[email_input, display_name, password, role]], columns=['Email', 'Name', 'Password', 'Role'])
                    save_users(pd.concat([users, new_user], ignore_index=True))
                    st.success("Account created! Switch to Login.")
                    
        elif auth_mode == "Login":
            if st.button("Login", use_container_width=True):
                users = load_users()
                user_match = users[(users['Email'] == email_input) & (users['Password'] == password)]
                
                if not user_match.empty:
                    role = user_match.iloc[0]['Role']
                    if role == 'pending':
                        st.error("Awaiting Admin approval.")
                    else:
                        st.session_state.logged_in_user = email_input
                        st.session_state.logged_in_name = user_match.iloc[0]['Name']
                        st.session_state.user_role = role
                        st.rerun()
                else:
                    st.error("Incorrect email/password.")
    st.stop() # Stop rendering the app here until they log in

# --- Sidebar (Only visible AFTER login) ---
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
        if st.button("💾 Save User Changes", use_container_width=True):
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
st.markdown("<h1>RESERVE <span style='color: #10b981;'>TABLE</span></h1>", unsafe_allow_html=True)

HOURS = [f"{h:02d}:{m}" for h in range(8, 24) for m in ("00", "30")] 

# Generate 14 days
today = datetime.now().date()
upcoming_dates = [today + timedelta(days=i) for i in range(14)]
def get_date_label(d):
    if d == today: return "Today"
    if d == today + timedelta(days=1): return "Tomorrow"
    return d.strftime("%a %d") 

date_labels = [get_date_label(d) for d in upcoming_dates]

# The Date Selector
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

# 3 Columns for the tables 
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

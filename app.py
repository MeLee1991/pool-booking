import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import os

st.set_page_config(page_title="Poolhall Reservations", layout="wide")

# ==========================================
# 0. MODERN DESIGN CSS (Based on your mockup)
# ==========================================
st.markdown("""
<style>
    /* Global App Background & Text */
    .stApp {
        background-color: #0d1117 !important; /* Deep modern dark theme */
        color: #ffffff !important;
    }
    
    /* Center and style the main title */
    h1 {
        text-align: center;
        font-weight: 800 !important;
        letter-spacing: 1px;
        text-transform: uppercase;
        margin-bottom: 20px !important;
    }
    
    /* Style the Date Selector to be full-width and modern */
    [data-testid="stRadio"] > div[role="radiogroup"] {
        display: flex !important;
        flex-wrap: wrap !important;
        justify-content: center !important;
        gap: 6px !important;
        width: 100% !important;
        padding: 10px 0 !important;
        border-bottom: 1px solid #2d333b;
        margin-bottom: 15px !important;
    }
    
    /* Make the Table Headers modern */
    h3 {
        text-align: center !important;
        font-size: 15px !important;
        font-weight: bold !important;
        color: #10b981 !important; /* Emerald Green */
        text-transform: uppercase;
        background-color: #161b22;
        padding: 8px 0;
        border-radius: 4px;
    }

    /* 1. Force columns to stay side-by-side on mobile */
    @media (max-width: 768px) {
        [data-testid="stHorizontalBlock"] {
            flex-direction: row !important;
            flex-wrap: nowrap !important;
        }
        [data-testid="column"] {
            width: 33.33% !important;
            flex: 1 1 33.33% !important;
            min-width: 32% !important;
            padding: 0 1px !important; /* ULTRA TIGHT GAP for mobile */
        }
    }
    
    /* 2. Squish buttons to be narrower and continuous */
    .stButton > button {
        width: 100%;
        border-radius: 3px !important; 
        padding: 2px !important; 
        min-height: 32px !important;
        margin-bottom: -8px !important; /* Seamless stacking */
        font-size: 11px !important; 
        line-height: 1.1 !important;
        font-weight: 600 !important;
        border: none !important;
    }
    
    /* Custom button colors to match your mockup */
    /* Primary buttons (Cancel) */
    button[kind="primary"] {
        background-color: #ef4444 !important; 
        color: white !important;
    }
    
    /* Hide extra padding to save screen space */
    .block-container {
        padding-top: 1rem !important;
        padding-left: 0.2rem !important;
        padding-right: 0.2rem !important;
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
# 2. AUTHENTICATION & LOGIN SYSTEM
# ==========================================
if 'logged_in_user' not in st.session_state:
    st.session_state.logged_in_user = None
if 'logged_in_name' not in st.session_state:
    st.session_state.logged_in_name = None
if 'user_role' not in st.session_state:
    st.session_state.user_role = None

st.sidebar.title("🔐 Login / Register")

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
                st.sidebar.error("Please enter a valid email address.")
            elif len(display_name) < 2:
                st.sidebar.error("Please enter a display name.")
            else:
                role = 'admin' if email_input == OWNER_EMAIL else 'pending'
                new_user = pd.DataFrame([[email_input, display_name, password, role]], columns=['Email', 'Name', 'Password', 'Role'])
                save_users(pd.concat([users, new_user], ignore_index=True))
                st.sidebar.success("Account created! Please switch to Login above.")
                
    elif auth_mode == "Login":
        if st.sidebar.button("Login"):
            users = load_users()
            user_match = users[(users['Email'] == email_input) & (users['Password'] == password)]
            
            if not user_match.empty:
                role = user_match.iloc[0]['Role']
                if role == 'pending':
                    st.sidebar.error("Your account is waiting for Admin approval.")
                else:
                    st.session_state.logged_in_user = email_input
                    st.session_state.logged_in_name = user_match.iloc[0]['Name']
                    st.session_state.user_role = role
                    st.rerun()
            else:
                st.sidebar.error("Incorrect email or password.")
    st.stop()

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
# 4. THE BOOKING SYSTEM (Modern Optimized)
# ==========================================
# Use a custom HTML header for the modern title
st.markdown("<h1>RESERVE YOUR <span style='color: #10b981;'>TABLE</span></h1>", unsafe_allow_html=True)

HOURS = [f"{h:02d}:{m}" for h in range(8, 24) for m in ("00", "30")] 

# EXPANDED TO 14 DAYS
today = datetime.now().date()
upcoming_dates = [today + timedelta(days=i) for i in range(14)]
def get_date_label(d):
    if d == today: return "Today"
    if d == today + timedelta(days=1): return "Tomorrow"
    return d.strftime("%a, %b %d")

date_labels = [get_date_label(d) for d in upcoming_dates]

selected_date_label_main = st.radio("Select Date:", date_labels, horizontal=True, label_visibility="collapsed")
view_date = upcoming_dates[date_labels.index(selected_date_label_main)]

bookings_df = load_bookings()
bookings_df['Date'] = bookings_df['Date'].astype(str) 
relevant_bookings = bookings_df[bookings_df['Date'] == str(view_date)]

user_today_hours = relevant_bookings[relevant_bookings['User'] == st.session_state.logged_in_user]['Duration'].sum()

if st.session_state.user_role != 'admin':
    st.caption(f"**Your time today:** {user_today_hours} / 3.0h")

users_df = load_users()
name_lookup = dict(zip(users_df['Email'], users_df['Name']))

# 3 Columns for the tables (CSS forces these side-by-side on mobile)
cols = st.columns(3)

for i, col in enumerate(cols):
    t_name = f"Table {i+1}"
    col.markdown(f"### {t_name}")
    
    for time_str in HOURS:
        hour_int = int(time_str.split(":")[0])
        is_off_peak = hour_int < 10 or hour_int >= 22
        
        booked = relevant_bookings[(relevant_bookings['Table'] == t_name) & (relevant_bookings['Time'] == time_str)]
        button_key = f"{t_name}_{time_str}_{view_date}"
        
        if not booked.empty:
            booked_user_email = booked.iloc[0]['User']
            short_name = name_lookup.get(booked_user_email, str(booked_user_email).split('@')[0])
            
            # Formatting for taken slots
            if is_off_peak:
                btn_label = f"x {short_name.lower()}" if st.session_state.user_role == 'admin' or booked_user_email == st.session_state.logged_in_user else f"- {short_name.lower()}"
            else:
                btn_label = f"{time_str}\n❌ {short_name}" if st.session_state.user_role == 'admin' or booked_user_email == st.session_state.logged_in_user else f"{time_str}\n🔒 {short_name}"
            
            if st.session_state.user_role == 'admin' or booked_user_email == st.session_state.logged_in_user:
                if col.button(btn_label, key=f"del_{button_key}", type="primary"):
                    log_action("CANCELLED", st.session_state.logged_in_user, booked_user_email, f"{t_name} | {view_date} | {time_str}")
                    bookings_df = bookings_df[~((bookings_df['Table'] == t_name) & 
                                                (bookings_df['Time'] == time_str) & 
                                                (bookings_df['Date'] == str(view_date)))]
                    save_bookings(bookings_df)
                    st.rerun()
            else:
                col.button(btn_label, key=f"dis_{button_key}", disabled=True)
                
        else:
            # Formatting for FREE slots (Now styled green via Python injection to ensure it bypasses themes)
            btn_label = f"{time_str} free" if is_off_peak else f"{time_str}\n🟢 FREE"
            
            if col.button(btn_label, key=f"add_{button_key}"):
                if user_today_hours + 0.5 > 3.0 and st.session_state.user_role != 'admin':
                    st.error("Limit reached! (3h/day)")
                else:
                    log_action("BOOKED", st.session_state.logged_in_user, st.session_state.logged_in_user, f"{t_name} | {view_date} | {time_str}")
                    new_row = pd.DataFrame([[st.session_state.logged_in_user, str(view_date), t_name, time_str, 0.5]], 
                                           columns=['User', 'Date', 'Table', 'Time', 'Duration'])
                    bookings_df = pd.concat([bookings_df, new_row], ignore_index=True)
                    save_bookings(bookings_df)
                    st.rerun()

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
import streamlit.components.v1 as components

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
        padding-top: 2rem !important;
        padding-left: 0.5rem !important;
        padding-right: 0.5rem !important;
    }

    /* ---------------------------------------------------
       MAIN AREA: 2-ROW DATE RIBBON (Week 1 / Week 2)
       --------------------------------------------------- */
    section[data-testid="stMain"] [data-testid="stRadio"] > div[role="radiogroup"] {
        display: grid !important;
        grid-template-columns: max-content repeat(7, max-content) !important;
        grid-template-rows: auto auto !important;
        gap: 12px 8px !important; 
        padding: 10px 5px 15px 5px !important;
        border-bottom: 1px solid #dee2e6; 
        margin-bottom: 25px !important;
        overflow-x: auto !important; 
        -webkit-overflow-scrolling: touch; 
        scrollbar-width: none; 
        align-items: center;
        justify-content: center !important; 
    }
    section[data-testid="stMain"] [data-testid="stRadio"] > div[role="radiogroup"]::-webkit-scrollbar {
        display: none;
    }
    
    section[data-testid="stMain"] [data-testid="stRadio"] > div[role="radiogroup"]::before {
        content: "Week 1:"; grid-column: 1; grid-row: 1; font-weight: 500; color: #495057; font-size: 14px; padding-right: 5px;
    }
    section[data-testid="stMain"] [data-testid="stRadio"] > div[role="radiogroup"]::after {
        content: "Week 2:"; grid-column: 1; grid-row: 2; font-weight: 500; color: #495057; font-size: 14px; padding-right: 5px;
    }
    
    section[data-testid="stMain"] [data-testid="stRadio"] label:nth-of-type(1)  { grid-column: 2; grid-row: 1; }
    section[data-testid="stMain"] [data-testid="stRadio"] label:nth-of-type(2)  { grid-column: 3; grid-row: 1; }
    section[data-testid="stMain"] [data-testid="stRadio"] label:nth-of-type(3)  { grid-column: 4; grid-row: 1; }
    section[data-testid="stMain"] [data-testid="stRadio"] label:nth-of-type(4)  { grid-column: 5; grid-row: 1; }
    section[data-testid="stMain"] [data-testid="stRadio"] label:nth-of-type(5)  { grid-column: 6; grid-row: 1; }
    section[data-testid="stMain"] [data-testid="stRadio"] label:nth-of-type(6)  { grid-column: 7; grid-row: 1; }
    section[data-testid="stMain"] [data-testid="stRadio"] label:nth-of-type(7)  { grid-column: 8; grid-row: 1; }
    
    section[data-testid="stMain"] [data-testid="stRadio"] label:nth-of-type(8)  { grid-column: 2; grid-row: 2; }
    section[data-testid="stMain"] [data-testid="stRadio"] label:nth-of-type(9)  { grid-column: 3; grid-row: 2; }
    section[data-testid="stMain"] [data-testid="stRadio"] label:nth-of-type(10) { grid-column: 4; grid-row: 2; }
    section[data-testid="stMain"] [data-testid="stRadio"] label:nth-of-type(11) { grid-column: 5; grid-row: 2; }
    section[data-testid="stMain"] [data-testid="stRadio"] label:nth-of-type(12) { grid-column: 6; grid-row: 2; }
    section[data-testid="stMain"] [data-testid="stRadio"] label:nth-of-type(13) { grid-column: 7; grid-row: 2; }
    section[data-testid="stMain"] [data-testid="stRadio"] label:nth-of-type(14) { grid-column: 8; grid-row: 2; }

    section[data-testid="stMain"] [data-testid="stRadio"] label {
        background-color: #ffffff !important;
        border: 1px solid #ced4da !important;
        border-radius: 6px !important;
        padding: 6px 12px !important;
        min-width: max-content; 
        cursor: pointer;
        margin: 0 !important; 
    }
    
    section[data-testid="stMain"] [data-testid="stRadio"] label[data-checked="true"] {
        background-color: #007bff !important; border-color: #007bff !important;
    }
    section[data-testid="stMain"] [data-testid="stRadio"] label[data-checked="true"] p { color: #ffffff !important; }
    
    div[role="radiogroup"] div[role="radio"] > div:first-child { display: none !important; }

    /* ---------------------------------------------------
       MAIN AREA: TABLES & STICKY HEADERS
       --------------------------------------------------- */
    [data-testid="stHorizontalBlock"] { gap: 15px !important; justify-content: center !important; }
    [data-testid="column"] { display: flex !important; flex-direction: column !important; padding: 0 !important; }

    /* MAGIC STICKY HEADER FIX */
    .table-header {
        position: sticky;       
        top: 2.875rem;          
        z-index: 990;           
        text-align: center !important;
        font-size: 15px !important;
        font-weight: 700 !important;
        letter-spacing: 1px !important;
        text-transform: uppercase !important;
        color: #ffffff !important; 
        background-color: #495057 !important; 
        padding: 10px 0;
        border-radius: 6px !important;
        margin-bottom: 12px !important; 
        box-shadow: 0 4px 6px rgba(0,0,0,0.3); 
    }

    /* Base button structural styles */
    [data-testid="column"] .stButton > button {
        width: 100% !important;
        border-radius: 4px !important; 
        padding: 6px 2px !important; 
        min-height: 44px !important; 
        margin-bottom: 4px !important; 
        font-size: 13px !important; 
        line-height: 1.2 !important;
        text-align: center !important; 
        background-color: #ffffff !important; 
        transition: all 0.2s ease;
    }
    
    /* Hour Banding Background stripes */
    [data-testid="column"] > div:nth-child(4n) button, [data-testid="column"] > div:nth-child(4n+1) button {
        background-color: #f1f3f5 !important; 
    }
    [data-testid="column"] .stButton > button:hover {
        background-color: #e6f4ea !important; 
    }
    
    /* Active User / Admin Clickable Slot (Solid Red) */
    [data-testid="column"] button[kind="primary"] {
        background-color: #ff4b4b !important; 
    }
    [data-testid="column"] button[kind="primary"] p {
        color: #ffffff !important; 
        font-weight: 500 !important;
    }
    
    /* HEAVY OCCUPIED LOOK FOR LOCKED SLOTS (Red Text + Light Red BG) */
    [data-testid="column"] button:disabled {
        background-color: #fff5f5 !important; /* Pale Red */
        opacity: 1 !important; /* Removes default fade */
    }
    [data-testid="column"] button:disabled p {
        color: #dc3545 !important; /* Bright Red Text & Icon */
        font-weight: 700 !important;
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 1.5 DYNAMIC "PRIME TIME" HEATMAP BORDERS (RED)
# ==========================================
HOURS = [f"{h:02d}:{m}" for h in range(8, 24) for m in ("00", "30")] 
prime_time_css = "<style>\n"

for idx, time_str in enumerate(HOURS):
    hour = int(time_str[:2])
    minute = int(time_str[3:])
    time_float = hour + minute / 60.0
    
    # Calculate distance from 19:00
    dist = abs(time_float - 19.0)
    
    # Intensity: 1.0 at 19:00, approaches 0 at off-hours
    intensity = max(0.0, 1.0 - (dist / 10.0))
    
    # Color fades from Light Gray rgb(222,226,230) to Theme Red rgb(220,53,69)
    r = int(222 - (222 - 220) * intensity)
    g = int(226 - (226 - 53) * intensity)
    b = int(230 - (230 - 69) * intensity)
    
    # Border thickens slightly as it gets closer to prime time (1px to 3px)
    border_width = 1 + int(2 * intensity)
    
    child_idx = idx + 2 # +2 because child 1 is the Table Header
    
    prime_time_css += f'[data-testid="column"] > div:nth-child({child_idx}) button {{\n'
    prime_time_css += f'    border: {border_width}px solid rgb({r}, {g}, {b}) !important;\n'
    prime_time_css += f'}}\n'

prime_time_css += "</style>"
st.markdown(prime_time_css, unsafe_allow_html=True)


# ==========================================
# 2. DATABASE & LOGGING SETUP
# ==========================================
USERS_FILE, BOOKINGS_FILE, AUDIT_FILE = 'users.csv', 'bookings.csv', 'audit.csv'
OWNER_EMAIL = "tomazbratina@gmail.com" 

if not os.path.exists(USERS_FILE): pd.DataFrame(columns=['Email', 'Name', 'Password', 'Role']).to_csv(USERS_FILE, index=False)
if not os.path.exists(BOOKINGS_FILE): pd.DataFrame(columns=['User', 'Date', 'Table', 'Time', 'Duration']).to_csv(BOOKINGS_FILE, index=False)
if not os.path.exists(AUDIT_FILE): pd.DataFrame(columns=['Timestamp', 'Action', 'Performed_By', 'Target_User', 'Details']).to_csv(AUDIT_FILE, index=False)

def load_users(): 
    try: return pd.read_csv(USERS_FILE)
    except: return pd.DataFrame(columns=['Email', 'Name', 'Password', 'Role'])

def save_users(df): df.to_csv(USERS_FILE, index=False)
def load_bookings(): return pd.read_csv(BOOKINGS_FILE)
def save_bookings(df): df.to_csv(BOOKINGS_FILE, index=False)
def log_action(action, performed_by, target_user, details):
    audit_df = pd.read_csv(AUDIT_FILE)
    new_log = pd.DataFrame([[datetime.now().strftime("%Y-%m-%d %H:%M:%S"), action, performed_by, target_user, details]], columns=['Timestamp', 'Action', 'Performed_By', 'Target_User', 'Details'])
    pd.concat([audit_df, new_log], ignore_index=True).to_csv(AUDIT_FILE, index=False)


# ==========================================
# 3. AUTHENTICATION & STATE MANAGEMENT
# ==========================================
if 'logged_in_user' not in st.session_state: st.session_state.logged_in_user = None
if 'logged_in_name' not in st.session_state: st.session_state.logged_in_name = None
if 'user_role' not in st.session_state: st.session_state.user_role = None

st.sidebar.markdown("<h2>🔐 Access</h2>", unsafe_allow_html=True)

if st.session_state.logged_in_user is None:
    auth_mode = st.sidebar.radio("Choose Action", ["Login", "Register"])
    email_input = st.sidebar.text_input("Email Address").strip().lower()
    display_name = st.sidebar.text_input("Display Name (e.g. Tomi)").strip() if auth_mode == "Register" else ""
    password = st.sidebar.text_input("Password", type="password")
    
    if st.sidebar.button("Go", type="primary", use_container_width=True):
        users = load_users()
        if auth_mode == "Register":
            if email_input in users['Email'].values: st.sidebar.error("Email already exists!")
            elif len(email_input) < 5 or "@" not in email_input: st.sidebar.error("Valid email required.")
            elif len(display_name) < 2: st.sidebar.error("Display name required.")
            else:
                role = 'admin' if email_input == OWNER_EMAIL else 'pending'
                new_user = pd.DataFrame([[email_input, display_name, password, role]], columns=['Email', 'Name', 'Password', 'Role'])
                save_users(pd.concat([users, new_user], ignore_index=True))
                st.sidebar.success("Account created! Switch to Login.")
        else:
            user_match = users[(users['Email'] == email_input) & (users['Password'] == password)]
            if not user_match.empty:
                st.session_state.logged_in_user = email_input
                st.session_state.logged_in_name = user_match.iloc[0]['Name']
                st.session_state.user_role = user_match.iloc[0]['Role']
                st.rerun()
            else: st.sidebar.error("Incorrect email/password.")
                
    st.markdown("<h1>RESERVE TABLE</h1>", unsafe_allow_html=True)
    st.info("👈 Please use the sidebar menu to log in or register to view the schedule.")
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
# 4. ADMIN DASHBOARD
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
                st.session_state.logged_in_name = edited_users[edited_users['Email'] == st.session_state.logged_in_user].iloc[0]['Name']
            st.success("Database updated successfully!")

    with tab2: st.dataframe(load_bookings(), use_container_width=True)
    with tab3: st.dataframe(pd.read_csv(AUDIT_FILE) if st.session_state.logged_in_user == OWNER_EMAIL else "⛔ Access Denied", use_container_width=True)
    st.stop()


# ==========================================
# 5. POPUP DIALOG WINDOWS (Centered over screen)
# ==========================================

@st.dialog("⚙️ Admin Control")
def admin_modal(table, time, date, current_user, display_name):
    st.write(f"**Slot:** {table} at {time}")
    new_name = st.text_input("Edit Player Name:", value=display_name)
    
    c1, c2 = st.columns(2)
    if c1.button("💾 Save Name", type="primary", use_container_width=True):
        df = load_bookings()
        df.loc[(df['Table'] == table) & (df['Time'] == time) & (df['Date'] == str(date)), 'User'] = new_name 
        save_bookings(df)
        log_action("EDITED", st.session_state.logged_in_user, current_user, f"{table} | {time} | New Name: {new_name}")
        st.rerun()
        
    if c2.button("🗑️ Free Slot", use_container_width=True):
        df = load_bookings()
        df = df[~((df['Table'] == table) & (df['Time'] == time) & (df['Date'] == str(date)))]
        save_bookings(df)
        log_action("CANCELLED", st.session_state.logged_in_user, current_user, f"{table} | {date} | {time}")
        st.rerun()

@st.dialog("❌ Cancel Booking")
def user_cancel_modal(table, time, date):
    st.write(f"Are you sure you want to cancel your reservation for **{table}** at **{time}**?")
    c1, c2 = st.columns(2)
    if c1.button("Yes, Cancel", type="primary", use_container_width=True):
        df = load_bookings()
        df = df[~((df['Table'] == table) & (df['Time'] == time) & (df['Date'] == str(date)))]
        save_bookings(df)
        log_action("CANCELLED", st.session_state.logged_in_user, st.session_state.logged_in_user, f"{table} | {date} | {time}")
        st.rerun()
    if c2.button("No, Keep it", use_container_width=True):
        st.rerun()

@st.dialog("🟢 Book Table")
def book_modal(table, time, date, current_hours):
    st.write(f"Reserve **{table}** at **{time}**?")
    c1, c2 = st.columns(2)
    if c1.button("Confirm", type="primary", use_container_width=True):
        if current_hours + 0.5 > 3.0 and st.session_state.user_role != 'admin':
            st.error("Limit reached! (3h/day)")
        else:
            df = load_bookings()
            new_row = pd.DataFrame([[st.session_state.logged_in_user, str(date), table, time, 0.5]], columns=['User', 'Date', 'Table', 'Time', 'Duration'])
            save_bookings(pd.concat([df, new_row], ignore_index=True))
            log_action("BOOKED", st.session_state.logged_in_user, st.session_state.logged_in_user, f"{table} | {date} | {time}")
            st.rerun()
    if c2.button("Cancel", use_container_width=True):
        st.rerun()


# ==========================================
# 6. THE BOOKING SYSTEM
# ==========================================
st.markdown("<h1>RESERVE <span style='color: #dc3545;'>TABLE</span></h1>", unsafe_allow_html=True)

today = datetime.now().date()
upcoming_dates = [today + timedelta(days=i) for i in range(14)]
date_labels = ["Today" if d == today else "Tomorrow" if d == today + timedelta(days=1) else d.strftime("%a %d") for d in upcoming_dates]

selected_date_label_main = st.radio("Select Date:", date_labels, horizontal=True, label_visibility="collapsed")
view_date = upcoming_dates[date_labels.index(selected_date_label_main)]

bookings_df = load_bookings()
relevant_bookings = bookings_df[bookings_df['Date'] == str(view_date)]
user_today_hours = relevant_bookings[relevant_bookings['User'] == st.session_state.logged_in_user]['Duration'].sum()

if st.session_state.user_role != 'admin':
    st.caption(f"<div style='text-align:center;'>**Your booked time:** {user_today_hours} / 3.0h</div>", unsafe_allow_html=True)

users_df = load_users()
name_lookup = dict(zip(users_df['Email'], users_df['Name']))

# --- THE GRID ---
cols = st.columns(3)

for i, col in enumerate(cols):
    t_name = f"Table {i+1}"
    col.markdown(f"<div class='table-header'>Tbl {i+1}</div>", unsafe_allow_html=True)
    
    for time_str in HOURS:
        booked = relevant_bookings[(relevant_bookings['Table'] == f"Table {i+1}") & (relevant_bookings['Time'] == time_str)]
        button_key = f"T{i+1}_{time_str}_{view_date}"
        
        if not booked.empty:
            booked_user_email = booked.iloc[0]['User']
            short_name = name_lookup.get(booked_user_email, str(booked_user_email).split('@')[0]) if "@" in str(booked_user_email) else booked_user_email
            
            if st.session_state.user_role == 'admin':
                if col.button(f"{time_str} 🔴 {short_name}", key=f"admin_{button_key}", type="primary", use_container_width=True):
                    admin_modal(f"Table {i+1}", time_str, view_date, booked_user_email, short_name)
                    
            elif booked_user_email == st.session_state.logged_in_user:
                if col.button(f"{time_str} ❌ {short_name}", key=f"del_{button_key}", type="primary", use_container_width=True):
                    user_cancel_modal(f"Table {i+1}", time_str, view_date)
            else:
                col.button(f"{time_str} 🔒 {short_name}", key=f"dis_{button_key}", disabled=True, use_container_width=True)
                
        else:
            if col.button(f"{time_str} 🟢 FREE", key=f"add_{button_key}", use_container_width=True):
                book_modal(f"Table {i+1}", time_str, view_date, user_today_hours)

# ==========================================
# 7. AUTO-SCROLL TO PRIME TIME SCRIPT (Gated)
# ==========================================
# This prevents the page from ripping away when a modal opens!
# It only scrolls when you change the date.
if 'scroll_trigger_date' not in st.session_state:
    st.session_state.scroll_trigger_date = None

if st.session_state.scroll_trigger_date != view_date:
    st.session_state.scroll_trigger_date = view_date
    components.html(
        """
        <script>
        setTimeout(function() {
            const buttons = window.parent.document.querySelectorAll('button');
            for (let btn of buttons) {
                if (btn.innerText.includes('19:00')) {
                    btn.scrollIntoView({behavior: 'smooth', block: 'center'});
                    break;
                }
            }
        }, 800); 
        </script>
        """,
        height=0
    )

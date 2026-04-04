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
# 1. DYNAMIC BACKGROUND COLORS & ALIGNMENT ENGINE
# ==========================================
HOURS = [f"{h:02d}:{m}" for h in range(8, 24) for m in ("00", "30")] 

# 4-Row (2-Hour) Color Blocks (Background, Border, Text)
BLOCK_STYLES = [
    {"bg": "#fff9c4", "border": "#fbc02d", "text": "#495057"}, # 08-09 Pale Yellow
    {"bg": "#e3f2fd", "border": "#64b5f6", "text": "#495057"}, # 10-11 Pale Blue
    {"bg": "#e8f5e9", "border": "#81c784", "text": "#495057"}, # 12-13 Pale Green
    {"bg": "#ffebee", "border": "#e57373", "text": "#495057"}, # 14-15 Pale Red
    {"bg": "#f3e5f5", "border": "#ba68c8", "text": "#495057"}, # 16-17 Pale Purple
    {"bg": "#ff9800", "border": "#e65100", "text": "#ffffff"}, # 18-19 VIBRANT ORANGE (PRIME)
    {"bg": "#00bfa5", "border": "#004d40", "text": "#ffffff"}, # 20-21 VIBRANT TEAL (PRIME)
    {"bg": "#efebe9", "border": "#a1887f", "text": "#495057"}  # 22-23 Pale Brown
]

dynamic_css = "<style>\n"
mobile_css = "@media (max-width: 900px) {\n" 

for idx, time_str in enumerate(HOURS):
    hour = int(time_str[:2])
    is_prime = 18 <= hour <= 22
    
    # Get styles for this specific 4-row block
    style = BLOCK_STYLES[idx // 4]
    
    child_idx = idx + 3 # 1: Header, 2: Image/Placeholder, 3+: Buttons
    
    if is_prime:
        # 🔥 EXPLOSIVE PRIME TIME
        height = "42px" 
        font_size = "14px"
        font_weight = "800"
        shadow = "0px 4px 8px rgba(0,0,0,0.3)"
        
        m_height = "34px" 
        m_font_size = "10px" 
    else:
        # 🌙 TINY OFF-HOURS
        height = "28px"
        font_size = "11px"
        font_weight = "500"
        shadow = "none"
        
        m_height = "24px" 
        m_font_size = "8px" 

    # --- DESKTOP ---
    # Lock the exact height of Streamlit's invisible wrapper to guarantee row alignment
    dynamic_css += f'[data-testid="stMain"] div[data-testid="column"] > div:nth-child({child_idx}) {{\n'
    dynamic_css += f'    height: {height} !important;\n'
    dynamic_css += f'    min-height: {height} !important;\n'
    dynamic_css += f'    max-height: {height} !important;\n'
    dynamic_css += f'    margin-bottom: 6px !important;\n'
    dynamic_css += f'}}\n'
    
    dynamic_css += f'[data-testid="stMain"] div[data-testid="column"] > div:nth-child({child_idx}) button {{\n'
    dynamic_css += f'    background-color: {style["bg"]} !important;\n'
    dynamic_css += f'    border: 2px solid {style["border"]} !important;\n'
    dynamic_css += f'    box-shadow: {shadow} !important;\n'
    dynamic_css += f'}}\n'
    
    dynamic_css += f'[data-testid="stMain"] div[data-testid="column"] > div:nth-child({child_idx}) button p {{\n'
    dynamic_css += f'    font-size: {font_size} !important;\n'
    dynamic_css += f'    font-weight: {font_weight} !important;\n'
    dynamic_css += f'    color: {style["text"]} !important;\n'
    dynamic_css += f'}}\n'

    # --- MOBILE ---
    mobile_css += f'[data-testid="stMain"] div[data-testid="column"] > div:nth-child({child_idx}) {{\n'
    mobile_css += f'    height: {m_height} !important;\n'
    mobile_css += f'    min-height: {m_height} !important;\n'
    mobile_css += f'    max-height: {m_height} !important;\n'
    mobile_css += f'    margin-bottom: 4px !important;\n'
    mobile_css += f'}}\n'
    mobile_css += f'[data-testid="stMain"] div[data-testid="column"] > div:nth-child({child_idx}) button p {{\n'
    mobile_css += f'    font-size: {m_font_size} !important;\n'
    mobile_css += f'}}\n'

mobile_css += "}\n</style>"
dynamic_css += mobile_css
st.markdown(dynamic_css, unsafe_allow_html=True)


# ==========================================
# 1.5 GENERIC CSS & ANTI-STRETCH BUTTON LOGIC
# ==========================================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500;700&display=swap');

    html, body, [class*="css"] { font-family: 'Roboto', sans-serif !important; font-weight: 300 !important; }
    h1, h2, h3, h4 { font-family: 'Roboto', sans-serif !important; font-weight: 500 !important; text-align: center; }

    .block-container {
        max-width: 800px !important; 
        margin: 0 auto !important;
        padding-top: 1.5rem !important;
        padding-left: 0.5rem !important;
        padding-right: 0.5rem !important;
    }

    /* DATE RIBBON */
    [data-testid="stMain"] div[role="radiogroup"] {
        display: grid !important;
        grid-template-columns: max-content repeat(7, max-content) !important;
        grid-template-rows: auto auto !important;
        gap: 8px 6px !important; 
        padding: 5px !important;
        border-bottom: 1px solid #dee2e6; 
        margin-bottom: 15px !important;
        overflow-x: auto !important; 
        -webkit-overflow-scrolling: touch; 
        scrollbar-width: none; 
        align-items: center;
        justify-content: flex-start !important; 
    }
    [data-testid="stMain"] div[role="radiogroup"]::-webkit-scrollbar { display: none; }
    [data-testid="stMain"] div[role="radiogroup"]::before { content: "Week 1:"; grid-column: 1; grid-row: 1; font-weight: 500; color: #495057; font-size: 12px; padding-right: 5px; }
    [data-testid="stMain"] div[role="radiogroup"]::after { content: "Week 2:"; grid-column: 1; grid-row: 2; font-weight: 500; color: #495057; font-size: 12px; padding-right: 5px; }
    
    [data-testid="stMain"] div[role="radiogroup"] label:nth-of-type(1)  { grid-column: 2; grid-row: 1; }
    [data-testid="stMain"] div[role="radiogroup"] label:nth-of-type(2)  { grid-column: 3; grid-row: 1; }
    [data-testid="stMain"] div[role="radiogroup"] label:nth-of-type(3)  { grid-column: 4; grid-row: 1; }
    [data-testid="stMain"] div[role="radiogroup"] label:nth-of-type(4)  { grid-column: 5; grid-row: 1; }
    [data-testid="stMain"] div[role="radiogroup"] label:nth-of-type(5)  { grid-column: 6; grid-row: 1; }
    [data-testid="stMain"] div[role="radiogroup"] label:nth-of-type(6)  { grid-column: 7; grid-row: 1; }
    [data-testid="stMain"] div[role="radiogroup"] label:nth-of-type(7)  { grid-column: 8; grid-row: 1; }
    [data-testid="stMain"] div[role="radiogroup"] label:nth-of-type(8)  { grid-column: 2; grid-row: 2; }
    [data-testid="stMain"] div[role="radiogroup"] label:nth-of-type(9)  { grid-column: 3; grid-row: 2; }
    [data-testid="stMain"] div[role="radiogroup"] label:nth-of-type(10) { grid-column: 4; grid-row: 2; }
    [data-testid="stMain"] div[role="radiogroup"] label:nth-of-type(11) { grid-column: 5; grid-row: 2; }
    [data-testid="stMain"] div[role="radiogroup"] label:nth-of-type(12) { grid-column: 6; grid-row: 2; }
    [data-testid="stMain"] div[role="radiogroup"] label:nth-of-type(13) { grid-column: 7; grid-row: 2; }
    [data-testid="stMain"] div[role="radiogroup"] label:nth-of-type(14) { grid-column: 8; grid-row: 2; }

    [data-testid="stMain"] div[role="radiogroup"] label {
        background-color: #ffffff !important; border: 1px solid #ced4da !important; border-radius: 4px !important;
        padding: 4px 8px !important; min-width: max-content; cursor: pointer; margin: 0 !important; 
    }
    [data-testid="stMain"] div[role="radiogroup"] label[data-checked="true"] { background-color: #007bff !important; border-color: #007bff !important; }
    [data-testid="stMain"] div[role="radiogroup"] label[data-checked="true"] p { color: #ffffff !important; }
    [data-testid="stMain"] div[role="radiogroup"] div[role="radio"] > div:first-child { display: none !important; }

    /* TABLES & HEADERS */
    [data-testid="stMain"] div[data-testid="stHorizontalBlock"], [data-testid="stMain"] div.stColumns { 
        gap: 10px !important; justify-content: center !important; 
    }
    [data-testid="stMain"] div[data-testid="column"] { 
        display: flex !important; flex-direction: column !important; padding: 0 !important; 
    }

    [data-testid="stMain"] .table-header {
        position: sticky;       
        top: 2.875rem;          
        z-index: 990;           
        text-align: center !important;
        font-size: 14px !important;
        font-weight: 700 !important;
        text-transform: uppercase !important;
        color: #ffffff !important; 
        background-color: #212529 !important; 
        padding: 6px 0;
        border-radius: 4px !important;
        margin-bottom: 4px !important; 
        box-shadow: 0 2px 4px rgba(0,0,0,0.4); 
    }

    [data-testid="stMain"] [data-testid="stImage"] { margin-bottom: 4px !important; border-radius: 4px; overflow: hidden; }

    /* ---------------------------------------------------
       PERFECT ROW ALIGNMENT CSS 
       --------------------------------------------------- */
    [data-testid="stMain"] div[data-testid="column"] .stButton {
        height: 100% !important;
        width: 100% !important;
        margin: 0 !important;
        padding: 0 !important;
    }
    
    [data-testid="stMain"] div[data-testid="column"] .stButton > button {
        height: 100% !important; 
        width: 100% !important; 
        border-radius: 4px !important; 
        margin: 0 !important; 
        padding: 0 2px !important;
        display: flex !important; 
        align-items: center !important; 
        justify-content: center !important;
        transition: none !important; /* ZERO TRANSITIONS */
        animation: none !important;
    }
    
    [data-testid="stMain"] div[data-testid="column"] .stButton > button p {
        white-space: nowrap !important; /* ABSOLUTELY BANS TEXT WRAPPING */
        overflow: hidden !important;    
        text-overflow: ellipsis !important; 
        width: 100% !important;
        margin: 0 !important;
    }
    
    /* OVERRIDES: Active and Disabled Slots */
    [data-testid="stMain"] div[data-testid="column"] button[kind="primary"] { 
        background-color: #dc3545 !important; 
        border: 2px solid #bd2130 !important;
        box-shadow: inset 0 0 5px rgba(0,0,0,0.2) !important;
    }
    [data-testid="stMain"] div[data-testid="column"] button[kind="primary"] p { 
        color: #ffffff !important; font-weight: 700 !important; 
    }
    
    [data-testid="stMain"] div[data-testid="column"] button[disabled] { 
        background-color: #ffe5e5 !important; 
        border: 1px solid #dc3545 !important;
        opacity: 1 !important; box-shadow: none !important;
    }
    [data-testid="stMain"] div[data-testid="column"] button[disabled] p { 
        color: #dc3545 !important; font-weight: 700 !important; 
    }

    /* ---------------------------------------------------
       📱 100% FORCED 3-COLUMN MOBILE LAYOUT 
       --------------------------------------------------- */
    @media (max-width: 900px) {
        .block-container {
            padding-left: 2px !important;
            padding-right: 2px !important;
        }

        [data-testid="stMain"] div[data-testid="stHorizontalBlock"] {
            display: flex !important; 
            flex-direction: row !important; /* FORCE SIDE BY SIDE */
            flex-wrap: nowrap !important;   /* BAN STACKING */
            width: 100% !important;
            padding: 0 !important; 
            margin: 0 !important;
            justify-content: space-between !important; 
            gap: 2px !important; 
            overflow: hidden !important; 
        }
        
        [data-testid="stMain"] div[data-testid="column"] {
            min-width: 0 !important; /* ALLOWS COLUMNS TO SHRINK */
            width: calc(33.33% - 2px) !important; 
            flex: 1 1 0 !important; 
            margin: 0 !important;
            padding: 0 !important;
            display: flex !important;
            flex-direction: column !important;
            overflow: hidden !important;
        }

        [data-testid="stMain"] .table-header { 
            font-size: 11px !important; 
            padding: 2px 0 !important; 
            margin-bottom: 2px !important;
        }
    }
</style>
""", unsafe_allow_html=True)


# ==========================================
# 2. DATABASE & ARCHIVE SYSTEM
# ==========================================
USERS_FILE, BOOKINGS_FILE, AUDIT_FILE = 'users.csv', 'bookings.csv', 'audit.csv'
HISTORY_FILE = 'history.csv'
OWNER_EMAIL = "tomazbratina@gmail.com" 

if not os.path.exists(USERS_FILE): pd.DataFrame(columns=['Email', 'Name', 'Password', 'Role', 'Max_Hours_Day']).to_csv(USERS_FILE, index=False)
if not os.path.exists(BOOKINGS_FILE): pd.DataFrame(columns=['User', 'Date', 'Table', 'Time', 'Duration']).to_csv(BOOKINGS_FILE, index=False)
if not os.path.exists(AUDIT_FILE): pd.DataFrame(columns=['Timestamp', 'Action', 'Performed_By', 'Target_User', 'Details']).to_csv(AUDIT_FILE, index=False)
if not os.path.exists(HISTORY_FILE): pd.DataFrame(columns=['User', 'Date', 'Table', 'Time', 'Duration']).to_csv(HISTORY_FILE, index=False)

def archive_old_bookings():
    try:
        df = pd.read_csv(BOOKINGS_FILE)
        if df.empty: return
        df['DateObj'] = pd.to_datetime(df['Date'], errors='coerce').dt.date
        today = datetime.now().date()
        past_bookings = df[df['DateObj'] < today].copy()
        active_bookings = df[df['DateObj'] >= today].copy()
        if not past_bookings.empty:
            past_bookings = past_bookings.drop(columns=['DateObj'])
            active_bookings = active_bookings.drop(columns=['DateObj'])
            history_df = pd.read_csv(HISTORY_FILE)
            history_df = pd.concat([history_df, past_bookings], ignore_index=True)
            history_df.to_csv(HISTORY_FILE, index=False)
            active_bookings.to_csv(BOOKINGS_FILE, index=False)
    except: pass 

archive_old_bookings()

def load_users(): 
    try: 
        df = pd.read_csv(USERS_FILE)
        if 'Max_Hours_Day' not in df.columns:
            df['Max_Hours_Day'] = 3.0
            df.to_csv(USERS_FILE, index=False)
        return df
    except: 
        return pd.DataFrame(columns=['Email', 'Name', 'Password', 'Role', 'Max_Hours_Day'])

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
                new_user = pd.DataFrame([[email_input, display_name, password, role, 3.0]], columns=['Email', 'Name', 'Password', 'Role', 'Max_Hours_Day'])
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
    tab1, tab2, tab3, tab4 = st.tabs(["👥 Users", "📊 Active Database", "🕰️ History (Archive)", "🕵️‍♂️ Audit Log"])
    
    with tab1:
        st.write("### Manage Users")
        users_df = load_users()
        edited_users = st.data_editor(
            users_df,
            column_config={
                "Role": st.column_config.SelectboxColumn("User Role", options=["pending", "user", "admin"], required=True),
                "Name": st.column_config.TextColumn("Display Name"), 
                "Email": st.column_config.TextColumn("Email Address", disabled=False), 
                "Password": st.column_config.TextColumn("Password", disabled=False),
                "Max_Hours_Day": st.column_config.NumberColumn("Daily Max (Hours)", min_value=0.5, max_value=24.0, step=0.5)
            },
            num_rows="dynamic",
            hide_index=True, use_container_width=True
        )
        if st.button("💾 Save User Changes", type="primary"):
            save_users(edited_users)
            if st.session_state.logged_in_user in edited_users['Email'].values:
                st.session_state.logged_in_name = edited_users[edited_users['Email'] == st.session_state.logged_in_user].iloc[0]['Name']
            st.success("Database updated successfully!")

    with tab2: 
        st.write("### Current Future Bookings")
        st.dataframe(load_bookings(), use_container_width=True)
        
    with tab3:

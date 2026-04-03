import os

# ==========================================
# 0. THE "KILL DARK MODE" SCRIPT
# ==========================================
if not os.path.exists('.streamlit'):
    os.makedirs('.streamlit)
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
# 1. DYNAMIC "PRIME TIME" HEATMAP & SIZING ENGINE
# ==========================================
# This first dynamic block sets the standard formatting, which will be
# overridden for special user/admin states in the main CSS block below.
HOURS = [f"{h:02d}:{m}" for h in range(8, 24) for m in ("00", "30")] 
dynamic_css = "<style>\n"

for idx, time_str in enumerate(HOURS):
    hour = int(time_str[:2])
    minute = int(time_str[3:])
    time_float = hour + minute / 60.0
    
    # Peak intensity distance from 19:30
    dist = abs(time_float - 19.5)
    
    # Calculate visual weight intensity (fades from off-peak to peak)
    intensity = max(0.0, 1.0 - (dist / 11.5))
    
    # Define Prime Time (18:00 to 22:00) for binary size/text styling
    is_prime = 18 <= hour <= 22
    
    if is_prime:
        # FLASHY PRIME TIME SETTINGS: Larger font, bold text, fading Gold-to-Red border
        bg_color = "#ffffff" if hour % 2 == 0 else "#fffde7" # Crisp White / Pale Warm Yellow
        font_size = "16px"
        font_weight = "700"
        padding = "10px 2px" # Taller buttons
        
        # Color math: Fades from Gold (255,193,7) to Theme Red (220,53,69)
        r = int(255 - (255 - 220) * intensity)
        g = int(193 - (193 - 53) * intensity)
        b = int(7 - (7 - 69) * intensity)
        border = f"3px solid rgb({r}, {g}, {b})"
    else:
        # DIM OFF-HOURS SETTINGS: Small font, faded text, thin gray border
        bg_color = "#f8f9fa" if hour % 2 == 0 else "#e9ecef"
        font_size = "11px"
        font_weight = "400"
        padding = "4px 2px"
        
        # Muted Gray Border (fades from light to darker gray)
        gray = int(222 - (50 * intensity))
        border = f"1px solid rgb({gray}, {gray}, {gray})"

    # +3 Because in the column we have: 1. Header, 2. Image, 3. The first button
    child_idx = idx + 3 
    
    # Apply standard settings (background, border, height) to the button container
    dynamic_css += f'[data-testid="column"] > div:nth-child({child_idx}) button {{\n'
    dynamic_css += f'    border: {border} !important;\n'
    dynamic_css += f'    background-color: {bg_color} !important;\n'
    dynamic_css += f'    padding: {padding} !important;\n'
    dynamic_css += f'}}\n'
    
    # Apply typography (font size, font weight) to the text inside the button
    dynamic_css += f'[data-testid="column"] > div:nth-child({child_idx}) button p {{\n'
    dynamic_css += f'    font-size: {font_size} !important;\n'
    dynamic_css += f'    font-weight: {font_weight} !important;\n'
    dynamic_css += f'}}\n'

dynamic_css += "</style>"
st.markdown(dynamic_css, unsafe_allow_html=True)


# ==========================================
# 1.5 CLEAN STRUCTURAL CSS
# ==========================================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500;700&display=swap');

    html, body, [class*="css"] { font-family: 'Roboto', sans-serif !important; font-weight: 300 !important; }
    h1, h2, h3, h4 { font-family: 'Roboto', sans-serif !important; font-weight: 500 !important; text-align: center; }

    .block-container {
        max-width: 750px !important; 
        margin: 0 auto !important;
        padding-top: 2rem !important;
        padding-left: 0.5rem !important;
        padding-right: 0.5rem !important;
    }

    /* ---------------------------------------------------
       MAIN AREA: 2-ROW DATE RIBBON
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
    section[data-testid="stMain"] [data-testid="stRadio"] > div[role="radiogroup"]::-webkit-scrollbar { display: none; }
    
    section[data-testid="stMain"] [data-testid="stRadio"] > div[role="radiogroup"]::before { content: "Week 1:"; grid-column: 1; grid-row: 1; font-weight: 500; color: #495057; font-size: 14px; padding-right: 5px; }
    section[data-testid="stMain"] [data-testid="stRadio"] > div[role="radiogroup"]::after { content: "Week 2:"; grid-column: 1; grid-row: 2; font-weight: 500; color: #495057; font-size: 14px; padding-right: 5px; }
    
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
        background-color: #ffffff !important; border: 1px solid #ced4da !important; border-radius: 6px !important;
        padding: 6px 12px !important; min-width: max-content; cursor: pointer; margin: 0 !important; 
    }
    
    section[data-testid="stMain"] [data-testid="stRadio"] label[data-checked="true"] { background-color: #007bff !important; border-color: #007bff !important; }
    section[data-testid="stMain"] [data-testid="stRadio"] label[data-checked="true"] p { color: #ffffff !important; }
    div[role="radiogroup"] div[role="radio"] > div:first-child { display: none !important; }

    /* ---------------------------------------------------
       MAIN AREA: TABLES & STICKY HEADERS
       --------------------------------------------------- */
    [data-testid="stHorizontalBlock"] { gap: 15px !important; justify-content: center !important; }
    [data-testid="column"] { display: flex !important; flex-direction: column !important; padding: 0 !important; }

    /* STICKY HEADER FIX */
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
        background-color: #343a40 !important; /* Reference site dark gray */
        padding: 10px 0;
        border-radius: 6px !important;
        margin-bottom: 8px !important; 
        box-shadow: 0 4px 6px rgba(0,0,0,0.3); 
    }

    [data-testid="stImage"] { margin-bottom: 10px !important; border-radius: 6px; overflow: hidden; }

    /* Base button structural styles */
    [data-testid="column"] .stButton > button {
        width: 100% !important; border-radius: 4px !important; 
        line-height: 1.2 !important; text-align: center !important; transition: all 0.2s ease;
        margin-bottom: 4px !important;
    }
    [data-testid="column"] .stButton > button:hover { background-color: #e6f4ea !important; }
    
    /* OVERRIDES: Ensure Active/Booked slots beat Dynamic Backgrounds */
    
    /* User's Own Slot / Admin View (Solid Deep Red) */
    [data-testid="column"] div button[kind="primary"] { 
        background-color: #dc3545 !important; 
        border: 2px solid #bd2130 !important;
        padding: 10px 2px !important; # Match Prime height
    }
    [data-testid="column"] div button[kind="primary"] p { 
        color: #ffffff !important; 
        font-weight: 600 !important; font-size: 14px !important; 
    }
    
    /* 🔥 LIGHTER RED LOCKED SLOTS 🔥 (Light Red BG, Red Text) */
    [data-testid="column"] div button:disabled { 
        background-color: #ffcccc !important; /* Pale/Lighter Red */
        border: 1px solid #dc3545 !important;
        opacity: 1 !important; /* Removes default fade */
        padding: 10px 2px !important; # Match Prime height
    }
    [data-testid="column"] div button:disabled p { 
        color: #dc3545 !important; /* Bright Red Text */
        font-weight: 700 !important; font-size: 14px !important; 
    }
</style>
""", unsafe_allow_html=True)


# ==========================================
# 2. DATABASE & LOGGING SETUP
# ==========================================
USERS_FILE, BOOKINGS_FILE, AUDIT_FILE = 'users.csv', 'bookings.csv', 'audit.csv'
OWNER_EMAIL = "tomazbratina@gmail.com" 

def load_users(): 
    try: 
        df = pd.read_csv(USERS_FILE)
        if 'Max_Hours_Day' not in df.columns:
            df['Max_Hours_Day'] = 3.0
            df.to_csv(USERS_FILE, index=False)
        return df
    except: 
        return pd.DataFrame(columns=['Email', 'Name', 'Password', 'Role', 'Max_Hours_Day'])

if not os.path.exists(USERS_FILE): pd.DataFrame(columns=['Email', 'Name', 'Password', 'Role', 'Max_Hours_Day']).to_csv(USERS_FILE, index=False)
if not os.path.exists(BOOKINGS_FILE): pd.DataFrame(columns=['User', 'Date', 'Table', 'Time', 'Duration']).to_csv(BOOKINGS_FILE, index=False)
if not os.path.exists(AUDIT_FILE): pd.DataFrame(columns=['Timestamp', 'Action', 'Performed_By', 'Target_User', 'Details']).to_csv(AUDIT_FILE, index=False)

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
                "Password": st.column_config.TextColumn("Password", disabled=True),
                "Max_Hours_Day": st.column_config.NumberColumn("Daily Max (Hours)", min_value=0.5, max_value=24.0, step=0.5)
            },
            hide_index=True, use_container_width=True
        )
        if st.button("💾 Save User Changes", type="primary"):
            save_users(edited_users)
            if st.session_state.logged_in_user in edited_users['Email'].values:
                st.session_state.logged_in_name = edited_users[edited_users['Email'] == st.session_state.logged_in_user].iloc[0]['Name']
            st.success("Database updated successfully!")

    with tab2: st.dataframe(load_bookings(), use_container_width=True)
    with tab3: 
        if st.session_state.logged_in_user == OWNER_EMAIL:
            st.dataframe(pd.read_csv(AUDIT_FILE), use_container_width=True)
        else:
            st.error("⛔ Access Denied. Only the Owner can view the Audit Log.")
    st.stop()


# ==========================================
# 5. POPUP DIALOG WINDOWS
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
def book_modal(table, time, date, current_hours, max_allowed):
    st.write(f"Reserve **{table}** at **{time}**?")
    c1, c2 = st.columns(2)
    if c1.button("Confirm", type="primary", use_container_width=True):
        if current_hours + 0.5 > max_allowed and st.session_state.user_role != 'admin':
            st.error(f"Limit reached! Your daily limit is {max_allowed}h.")
        else:
            df = load_bookings()
            new_row = pd.DataFrame([[st.session_state.logged_in_user, str(date), table, time, 0.5]], columns=['User', 'Date', 'Table', 'Time', 'Duration'])
            save_bookings(pd.concat([df, new_row], ignore_index=True))
            log_action("BOOKED", st.session_state.logged_in_user, st.session_state.logged_in_user, f"{table} | {date} | {time}")
            st.rerun()
    if c2.button("Cancel", use_container_width=True):
        st.rerun()


# ==========================================
# 6. THE BOOKING SYSTEM UI & IMAGES
# ==========================================
st.markdown("<h1>RESERVE <span style='color: #dc3545;'>TABLE</span></h1>", unsafe_allow_html=True)
# Main Banner Image (Place holder of a pool hall)
st.image("https://images.unsplash.com/photo-1542155018-8fbf4cba4da4?q=80&w=1200&auto=format&fit=crop", use_container_width=True)

today = datetime.now().date()
upcoming_dates = [today + timedelta(days=i) for i in range(14)]
date_labels = ["Today" if d == today else "Tomorrow" if d == today + timedelta(days=1) else d.strftime("%a %d") for d in upcoming_dates]

selected_date_label_main = st.radio("Select Date:", date_labels, horizontal=True, label_visibility="collapsed")
view_date = upcoming_dates[date_labels.index(selected_date_label_main)]

users_df = load_users()
name_lookup = dict(zip(users_df['Email'], users_df['Name']))

user_max_hours = float(users_df[users_df['Email'] == st.session_state.logged_in_user]['Max_Hours_Day'].iloc[0])

bookings_df = load_bookings()
bookings_df['Date'] = bookings_df['Date'].astype(str) 
relevant_bookings = bookings_df[bookings_df['Date'] == str(view_date)]
user_today_hours = relevant_bookings[relevant_bookings['User'] == st.session_state.logged_in_user]['Duration'].sum()

if st.session_state.user_role != 'admin':
    st.caption(f"<div style='text-align:center; font-weight: 500; font-size: 15px;'>Your booked time: {user_today_hours} / {user_max_hours}h</div>", unsafe_allow_html=True)

# Table thumbnail images (Placeholders of pool tables)
TABLE_IMAGES = [
    "https://images.unsplash.com/photo-1598284566378-08d4469e8bd5?q=80&w=300&auto=format&fit=crop",
    "https://images.unsplash.com/photo-1598284566378-08d4469e8bd5?q=80&w=300&auto=format&fit=crop",
    "https://images.unsplash.com/photo-1598284566378-08d4469e8bd5?q=80&w=300&auto=format&fit=crop"
]

# --- THE GRID ---
cols = st.columns(3)

for i, col in enumerate(cols):
    t_name = f"Table {i+1}"
    
    # Render Sticky Header
    col.markdown(f"<div class='table-header'>Tbl {i+1}</div>", unsafe_allow_html=True)
    # Render Table Thumbnail Image
    col.image(TABLE_IMAGES[i], use_container_width=True)
    
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
                # Locked by someone else (pale red BG)
                col.button(f"{time_str} 🔒 {short_name}", key=f"dis_{button_key}", disabled=True, use_container_width=True)
                
        else:
            if col.button(f"{time_str} 🟢 FREE", key=f"add_{button_key}", use_container_width=True):
                book_modal(f"Table {i+1}", time_str, view_date, user_today_hours, user_max_hours)

# ==========================================
# 7. AUTO-SCROLL TO PRIME TIME SCRIPT (Gated)
# ==========================================
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
                    btn.scrollIntoView({behavior: 'smooth', block: 'nearest'});
                    break;
                }
            }
        }, 800); 
        </script>
        """,
        height=0
    )

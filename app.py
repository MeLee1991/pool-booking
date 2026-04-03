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
# 1. DYNAMIC "PRIME TIME" HEATMAP & SIZING ENGINE (HALF SIZE)
# ==========================================
HOURS = [f"{h:02d}:{m}" for h in range(8, 24) for m in ("00", "30")] 
dynamic_css = "<style>\n"

for idx, time_str in enumerate(HOURS):
    hour = int(time_str[:2])
    minute = int(time_str[3:])
    time_float = hour + minute / 60.0
    
    dist = abs(time_float - 19.5)
    intensity = max(0.0, 1.0 - (dist / 11.5))
    is_prime = 18 <= hour <= 22
    
    if is_prime:
        # PRIME TIME: Still flashy, but much smaller heights/padding
        bg_color = "#ffffff" if hour % 2 == 0 else "#fffde7" 
        font_size = "13px"
        font_weight = "700"
        padding = "4px 2px" 
        min_height = "28px"
        
        r = int(255 - (255 - 220) * intensity)
        g = int(193 - (193 - 53) * intensity)
        b = int(7 - (7 - 69) * intensity)
        border = f"2px solid rgb({r}, {g}, {b})"
    else:
        # OFF-HOURS: Tiny and compact
        bg_color = "#f8f9fa" if hour % 2 == 0 else "#e9ecef"
        font_size = "10px"
        font_weight = "400"
        padding = "2px 2px"
        min_height = "24px"
        
        gray = int(222 - (50 * intensity))
        border = f"1px solid rgb({gray}, {gray}, {gray})"

    child_idx = idx + 3 
    
    dynamic_css += f'[data-testid="column"] > div:nth-child({child_idx}) button {{\n'
    dynamic_css += f'    border: {border} !important;\n'
    dynamic_css += f'    background-color: {bg_color} !important;\n'
    dynamic_css += f'    padding: {padding} !important;\n'
    dynamic_css += f'    min-height: {min_height} !important;\n'
    dynamic_css += f'}}\n'
    
    dynamic_css += f'[data-testid="column"] > div:nth-child({child_idx}) button p {{\n'
    dynamic_css += f'    font-size: {font_size} !important;\n'
    dynamic_css += f'    font-weight: {font_weight} !important;\n'
    dynamic_css += f'    margin: 0 !important;\n'
    dynamic_css += f'    line-height: 1.0 !important;\n'
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
        padding-top: 1.5rem !important;
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
        gap: 8px 6px !important; 
        padding: 5px !important;
        border-bottom: 1px solid #dee2e6; 
        margin-bottom: 15px !important;
        overflow-x: auto !important; 
        -webkit-overflow-scrolling: touch; 
        scrollbar-width: none; 
        align-items: center;
        justify-content: center !important; 
    }
    section[data-testid="stMain"] [data-testid="stRadio"] > div[role="radiogroup"]::-webkit-scrollbar { display: none; }
    section[data-testid="stMain"] [data-testid="stRadio"] > div[role="radiogroup"]::before { content: "Week 1:"; grid-column: 1; grid-row: 1; font-weight: 500; color: #495057; font-size: 12px; padding-right: 5px; }
    section[data-testid="stMain"] [data-testid="stRadio"] > div[role="radiogroup"]::after { content: "Week 2:"; grid-column: 1; grid-row: 2; font-weight: 500; color: #495057; font-size: 12px; padding-right: 5px; }
    
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
        background-color: #ffffff !important; border: 1px solid #ced4da !important; border-radius: 4px !important;
        padding: 4px 8px !important; min-width: max-content; cursor: pointer; margin: 0 !important; 
    }
    section[data-testid="stMain"] [data-testid="stRadio"] label[data-checked="true"] { background-color: #007bff !important; border-color: #007bff !important; }
    section[data-testid="stMain"] [data-testid="stRadio"] label[data-checked="true"] p { color: #ffffff !important; }
    div[role="radiogroup"] div[role="radio"] > div:first-child { display: none !important; }

    /* ---------------------------------------------------
       MAIN AREA: TABLES & STICKY HEADERS
       --------------------------------------------------- */
    section[data-testid="stMain"] [data-testid="stHorizontalBlock"] { gap: 10px !important; justify-content: center !important; }
    section[data-testid="stMain"] [data-testid="column"] { display: flex !important; flex-direction: column !important; padding: 0 !important; }

    .table-header {
        position: sticky;       
        top: 2.875rem;          
        z-index: 990;           
        text-align: center !important;
        font-size: 14px !important;
        font-weight: 700 !important;
        text-transform: uppercase !important;
        color: #ffffff !important; 
        background-color: #343a40 !important; 
        padding: 6px 0;
        border-radius: 4px !important;
        margin-bottom: 4px !important; 
        box-shadow: 0 2px 4px rgba(0,0,0,0.3); 
    }

    [data-testid="stImage"] { margin-bottom: 8px !important; border-radius: 4px; overflow: hidden; }

    section[data-testid="stMain"] [data-testid="column"] .stButton > button {
        width: 100% !important; border-radius: 4px !important; 
        text-align: center !important; transition: all 0.1s ease;
        margin-bottom: 2px !important;
    }
    section[data-testid="stMain"] [data-testid="column"] .stButton > button:hover { background-color: #e6f4ea !important; }
    
    /* ACTIVE/BOOKED SLOTS OVERRIDES (Matching compact sizes) */
    section[data-testid="stMain"] [data-testid="column"] button[kind="primary"] { 
        background-color: #dc3545 !important; 
        border: 1px solid #bd2130 !important;
        padding: 4px 2px !important; 
        min-height: 28px !important;
    }
    section[data-testid="stMain"] [data-testid="column"] button[kind="primary"] p { 
        color: #ffffff !important; font-weight: 600 !important; font-size: 12px !important; 
    }
    
    section[data-testid="stMain"] [data-testid="column"] button[disabled] { 
        background-color: #ffcccc !important; 
        border: 1px solid #dc3545 !important;
        opacity: 1 !important; 
        padding: 4px 2px !important; 
        min-height: 28px !important;
    }
    section[data-testid="stMain"] [data-testid="column"] button[disabled] p { 
        color: #dc3545 !important; font-weight: 700 !important; font-size: 12px !important; 
    }

    /* ---------------------------------------------------
       📱 MOBILE RESPONSIVE SWIPE CAROUSEL
       --------------------------------------------------- */
    @media (max-width: 768px) {
        section[data-testid="stMain"] [data-testid="stHorizontalBlock"] {
            display: flex !important; flex-direction: row !important; flex-wrap: nowrap !important;
            overflow-x: auto !important; overflow-y: hidden !important; scroll-snap-type: x mandatory;
            padding-bottom: 15px !important; justify-content: flex-start !important; -webkit-overflow-scrolling: touch;
        }
        section[data-testid="stMain"] [data-testid="column"] {
            min-width: 85vw !important; flex: 0 0 85vw !important; scroll-snap-align: center; margin-right: 10px !important;
        }
        section[data-testid="stMain"] [data-testid="column"]:last-child { margin-right: 0 !important; }
    }
</style>
""", unsafe_allow_html=True)


# ==========================================
# 2. DATABASE & ARCHIVE SYSTEM
# ==========================================
USERS_FILE, BOOKINGS_FILE, AUDIT_FILE = 'users.csv', 'bookings.csv', 'audit.csv'
HISTORY_FILE = 'history.csv'
OWNER_EMAIL = "tomazbratina@gmail.com" 

# Create missing files
if not os.path.exists(USERS_FILE): pd.DataFrame(columns=['Email', 'Name', 'Password', 'Role', 'Max_Hours_Day']).to_csv(USERS_FILE, index=False)
if not os.path.exists(BOOKINGS_FILE): pd.DataFrame(columns=['User', 'Date', 'Table', 'Time', 'Duration']).to_csv(BOOKINGS_FILE, index=False)
if not os.path.exists(AUDIT_FILE): pd.DataFrame(columns=['Timestamp', 'Action', 'Performed_By', 'Target_User', 'Details']).to_csv(AUDIT_FILE, index=False)
if not os.path.exists(HISTORY_FILE): pd.DataFrame(columns=['User', 'Date', 'Table', 'Time', 'Duration']).to_csv(HISTORY_FILE, index=False)

def archive_old_bookings():
    try:
        df = pd.read_csv(BOOKINGS_FILE)
        if df.empty: return
        
        # Safely calculate dates
        df['DateObj'] = pd.to_datetime(df['Date'], errors='coerce').dt.date
        today = datetime.now().date()
        
        past_bookings = df[df['DateObj'] < today].copy()
        active_bookings = df[df['DateObj'] >= today].copy()
        
        # If we have old bookings, move them to history
        if not past_bookings.empty:
            past_bookings = past_bookings.drop(columns=['DateObj'])
            active_bookings = active_bookings.drop(columns=['DateObj'])
            
            history_df = pd.read_csv(HISTORY_FILE)
            history_df = pd.concat([history_df, past_bookings], ignore_index=True)
            history_df.to_csv(HISTORY_FILE, index=False)
            
            active_bookings.to_csv(BOOKINGS_FILE, index=False)
    except Exception as e:
        pass # Silently fail on first run or corruption

# Run archive on startup
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

    with tab2: 
        st.write("### Current Future Bookings")
        st.dataframe(load_bookings(), use_container_width=True)
        
    with tab3: 
        st.write("### Past Bookings Archive")
        st.dataframe(pd.read_csv(HISTORY_FILE), use_container_width=True)
        # Offer CSV download
        with open(HISTORY_FILE, "rb") as file:
            st.download_button(label="📥 Download History CSV", data=file, file_name="reservation_history.csv", mime="text/csv")
            
    with tab4: 
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
# 6. THE BOOKING SYSTEM UI & LOCAL IMAGES
# ==========================================
st.markdown("<h1>RESERVE <span style='color: #dc3545;'>TABLE</span></h1>", unsafe_allow_html=True)

# Main Banner Local Image Check
if os.path.exists("banner.jpg"):
    st.image("banner.jpg", use_container_width=True)

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


# --- THE GRID ---
cols = st.columns(3)

for i, col in enumerate(cols):
    t_name = f"Table {i+1}"
    
    # Render Sticky Header
    col.markdown(f"<div class='table-header'>Tbl {i+1}</div>", unsafe_allow_html=True)
    
    # Render Local Table Image
    img_name = f"table{i+1}.jpg"
    if os.path.exists(img_name):
        col.image(img_name, use_container_width=True)
    
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
                book_modal(f"Table {i+1}", time_str, view_date, user_today_hours, user_max_hours)

# ==========================================
# 7. SAFE AUTO-SCROLL SCRIPT
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

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import os

st.set_page_config(page_title="Pool Club - 9ft Tables", layout="wide")

# ==========================================
# 1. DATABASE & LOGGING SETUP
# ==========================================
USERS_FILE = 'users.csv'
BOOKINGS_FILE = 'bookings.csv'
AUDIT_FILE = 'audit.csv'
OWNER_EMAIL = "tomazbratina@gmail.com" # <--- The Ultimate Boss

# Initialize Files
if not os.path.exists(USERS_FILE):
    pd.DataFrame(columns=['Email', 'Password', 'Role']).to_csv(USERS_FILE, index=False)
if not os.path.exists(BOOKINGS_FILE):
    pd.DataFrame(columns=['User', 'Date', 'Table', 'Time', 'Duration']).to_csv(BOOKINGS_FILE, index=False)
if not os.path.exists(AUDIT_FILE):
    pd.DataFrame(columns=['Timestamp', 'Action', 'Performed_By', 'Target_User', 'Details']).to_csv(AUDIT_FILE, index=False)

def load_users(): return pd.read_csv(USERS_FILE)
def save_users(df): df.to_csv(USERS_FILE, index=False)
def load_bookings(): return pd.read_csv(BOOKINGS_FILE)
def save_bookings(df): df.to_csv(BOOKINGS_FILE, index=False)

# Master Log Function
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
if 'user_role' not in st.session_state:
    st.session_state.user_role = None

st.sidebar.title("🔐 Login / Register")

# Logged OUT View
if st.session_state.logged_in_user is None:
    auth_mode = st.sidebar.radio("Choose Action", ["Login", "Register"])
    
    email_input = st.sidebar.text_input("Email Address").strip().lower()
    password = st.sidebar.text_input("Password", type="password")
    
    if auth_mode == "Register":
        if st.sidebar.button("Create Account"):
            users = load_users()
            if email_input in users['Email'].values:
                st.sidebar.error("Email already exists!")
            elif len(email_input) < 5 or "@" not in email_input:
                st.sidebar.error("Please enter a valid email address.")
            else:
                # Auto-admin for the owner, pending for everyone else
                role = 'admin' if email_input == OWNER_EMAIL else 'pending'
                new_user = pd.DataFrame([[email_input, password, role]], columns=['Email', 'Password', 'Role'])
                save_users(pd.concat([users, new_user], ignore_index=True))
                st.sidebar.success("Account created! Please log in.")
                
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
                    st.session_state.user_role = role
                    st.rerun()
            else:
                st.sidebar.error("Incorrect email or password.")
    st.stop()

# Logged IN View Sidebar
st.sidebar.success(f"Playing as: \n**{st.session_state.logged_in_user}**")
if st.sidebar.button("Logout"):
    st.session_state.logged_in_user = None
    st.session_state.user_role = None
    st.rerun()

# --- NAVIGATION MENU (Only visible to Admins) ---
view_mode = "📅 Schedule"
if st.session_state.user_role == 'admin':
    st.sidebar.markdown("---")
    view_mode = st.sidebar.radio("Navigation", ["📅 Schedule", "⚙️ Admin Dashboard"])


# ==========================================
# 3. ADMIN DASHBOARD (Nicer & Owner-Protected)
# ==========================================
if view_mode == "⚙️ Admin Dashboard":
    st.title("⚙️ Club Administration")
    
    tab1, tab2, tab3 = st.tabs(["👥 User Management", "📊 Raw Database", "🕵️‍♂️ Security Audit Log"])
    
    # --- TAB 1: Nice User Editor ---
    with tab1:
        st.write("### Manage Permissions")
        st.write("Double-click the **Role** column to change a user's permissions, then click Save.")
        users_df = load_users()
        
        # Interactive Grid
        edited_users = st.data_editor(
            users_df,
            column_config={
                "Role": st.column_config.SelectboxColumn("User Role", options=["pending", "user", "admin"], required=True),
                "Email": st.column_config.TextColumn("Email Address", disabled=True), # Lock emails from accidental edits
                "Password": st.column_config.TextColumn("Password", disabled=True)
            },
            hide_index=True,
            use_container_width=True
        )
        
        if st.button("💾 Save User Changes", type="primary"):
            save_users(edited_users)
            st.success("Database updated successfully!")

    # --- TAB 2: Bookings ---
    with tab2:
        st.write("### All Active Bookings")
        st.dataframe(load_bookings(), use_container_width=True)

    # --- TAB 3: Secret Audit Log ---
    with tab3:
        st.write("### Master Action Log")
        if st.session_state.logged_in_user == OWNER_EMAIL:
            st.info("🔓 Owner Access Granted. Viewing all system actions.")
            st.dataframe(pd.read_csv(AUDIT_FILE), use_container_width=True)
        else:
            st.error("⛔ Access Denied. Only the Club Owner can view the security logs.")
            
    st.stop() # Stops the rest of the page (the schedule) from drawing if we are in the dashboard


# ==========================================
# 4. THE BOOKING SYSTEM (Schedule)
# ==========================================
st.title("🎱 Interactive Table Reservations")
st.info("Limit: 3 hours per person per day. Click directly on the schedule to book or cancel.")

HOURS = [f"{h:02d}:{m}" for h in range(24) for m in ("00", "30")]
today = datetime.now().date()
upcoming_dates = [today + timedelta(days=i) for i in range(7)]
date_labels = ["Today" if d == today else "Tomorrow" if d == today + timedelta(days=1) else d.strftime("%a, %b %d") for d in upcoming_dates]

selected_date_label_main = st.radio("View Schedule for:", date_labels, horizontal=True)
view_date = upcoming_dates[date_labels.index(selected_date_label_main)]

bookings_df = load_bookings()
bookings_df['Date'] = bookings_df['Date'].astype(str) 
relevant_bookings = bookings_df[bookings_df['Date'] == str(view_date)]

user_today_hours = relevant_bookings[relevant_bookings['User'] == st.session_state.logged_in_user]['Duration'].sum()

if st.session_state.user_role != 'admin':
    st.write(f"**Your booked time today:** {user_today_hours} / 3.0 hours")

cols = st.columns(3)

for i, col in enumerate(cols):
    t_name = f"Table {i+1}"
    col.subheader(t_name)
    
    for time_str in HOURS:
        hour_int = int(time_str.split(":")[0])
        time_icon = "🌙" if hour_int < 8 else "☀️" if hour_int < 16 else "🌆"
        
        booked = relevant_bookings[(relevant_bookings['Table'] == t_name) & (relevant_bookings['Time'] == time_str)]
        
        c1, c2 = col.columns([1, 2])
        c1.write(f"{time_icon} {time_str}")
        button_key = f"{t_name}_{time_str}_{view_date}"
        
        if not booked.empty:
            booked_user = booked.iloc[0]['User']
            if st.session_state.user_role == 'admin' or booked_user == st.session_state.logged_in_user:
                if c2.button(f"❌ Cancel ({booked_user})", key=f"del_{button_key}", type="primary"):
                    # LOG THE ACTION
                    log_action("CANCELLED", st.session_state.logged_in_user, booked_user, f"{t_name} | {view_date} | {time_str}")
                    
                    bookings_df = bookings_df[~((bookings_df['Table'] == t_name) & 
                                                (bookings_df['Time'] == time_str) & 
                                                (bookings_df['Date'] == str(view_date)))]
                    save_bookings(bookings_df)
                    st.rerun()
            else:
                c2.button(f"🔴 Taken", key=f"dis_{button_key}", disabled=True)
                
        else:
            if c2.button("🟢 FREE", key=f"add_{button_key}"):
                if user_today_hours + 0.5 > 3.0 and st.session_state.user_role != 'admin':
                    st.error("Booking limit reached! You can only book 3 hours per day.")
                else:
                    # LOG THE ACTION
                    log_action("BOOKED", st.session_state.logged_in_user, st.session_state.logged_in_user, f"{t_name} | {view_date} | {time_str}")
                    
                    new_row = pd.DataFrame([[st.session_state.logged_in_user, str(view_date), t_name, time_str, 0.5]], 
                                           columns=['User', 'Date', 'Table', 'Time', 'Duration'])
                    bookings_df = pd.concat([bookings_df, new_row], ignore_index=True)
                    save_bookings(bookings_df)
                    st.rerun()

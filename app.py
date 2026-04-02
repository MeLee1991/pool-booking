import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import os

st.set_page_config(page_title="Pool Club - 9ft Tables", layout="wide")

# ==========================================
# 1. DATABASE SETUP (Using CSV files)
# ==========================================
USERS_FILE = 'users.csv'
BOOKINGS_FILE = 'bookings.csv'

# Create user database if it doesn't exist
if not os.path.exists(USERS_FILE):
    pd.DataFrame(columns=['Username', 'Password', 'Role']).to_csv(USERS_FILE, index=False)
    # Role can be: 'pending', 'user', 'admin'

# Create bookings database if it doesn't exist
if not os.path.exists(BOOKINGS_FILE):
    pd.DataFrame(columns=['User', 'Date', 'Table', 'Time', 'Duration']).to_csv(BOOKINGS_FILE, index=False)

def load_users(): return pd.read_csv(USERS_FILE)
def save_users(df): df.to_csv(USERS_FILE, index=False)
def load_bookings(): return pd.read_csv(BOOKINGS_FILE)
def save_bookings(df): df.to_csv(BOOKINGS_FILE, index=False)


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
    
    username = st.sidebar.text_input("Username").strip().lower()
    password = st.sidebar.text_input("Password", type="password")
    
    if auth_mode == "Register":
        if st.sidebar.button("Create Account"):
            users = load_users()
            if username in users['Username'].values:
                st.sidebar.error("Username already exists!")
            elif len(username) < 3 or len(password) < 3:
                st.sidebar.error("Username and password must be at least 3 characters.")
            else:
                # Special rule: If username is "admin" and DB is empty, make them admin instantly
                role = 'admin' if username == 'admin' and users.empty else 'pending'
                new_user = pd.DataFrame([[username, password, role]], columns=['Username', 'Password', 'Role'])
                save_users(pd.concat([users, new_user], ignore_index=True))
                st.sidebar.success("Account created! Please log in.")
                
    elif auth_mode == "Login":
        if st.sidebar.button("Login"):
            users = load_users()
            user_match = users[(users['Username'] == username) & (users['Password'] == password)]
            
            if not user_match.empty:
                role = user_match.iloc[0]['Role']
                if role == 'pending':
                    st.sidebar.error("Your account is waiting for Admin approval.")
                else:
                    st.session_state.logged_in_user = username
                    st.session_state.user_role = role
                    st.rerun()
            else:
                st.sidebar.error("Incorrect username or password.")
                
    st.stop() # Stop drawing the rest of the app if not logged in

# Logged IN View
st.sidebar.success(f"Welcome, {st.session_state.logged_in_user}!")
if st.sidebar.button("Logout"):
    st.session_state.logged_in_user = None
    st.session_state.user_role = None
    st.rerun()


# ==========================================
# 3. ADMIN SETTINGS PANEL
# ==========================================
if st.session_state.user_role == 'admin':
    st.sidebar.markdown("---")
    st.sidebar.header("⚙️ Admin Settings")
    
    with st.expander("Manage Users & Approvals"):
        users_df = load_users()
        
        # Approve Pending Users
        pending = users_df[users_df['Role'] == 'pending']
        if not pending.empty:
            st.write("### Pending Approvals")
            for idx, row in pending.iterrows():
                col1, col2, col3 = st.columns([2, 1, 1])
                col1.write(row['Username'])
                if col2.button("Approve", key=f"app_{row['Username']}"):
                    users_df.loc[idx, 'Role'] = 'user'
                    save_users(users_df)
                    st.rerun()
                if col3.button("Reject", key=f"rej_{row['Username']}"):
                    users_df = users_df.drop(idx)
                    save_users(users_df)
                    st.rerun()
        else:
            st.info("No pending users.")
            
        # Change Roles
        st.write("### Change User Roles")
        all_users = users_df['Username'].tolist()
        user_to_edit = st.selectbox("Select User", all_users)
        new_role = st.selectbox("Assign Role", ["user", "admin", "pending"])
        if st.button("Update Role"):
            users_df.loc[users_df['Username'] == user_to_edit, 'Role'] = new_role
            save_users(users_df)
            st.success(f"Updated {user_to_edit} to {new_role}")

    with st.expander("Database & Statistics"):
        db_bookings = load_bookings()
        st.write(f"Total bookings all-time: {len(db_bookings)} slots")
        st.dataframe(db_bookings)


# ==========================================
# 4. THE BOOKING SYSTEM (Main Display)
# ==========================================
st.title("🎱 Interactive Table Reservations")
st.info("Limit: 3 hours per person per day. Click directly on the schedule to book or cancel.")

# Generate Time Slots & Dates
HOURS = [f"{h:02d}:{m}" for h in range(24) for m in ("00", "30")]
today = datetime.now().date()
upcoming_dates = [today + timedelta(days=i) for i in range(7)]
date_labels = ["Today" if d == today else "Tomorrow" if d == today + timedelta(days=1) else d.strftime("%a, %b %d") for d in upcoming_dates]

selected_date_label_main = st.radio("View Schedule for:", date_labels, horizontal=True)
view_date = upcoming_dates[date_labels.index(selected_date_label_main)]

# Load active bookings
bookings_df = load_bookings()
# Filter for the selected date. Ensure Date column is treated as a string to match `view_date` format
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
                    # Delete from CSV
                    bookings_df = bookings_df[~((bookings_df['Table'] == t_name) & 
                                                (bookings_df['Time'] == time_str) & 
                                                (bookings_df['Date'] == str(view_date)))]
                    save_bookings(bookings_df)
                    st.rerun()
            else:
                c2.button(f"🔴 {booked_user}", key=f"dis_{button_key}", disabled=True)
                
        else:
            if c2.button("🟢 FREE", key=f"add_{button_key}"):
                if user_today_hours + 0.5 > 3.0 and st.session_state.user_role != 'admin':
                    st.error("Booking limit reached! You can only book 3 hours per day.")
                else:
                    # Save to CSV
                    new_row = pd.DataFrame([[st.session_state.logged_in_user, str(view_date), t_name, time_str, 0.5]], 
                                           columns=['User', 'Date', 'Table', 'Time', 'Duration'])
                    bookings_df = pd.concat([bookings_df, new_row], ignore_index=True)
                    save_bookings(bookings_df)
                    st.rerun()

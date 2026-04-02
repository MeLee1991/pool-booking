import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

st.set_page_config(page_title="Pool Club - 9ft Tables", layout="wide")

st.title("🎱 Interactive Table Reservations")

# --- DATA STORAGE ---
if 'bookings' not in st.session_state:
    st.session_state.bookings = pd.DataFrame(columns=['User', 'Date', 'Table', 'Time', 'Duration'])

# --- GENERATE TIME SLOTS ---
HOURS = []
for h in range(24):
    HOURS.append(f"{h:02d}:00")
    HOURS.append(f"{h:02d}:30")

# --- DATE GENERATION ---
today = datetime.now().date()
upcoming_dates = [today + timedelta(days=i) for i in range(7)]

def get_date_label(d):
    if d == today: return "Today"
    if d == today + timedelta(days=1): return "Tomorrow"
    return d.strftime("%a, %b %d")

date_labels = [get_date_label(d) for d in upcoming_dates]

# --- SIDEBAR: USER LOGIN ---
st.sidebar.header("👤 Who are you?")
current_user = st.sidebar.text_input("Enter your name to interact:")

# Admin System (Hidden until you type 'admin')
is_admin = False
if current_user.strip().lower() == "admin":
    pwd = st.sidebar.text_input("Admin Password", type="password")
    if pwd == "1234": # Change this password to whatever you want
        is_admin = True
        st.sidebar.success("Logged in as Admin. You can delete any booking.")
    else:
        st.sidebar.warning("Awaiting admin password...")

if current_user and current_user.lower() != "admin":
    # Show user how many hours they have booked today
    st.sidebar.success(f"Playing as: {current_user}")

st.sidebar.info("Limit: 3 hours per person per day. Click directly on the schedule to book or cancel 30-min slots.")

# --- MAIN DISPLAY: THE SCHEDULE ---
selected_date_label_main = st.radio("View Schedule for:", date_labels, horizontal=True)
view_date = upcoming_dates[date_labels.index(selected_date_label_main)]

relevant_bookings = st.session_state.bookings[st.session_state.bookings['Date'] == view_date]

# Calculate hours used by current user on selected day
if current_user:
    user_today_hours = relevant_bookings[relevant_bookings['User'] == current_user]['Duration'].sum()
else:
    user_today_hours = 0.0

if current_user and not is_admin:
    st.write(f"**Your booked time today:** {user_today_hours} / 3.0 hours")

cols = st.columns(3)

# Build the interactive grid
for i, col in enumerate(cols):
    t_name = f"Table {i+1}"
    col.subheader(t_name)
    
    for time_str in HOURS:
        hour_int = int(time_str.split(":")[0])
        
        # Time of day indicators instead of HTML borders
        if hour_int < 8: time_icon = "🌙" # Night
        elif hour_int < 16: time_icon = "☀️" # Day
        else: time_icon = "🌆" # Evening

        # Check if this specific slot is booked
        booked = relevant_bookings[(relevant_bookings['Table'] == t_name) & (relevant_bookings['Time'] == time_str)]
        
        # Layout: Time on the left, Button on the right
        c1, c2 = col.columns([1, 2])
        c1.write(f"{time_icon} {time_str}")
        
        button_key = f"{t_name}_{time_str}_{view_date}"
        
        if not booked.empty:
            # SLOT IS TAKEN
            booked_user = booked.iloc[0]['User']
            
            # Can this person delete it? (Are they the owner, or the Admin?)
            if is_admin or (current_user and booked_user == current_user):
                if c2.button(f"❌ Cancel ({booked_user})", key=f"del_{button_key}", type="primary"):
                    # Delete Logic
                    st.session_state.bookings = st.session_state.bookings[
                        ~((st.session_state.bookings['Table'] == t_name) & 
                          (st.session_state.bookings['Time'] == time_str) & 
                          (st.session_state.bookings['Date'] == view_date))
                    ]
                    st.rerun() # Refresh the page instantly
            else:
                # Someone else's booking, disabled button
                c2.button(f"🔴 {booked_user}", key=f"dis_{button_key}", disabled=True)
                
        else:
            # SLOT IS FREE
            if c2.button("🟢 FREE", key=f"add_{button_key}"):
                if not current_user:
                    st.error("Please enter your name in the sidebar first!")
                elif current_user.lower() == "admin" and not is_admin:
                    st.error("Please enter the admin password first.")
                elif user_today_hours + 0.5 > 3.0 and not is_admin:
                    st.error("Booking limit reached! You can only book 3 hours per day.")
                else:
                    # Add Logic
                    new_row = pd.DataFrame([[current_user, view_date, t_name, time_str, 0.5]], 
                                           columns=['User', 'Date', 'Table', 'Time', 'Duration'])
                    st.session_state.bookings = pd.concat([st.session_state.bookings, new_row], ignore_index=True)
                    st.rerun() # Refresh the page instantly

# Legend
st.markdown("---")
st.markdown("**Legend:** 🌙 Night (00:00-08:00) | ☀️ Day (08:00-16:00) | 🌆 Evening (16:00-24:00)")

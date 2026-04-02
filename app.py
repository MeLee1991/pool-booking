import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

st.set_page_config(page_title="Pool Club - 9ft Tables", layout="wide")

# Title and Info
st.title("🎱 Table Reservations")
st.info("Limit: 3 hours per person per day. Slots are 30 minutes.")

# --- DATA STORAGE ---
if 'bookings' not in st.session_state:
    st.session_state.bookings = pd.DataFrame(columns=['User', 'Date', 'Table', 'Time', 'Duration'])

# --- GENERATE TIME SLOTS (00:00 to 23:30) ---
HOURS = []
for h in range(24):
    HOURS.append(f"{h:02d}:00")
    HOURS.append(f"{h:02d}:30")

# --- DATE GENERATION (Next 7 Days) ---
today = datetime.now().date()
upcoming_dates = [today + timedelta(days=i) for i in range(7)]

def get_date_label(d):
    if d == today: return "Today"
    if d == today + timedelta(days=1): return "Tomorrow"
    return d.strftime("%a, %b %d")

date_labels = [get_date_label(d) for d in upcoming_dates]

# --- SIDEBAR: BOOKING FORM ---
st.sidebar.header("Reserve a Table")
name = st.sidebar.text_input("Your Name")

selected_date_label_sidebar = st.sidebar.radio("Select Date", date_labels)
date = upcoming_dates[date_labels.index(selected_date_label_sidebar)]

table = st.sidebar.selectbox("Select Table", ["Table 1", "Table 2", "Table 3"])
time_slot = st.sidebar.selectbox("Start Time", HOURS)

# Changed to 0.5 hour increments
hrs = st.sidebar.number_input("Duration (Hours)", min_value=0.5, max_value=3.0, step=0.5)

if st.sidebar.button("Confirm Booking"):
    if name:
        # Check 3-hour limit
        user_today = st.session_state.bookings[
            (st.session_state.bookings['User'] == name) & 
            (st.session_state.bookings['Date'] == date)
        ]['Duration'].sum()
        
        if user_today + hrs > 3.0:
            st.sidebar.error(f"Cannot book. You already have {user_today}h booked for this day.")
        else:
            # Create a separate 0.5h row for EVERY half hour booked
            start_dt = datetime.strptime(time_slot, "%H:%M")
            slots_needed = int(hrs / 0.5)
            new_rows = []
            
            for i in range(slots_needed):
                current_slot = start_dt + timedelta(minutes=30 * i)
                
                # Prevent bookings from spilling past midnight into the next day
                if current_slot.day != start_dt.day: 
                    break 
                
                booking_time_str = current_slot.strftime("%H:%M")
                new_rows.append([name, date, table, booking_time_str, 0.5])
            
            new_data = pd.DataFrame(new_rows, columns=['User', 'Date', 'Table', 'Time', 'Duration'])
            st.session_state.bookings = pd.concat([st.session_state.bookings, new_data], ignore_index=True)
            st.sidebar.success("Booked successfully!")
    else:
        st.sidebar.warning("Please enter a name.")

# --- MAIN DISPLAY: THE SCHEDULE ---
st.subheader("Schedule")

selected_date_label_main = st.radio("View Schedule for:", date_labels, horizontal=True)
view_date = upcoming_dates[date_labels.index(selected_date_label_main)]

relevant_bookings = st.session_state.bookings[st.session_state.bookings['Date'] == view_date]

# Create 3 columns for 3 tables
cols = st.columns(3)

for i, col in enumerate(cols):
    t_name = f"Table {i+1}"
    col.subheader(t_name)
    
    # We build a custom HTML block for each column to control the borders
    html_content = "<div style='display:flex; flex-direction:column; gap:6px;'>"
    
    for time_str in HOURS:
        hour_int = int(time_str.split(":")[0])
        
        # Determine the color of the cell border based on the time
        if hour_int < 8:
            # 00:00 - 08:00 (Night) -> Deep Blue Border
            border_color = "#1E3A8A" 
        elif hour_int < 16:
            # 08:00 - 16:00 (Day) -> Yellow/Amber Border
            border_color = "#F59E0B" 
        else:
            # 16:00 - 24:0

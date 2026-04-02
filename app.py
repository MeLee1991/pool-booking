import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

st.set_page_config(page_title="Pool Club - 9ft Tables", layout="wide")

# Title and Info
st.title("🎱 Table Reservations")
st.info("Limit: 3 hours per person per day.")

# --- DATA STORAGE ---
if 'bookings' not in st.session_state:
    st.session_state.bookings = pd.DataFrame(columns=['User', 'Date', 'Table', 'Time', 'Duration'])

# --- DATE GENERATION (Next 7 Days) ---
today = datetime.now().date()
upcoming_dates = [today + timedelta(days=i) for i in range(7)]

# Create friendly labels for the buttons
def get_date_label(d):
    if d == today: 
        return "Today"
    if d == today + timedelta(days=1): 
        return "Tomorrow"
    return d.strftime("%a, %b %d") # Example: "Fri, Apr 04"

date_labels = [get_date_label(d) for d in upcoming_dates]


# --- SIDEBAR: BOOKING FORM ---
st.sidebar.header("Reserve a Table")
name = st.sidebar.text_input("Your Name")

# Nicer date picker (Vertical list)
selected_date_label_sidebar = st.sidebar.radio("Select Date", date_labels)
# Convert the label back to the actual date object
date = upcoming_dates[date_labels.index(selected_date_label_sidebar)]

table = st.sidebar.selectbox("Select Table", ["Table 1", "Table 2", "Table 3"])
time_slot = st.sidebar.selectbox("Start Time", [f"{h:02d}:00" for h in range(8, 24)])
hrs = st.sidebar.number_input("How many hours?", min_value=1, max_value=3, step=1)

if st.sidebar.button("Confirm Booking"):
    if name:
        # Check 3-hour limit
        user_today = st.session_state.bookings[
            (st.session_state.bookings['User'] == name) & 
            (st.session_state.bookings['Date'] == date)
        ]['Duration'].sum()
        
        if user_today + hrs > 3:
            st.sidebar.error(f"Cannot book. You already have {user_today}h booked for this day.")
        else:
            start_hour = int(time_slot.split(":")[0])
            new_rows = []
            
            for i in range(hrs):
                current_hour = start_hour + i
                if current_hour < 24: # Prevents bookings past 23:00
                    booking_hour = f"{current_hour:02d}:00"
                    new_rows.append([name, date, table, booking_hour, 1])
            
            new_data = pd.DataFrame(new_rows, columns=['User', 'Date', 'Table', 'Time', 'Duration'])
            st.session_state.bookings = pd.concat([st.session_state.bookings, new_data], ignore_index=True)
            st.sidebar.success("Booked successfully!")
    else:
        st.sidebar.warning("Please enter a name.")


# --- MAIN DISPLAY: THE SCHEDULE ---
st.subheader("Schedule")

# Nicer date picker (Horizontal row for wide screen)
selected_date_label_main = st.radio("View Schedule for:", date_labels, horizontal=True)
view_date = upcoming_dates[date_labels.index(selected_date_label_main)]

relevant_bookings = st.session_state.bookings[st.session_state.bookings['Date'] == view_date]

# Create 3 columns for 3 tables
t1, t2, t3 = st.columns(3)

for i, col in enumerate([t1, t2, t3]):
    t_name = f"Table {i+1}"
    col.subheader(t_name)
    
    for hour in range(8, 24):
        h_str = f"{hour:02d}:00"
        # Check if booked
        booked = relevant_bookings[(relevant_bookings['Table'] == t_name) & (relevant_bookings['Time'] == h_str)]
        
        if not booked.empty:
            col.error(f"🔴 {h_str} - {booked.iloc[0]['User']}")
        else:
            col.success(f"🟢 {h_str} - FREE")

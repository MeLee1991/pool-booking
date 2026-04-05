import os
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

st.set_page_config(page_title="Pool Booking", layout="wide")

# =========================
# CSS (PRECISION CONTROL)
# =========================
st.markdown("""
<style>
/* FORCE 3 COLUMNS & REMOVE GAPS */
[data-testid="stHorizontalBlock"] {
    display: flex !important;
    flex-direction: row !important;
    flex-wrap: nowrap !important;
    gap: 2px !important; /* Extremely tight gap */
}

[data-testid="column"] {
    width: 33% !important;
    flex: 1 1 33% !important;
    min-width: 33% !important;
    padding: 0px 1px !important; /* Smaller columns */
}

/* TIGHTEN VERTICAL SPACING */
[data-testid="column"] > div {
    padding: 0px !important;
    margin-bottom: -14px !important; /* Very close rows */
}

/* BUTTON STYLING */
.stButton button {
    width: 100% !important;
    height: 24px !important; /* Smaller slot size */
    font-size: 10px !important; /* Smaller font */
    padding: 0px !important;
    border-radius: 4px !important;
    border: 1px solid rgba(255,255,255,0.1) !important;
}

/* RED FOR BOOKED SLOTS (NOT GRAY) */
/* We target the disabled state or specific keys if needed, 
   but for 'Lighter Red', we style the button background */
div.stButton > button:disabled {
    background-color: #ffcccc !important; /* Lighter Red */
    color: #900 !important; /* Dark Red text for contrast */
    opacity: 1 !important; /* Prevents the 'faded' gray look */
}

/* SCROLLABLE DATE BAR */
[data-testid="stRadio"] > div {
    display: flex !important;
    flex-direction: row !important;
    overflow-x: auto !important; /* Scrollable if no space */
    white-space: nowrap !important;
    gap: 10px !important;
    padding-bottom: 10px;
}

/* HEADER CHANGE */
.table-header-box {
    text-align: center;
    font-weight: bold;
    font-size: 12px;
    background-color: #1e1e1e;
    color: #fff;
    padding: 5px 0px;
    margin-bottom: 20px;
    border-bottom: 2px solid #444;
}
</style>
""", unsafe_allow_html=True)

# =========================
# LOGIC & DATA
# =========================
if "table_names" not in st.session_state:
    st.session_state.table_names = ["Table 1", "Table 2", "Table 3"]

# Date Picker (Horizontal Scrollable)
today = datetime.now().date()
dates = [today + timedelta(days=i) for i in range(14)]
date_labels = [d.strftime("%a %d") for d in dates]
selected_label = st.radio("", date_labels, horizontal=True)
selected_date = dates[date_labels.index(selected_label)]

# Header Change / Rename
with st.expander("Edit Table Names"):
    for i in range(3):
        st.session_state.table_names[i] = st.text_input(f"Table {i+1}", st.session_state.table_names[i])

# Time Slots
HOURS = []
for h in list(range(8, 24)) + list(range(0, 3)):
    for m in ["00", "30"]:
        HOURS.append(f"{h:02d}:{m}")

# =========================
# THE GRID
# =========================
df = load_bookings() # Assumes your helper function is present

# Table Headers
h_cols = st.columns(3)
for i, col in enumerate(h_cols):
    col.markdown(f"<div class='table-header-box'>{st.session_state.table_names[i]}</div>", unsafe_allow_html=True)

# Rows
for t in HOURS:
    # 4-hour group coloring (Zebra stripes for readability)
    hour_int = int(t.split(":")[0])
    is_alt_group = ((hour_int - 8) % 24) // 4 % 2 == 0
    bg_style = "background-color: rgba(255,255,255,0.03);" if is_alt_group else ""
    
    row_container = st.container()
    # Apply background to the whole 'time group' block
    with row_container:
        t_cols = st.columns(3)
        for i, col in enumerate(t_cols):
            t_name = st.session_state.table_names[i]
            key = f"btn_{i}_{t}_{selected_date}"
            
            # Check booking
            match = df[(df["Table"] == t_name) & (df["Time"] == t) & (df["Date"] == str(selected_date))]
            
            if not match.empty:
                user_name = match.iloc[0]["Name"]
                # Displayed as Lighter Red via CSS (disabled=True)
                col.button(f"{t} 🔒 {user_name}", key=key, disabled=True)
            else:
                if col.button(f"{t} 🟢", key=key):
                    # Your booking logic here
                    pass

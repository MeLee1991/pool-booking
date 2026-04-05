import os
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

st.set_page_config(page_title="Pool Booking", layout="wide")

# =========================
# 1. DATABASE FUNCTIONS
# =========================
BOOKINGS_FILE = "bookings.csv"

def load_bookings():
    if os.path.exists(BOOKINGS_FILE):
        return pd.read_csv(BOOKINGS_FILE)
    return pd.DataFrame(columns=["User","Name","Date","Table","Time"])

def save_bookings(df):
    df.to_csv(BOOKINGS_FILE, index=False)

# =========================
# 2. CSS (ULTRA-SLIM NO-SCROLL)
# =========================
st.markdown("""
<style>
/* PREVENT HORIZONTAL SCROLL & FORCE 3 COLUMNS */
[data-testid="stHorizontalBlock"] {
    display: flex !important;
    flex-wrap: nowrap !important;
    width: 100vw !important; /* Exactly screen width */
    gap: 1px !important;
    margin: 0 !important;
}

[data-testid="column"] {
    flex: 1 1 33% !important;
    width: 32vw !important; /* Force columns to be slim */
    max-width: 32vw !important;
    padding: 0px !important;
}

/* TIGHTEN ROWS */
[data-testid="column"] > div {
    padding: 0px !important;
    margin-bottom: -18px !important; 
}

/* SLIM SLOTS (SMALLER WIDTH) */
.stButton button {
    width: 95% !important; 
    height: 24px !important; 
    font-size: 9px !important;
    padding: 0px !important;
    margin: 0 auto !important;
    display: block !important;
    border-radius: 2px !important;
    border: none !important;
}

/* COLORS: LIGHT RED vs GREEN */
div.stButton > button:disabled {
    background-color: #ffcdd2 !important; /* Lighter Red */
    color: #b71c1c !important; 
    opacity: 1 !important;
}

div.stButton > button:not(:disabled) {
    background-color: #c8e6c9 !important; /* Light Green */
    color: #1b5e20 !important;
}

/* DATE BAR SCROLL */
[data-testid="stRadio"] > div {
    display: flex !important;
    overflow-x: auto !important;
    white-space: nowrap !important;
    gap: 8px !important;
}

/* HEADER */
.table-header-box {
    text-align: center;
    font-weight: bold;
    font-size: 10px;
    background-color: #000;
    color: #fff;
    padding: 4px 0;
    margin-bottom: 25px;
    width: 95%;
    margin: 0 auto;
}
</style>
""", unsafe_allow_html=True)

# =========================
# 3. APP LOGIC
# =========================
if "table_names" not in st.session_state:
    st.session_state.table_names = ["T1", "T2", "T3"]

# Date Selection
today = datetime.now().date()
dates = [today + timedelta(days=i) for i in range(14)]
date_labels = [d.strftime("%a %d") for d in dates]
selected_label = st.radio("", date_labels, horizontal=True)
selected_date = dates[date_labels.index(selected_label)]

df = load_bookings()

# Time Slots
HOURS = []
for h in list(range(8, 24)) + list(range(0, 3)):
    for m in ["00", "30"]:
        HOURS.append(f"{h:02d}:{m}")

# 4. RENDER HEADERS
h_cols = st.columns(3)
for i, col in enumerate(h_cols):
    col.markdown(f"<div class='table-header-box'>{st.session_state.table_names[i]}</div>", unsafe_allow_html=True)

# 5. RENDER GRID
for t in HOURS:
    t_cols = st.columns(3)
    for i, col in enumerate(t_cols):
        t_name = st.session_state.table_names[i]
        key = f"btn_{i}_{t}_{selected_date}"
        
        match = df[(df["Table"] == t_name) & (df["Time"] == t) & (df["Date"] == str(selected_date))]
        
        if not match.empty:
            user_name = match.iloc[0]["Name"]
            # BOOKED (Light Red)
            col.button(f"{t} {user_name[:5]}", key=key, disabled=True)
        else:
            # FREE (Green)
            if col.button(f"{t} 🟢", key=key):
                # Add booking logic...
                st.rerun()

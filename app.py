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
# 2. CSS (HARD OVERRIDE FOR 3-COLUMNS)
# =========================
st.markdown("""
<style>
/* 1. FORCE 3 COLUMNS ON MOBILE - NO STACKING */
[data-testid="stHorizontalBlock"] {
    display: grid !important;
    grid-template-columns: repeat(3, 1fr) !important; /* 3 Equal narrow columns */
    gap: 4px !important;
    width: 100% !important;
}

[data-testid="column"] {
    width: auto !important;
    flex: none !important;
}

/* 2. BUTTON SLOTS (2 ROWS) */
.stButton button {
    width: 100% !important;
    height: 42px !important; /* Height for two rows of text */
    font-size: 10px !important;
    line-height: 1.2 !important;
    padding: 0px !important;
    border-radius: 4px !important;
    border: 1px solid #bbbbbb !important; /* Visible border around slot */
    white-space: pre-wrap !important; /* Allows \n to work */
    display: block !important;
    margin-bottom: -12px !important; /* Tightens rows */
}

/* 3. SLOT COLORS */
/* Available (Green) */
div.stButton > button:not(:disabled) {
    background-color: #f0fff4 !important;
    color: #1a7f37 !important;
    border-color: #bef264 !important;
}

/* Booked (Light Red) */
div.stButton > button:disabled {
    background-color: #fff1f2 !important; 
    color: #be123c !important; 
    border-color: #fecaca !important;
    opacity: 1 !important;
}

/* 4. HEADER SPACING */
.table-header-box {
    text-align: center;
    font-weight: bold;
    font-size: 11px;
    background-color: #111;
    color: #fff;
    padding: 6px 0;
    margin-bottom: 30px; /* Space before table starts */
    border-radius: 4px;
}

/* 5. DATE BAR (SCROLLABLE) */
[data-testid="stRadio"] > div {
    display: flex !important;
    overflow-x: auto !important;
    gap: 12px !important;
}
</style>
""", unsafe_allow_html=True)

# =========================
# 3. APP LOGIC
# =========================
if "table_names" not in st.session_state:
    st.session_state.table_names = ["Table 1", "Table 2", "Table 3"]

st.title("RESERVE TABLE")

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

# 5. RENDER GRID (LOCKED 3-COLUMNS)
for t in HOURS:
    t_cols = st.columns(3)
    for i, col in enumerate(t_cols):
        t_name = st.session_state.table_names[i]
        key = f"btn_{i}_{t}_{selected_date}"
        
        match = df[(df["Table"] == t_name) & (df["Time"] == t) & (df["Date"] == str(selected_date))]
        
        if not match.empty:
            u_name = match.iloc[0]["Name"]
            # 2 rows: Time then Name
            col.button(f"{t}\n{u_name[:7]}", key=key, disabled=True)
        else:
            # 2 rows: Time then Status
            if col.button(f"{t}\n🟢", key=key):
                # Add booking logic...
                st.rerun()

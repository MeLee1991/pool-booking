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
# 2. CSS (NARROW COLUMNS & DEFINED SLOTS)
# =========================
st.markdown("""
<style>
/* CENTER THE TABLE & MAKE COLUMNS NARROW */
[data-testid="stHorizontalBlock"] {
    display: flex !important;
    justify-content: center !important; /* Centers the narrow table */
    gap: 2px !important;
    width: 100% !important;
}

[data-testid="column"] {
    flex: 0 0 80px !important; /* STRICT NARROW WIDTH (Adjust this number to go even narrower) */
    min-width: 80px !important;
    max-width: 80px !important;
    padding: 0px !important;
}

/* TIGHTEN VERTICAL SPACING */
[data-testid="column"] > div {
    padding: 0px !important;
    margin-bottom: -15px !important; 
}

/* BUTTON "SLOTS" WITH BORDERS */
.stButton button {
    width: 75px !important; /* Fixed width slightly smaller than column */
    height: 32px !important; /* Height for 2 rows of text */
    font-size: 9px !important;
    line-height: 1.1 !important;
    padding: 2px !important;
    margin: 0 auto !important;
    display: block !important;
    border-radius: 4px !important;
    border: 1px solid #ccc !important; /* Visible border */
    text-align: center !important;
    white-space: normal !important; /* Allows 2 rows */
    word-wrap: break-word !important;
}

/* LIGHT RED SLOT (BOOKED) */
div.stButton > button:disabled {
    background-color: #ffdee2 !important; 
    color: #a71d2a !important; 
    border: 1px solid #ebccd1 !important;
    opacity: 1 !important;
}

/* GREEN SLOT (AVAILABLE) */
div.stButton > button:not(:disabled) {
    background-color: #e6ffed !important;
    color: #1a7f37 !important;
    border: 1px solid #acf2bd !important;
}

/* HEADER STYLE */
.table-header-box {
    text-align: center;
    font-weight: bold;
    font-size: 10px;
    background-color: #111;
    color: #fff;
    padding: 5px 0;
    margin-bottom: 25px;
    border-radius: 4px;
    width: 75px;
    margin: 0 auto;
}

/* DATE BAR SCROLL */
[data-testid="stRadio"] > div {
    display: flex !important;
    overflow-x: auto !important;
    gap: 10px !important;
    padding: 10px 0;
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

# 5. RENDER GRID
for t in HOURS:
    t_cols = st.columns(3)
    for i, col in enumerate(t_cols):
        t_name = st.session_state.table_names[i]
        key = f"btn_{i}_{t}_{selected_date}"
        
        match = df[(df["Table"] == t_name) & (df["Time"] == t) & (df["Date"] == str(selected_date))]
        
        if not match.empty:
            user_name = match.iloc[0]["Name"]
            # 2 Rows: Time on top, Name on bottom
            col.button(f"{t}\n{user_name[:7]}", key=key, disabled=True)
        else:
            if col.button(f"{t}\n🟢", key=key):
                # Add booking logic...
                st.rerun()

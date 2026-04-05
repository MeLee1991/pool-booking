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
# 2. CSS (ULTRA-COMPACT GRID)
# =========================
st.markdown("""
<style>
/* FORCE 3 TINY COLUMNS */
[data-testid="stHorizontalBlock"] {
    display: flex !important;
    flex-direction: row !important;
    flex-wrap: nowrap !important;
    justify-content: center !important;
    gap: 4px !important;
}

[data-testid="column"] {
    width: 30% !important; /* Makes the table 2x smaller in width */
    max-width: 110px !important; /* Fixed width for cells */
    flex: 0 0 30% !important;
    padding: 0px !important;
}

/* TIGHTEN ROWS (NO VERTICAL GAPS) */
[data-testid="column"] > div {
    padding: 0px !important;
    margin-bottom: -18px !important; /* Pulls cells together */
}

/* BUTTON STYLE: FIXED SIZE & SMALL FONT */
.stButton button {
    width: 95% !important; /* Slightly smaller than column width */
    height: 22px !important; 
    font-size: 8px !important; /* Very small font for compact look */
    line-height: 1 !important;
    padding: 0px !important;
    border-radius: 4px !important;
    border: none !important;
    margin: 0 auto !important;
    display: block !important;
}

/* LIGHT RED FOR BOOKED (NOT GRAY) */
div.stButton > button:disabled {
    background-color: #ffcccc !important; 
    color: #b00020 !important; 
    opacity: 1 !important;
    border: 1px solid #ff9999 !important;
}

/* GREEN FOR AVAILABLE */
div.stButton > button:not(:disabled) {
    background-color: #e6ffed !important;
    color: #1a7f37 !important;
    border: 1px solid #acf2bd !important;
}

/* SCROLLABLE DATE BAR */
[data-testid="stRadio"] > div {
    display: flex !important;
    overflow-x: auto !important;
    white-space: nowrap !important;
    gap: 10px !important;
    padding: 10px 0 !important;
}

/* HEADER STYLE */
.table-header-box {
    text-align: center;
    font-weight: bold;
    font-size: 10px;
    background-color: #111;
    color: #fff;
    padding: 5px 0;
    margin-bottom: 25px; /* Space before rows start */
    border-radius: 4px;
    width: 95%;
    margin-left: auto;
    margin-right: auto;
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
            # Booked (Light Red)
            col.button(f"{t} {user_name}", key=key, disabled=True)
        else:
            # Available (Green)
            if col.button(f"{t} 🟢", key=key):
                # Simple logic to add a booking
                new_data = pd.DataFrame([[st.session_state.get("user", "guest"), "User", str(selected_date), t_name, t]], 
                                       columns=["User", "Name", "Date", "Table", "Time"])
                save_bookings(pd.concat([df, new_data]))
                st.rerun()

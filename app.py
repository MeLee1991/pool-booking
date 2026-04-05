import os
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

st.set_page_config(page_title="Pool Booking", layout="wide")

# =========================
# 1. DATABASE FUNCTIONS (FIXED)
# =========================
BOOKINGS_FILE = "bookings.csv"

def load_bookings():
    if os.path.exists(BOOKINGS_FILE):
        return pd.read_csv(BOOKINGS_FILE)
    return pd.DataFrame(columns=["User","Name","Date","Table","Time"])

def save_bookings(df):
    df.to_csv(BOOKINGS_FILE, index=False)

# =========================
# 2. CSS (COMPRESSED UI)
# =========================
st.markdown("""
<style>
/* FORCE 3 COMPACT COLUMNS */
[data-testid="stHorizontalBlock"] {
    display: flex !important;
    flex-direction: row !important;
    flex-wrap: nowrap !important;
    gap: 2px !important;
}

[data-testid="column"] {
    width: 33% !important;
    flex: 1 1 33% !important;
    min-width: 33% !important;
    padding: 0px 1px !important;
}

/* TIGHTEN ROWS */
[data-testid="column"] > div {
    padding: 0px !important;
    margin-bottom: -16px !important; /* Extremely close rows */
}

/* BUTTONS: SMALLER FONT & UNIFORM SIZE */
.stButton button {
    width: 100% !important;
    height: 22px !important; 
    font-size: 9px !important; 
    padding: 0px !important;
    border-radius: 2px !important;
    border: none !important;
    text-overflow: ellipsis;
    overflow: hidden;
}

/* LIGHT RED FOR BOOKED SLOTS (NOT GRAY) */
div.stButton > button:disabled {
    background-color: #ffb3b3 !important; /* Lighter Red */
    color: #800000 !important; /* Dark text for readability */
    opacity: 1 !important;
    border: 1px solid #ff8080 !important;
}

/* SCROLLABLE DATE BAR (PREVENTS VERTICAL TEXT) */
[data-testid="stRadio"] > div {
    display: flex !important;
    overflow-x: auto !important;
    white-space: nowrap !important;
    gap: 8px !important;
    padding-bottom: 5px;
}
[data-testid="stRadio"] label {
    font-size: 11px !important;
}

/* HEADER SPACING */
.table-header-box {
    text-align: center;
    font-weight: bold;
    font-size: 11px;
    background-color: #000;
    color: #fff;
    padding: 4px 0;
    margin-bottom: 22px; /* Gap between header and table */
    border-radius: 3px;
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

# Table Rename Expander
with st.expander("⚙️ Rename Tables"):
    for i in range(3):
        st.session_state.table_names[i] = st.text_input(f"Table {i+1}", st.session_state.table_names[i])

# Time Slots
HOURS = []
for h in list(range(8, 24)) + list(range(0, 3)):
    for m in ["00", "30"]:
        HOURS.append(f"{h:02d}:{m}")

df = load_bookings()

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
            # Booked slot (Light Red)
            col.button(f"{t} 🔒 {user_name}", key=key, disabled=True)
        else:
            # Available slot
            if col.button(f"{t} 🟢", key=key):
                # Placeholder for booking action
                new_row = pd.DataFrame([[st.session_state.get("user", "guest"), "Guest", str(selected_date), t_name, t]], 
                                     columns=["User","Name","Date","Table","Time"])
                save_bookings(pd.concat([df, new_row]))
                st.rerun()

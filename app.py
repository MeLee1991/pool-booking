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
# 2. CSS (STRICT NARROW COLUMNS & BUTTON SLOTS)
# =========================
st.markdown("""
<style>
/* 1. NARROW 3-COLUMN GRID (CENTERED) */
[data-testid="column"] {
    flex: 0 0 65px !important; /* ULTRA NARROW COLUMN */
    min-width: 65px !important;
    max-width: 65px !important;
    padding: 0px !important;
    margin: 0 auto !important;
}

[data-testid="stHorizontalBlock"] {
    justify-content: center !important; /* Centers the 3 narrow columns */
    gap: 4px !important;
}

/* 2. TIGHTEN VERTICAL SPACING */
[data-testid="column"] > div {
    padding: 0px !important;
    margin-bottom: -12px !important; 
}

/* 3. BUTTONS AS "SLOTS" (2 ROWS OF TEXT) */
.stButton button {
    width: 60px !important; /* Fixed button width */
    height: 40px !important; /* Height to comfortably fit 2 rows */
    font-size: 10px !important;
    line-height: 1.2 !important;
    padding: 0px !important;
    border-radius: 6px !important;
    border: 1.5px solid #d1d1d1 !important; /* Defined border */
    background-color: #f9f9f9 !important;
    display: block !important;
    white-space: pre-wrap !important; /* Essential for the \n line break */
    box-shadow: 1px 1px 2px rgba(0,0,0,0.05) !important;
}

/* 4. COLORS FOR SLOTS */
/* Booked: Light Red */
div.stButton > button:disabled {
    background-color: #fee2e2 !important; 
    color: #991b1b !important; 
    border-color: #fecaca !important;
    opacity: 1 !important;
}

/* Available: Light Green */
div.stButton > button:not(:disabled) {
    background-color: #f0fdf4 !important;
    color: #166534 !important;
    border-color: #dcfce7 !important;
}

/* 5. HEADER STYLE */
.table-header-box {
    text-align: center;
    font-weight: bold;
    font-size: 11px;
    background-color: #111;
    color: #fff;
    padding: 5px 0;
    margin-bottom: 25px; /* Space before table starts */
    border-radius: 4px;
    width: 60px;
    margin: 0 auto;
}

/* 6. BACKGROUND GROUPING (EVERY 4 HOURS) */
.time-group-bg {
    background-color: rgba(0,0,0,0.03);
    border-radius: 8px;
    padding: 5px 0;
    margin-bottom: 5px;
}
</style>
""", unsafe_allow_html=True)

# =========================
# 3. APP LOGIC
# =========================
if "table_names" not in st.session_state:
    st.session_state.table_names = ["T1", "T2", "T3"]

st.title("RESERVE TABLE")

# Date Selection (Stays normal width)
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
    # Logic for background colors (Changes every 4 hours)
    hour_int = int(t.split(":")[0])
    is_group_a = ((hour_int - 8) % 24) // 4 % 2 == 0
    
    # Use a container for the group background if desired
    t_cols = st.columns(3)
    
    for i, col in enumerate(t_cols):
        t_name = st.session_state.table_names[i]
        key = f"btn_{i}_{t}_{selected_date}"
        
        match = df[(df["Table"] == t_name) & (df["Time"] == t) & (df["Date"] == str(selected_date))]
        
        if not match.empty:
            user_name = match.iloc[0]["Name"]
            # Two lines: Time on top, short name on bottom
            col.button(f"{t}\n{user_name[:6]}", key=key, disabled=True)
        else:
            # Two lines: Time on top, green dot on bottom
            if col.button(f"{t}\n🟢", key=key):
                # Simple logic for demo
                new_row = pd.DataFrame([[st.session_state.get("user", "guest"), "User", str(selected_date), t_name, t]], 
                                     columns=["User", "Name", "Date", "Table", "Time"])
                save_bookings(pd.concat([df, new_row]))
                st.rerun()

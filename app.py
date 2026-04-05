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
# 2. CSS (STRICT 3-COLUMN LAYOUT)
# =========================
st.markdown("""
<style>
/* FORCE ENTIRE TABLE TO FIT SCREEN WIDTH */
[data-testid="stHorizontalBlock"] {
    display: flex !important;
    flex-direction: row !important;
    flex-wrap: nowrap !important;
    width: 100% !important;
    gap: 2px !important;
}

[data-testid="column"] {
    flex: 1 1 33% !important;
    width: 33% !important;
    min-width: 0px !important; /* Prevents overflow */
    padding: 0px !important;
}

/* TIGHTEN VERTICAL ROWS */
[data-testid="column"] > div {
    padding: 0px !important;
    margin-bottom: -18px !important; 
}

/* NICE BUTTON SLOTS (FIXED WIDTH) */
.stButton button {
    width: 92% !important; /* Slightly smaller than column for padding look */
    max-width: 120px;
    height: 28px !important; 
    font-size: 10px !important;
    font-weight: 600 !important;
    margin: 0 auto !important;
    display: block !important;
    border-radius: 4px !important;
    border: none !important;
    box-shadow: inset 0 -2px 0 rgba(0,0,0,0.1); /* Subtle slot depth */
    transition: all 0.2s;
}

/* STATE: AVAILABLE (SOFT GREEN) */
div.stButton > button:not(:disabled) {
    background-color: #d4edda !important;
    color: #155724 !important;
    border: 1px solid #c3e6cb !important;
}

/* STATE: BOOKED (LIGHT RED - NOT GRAY) */
div.stButton > button:disabled {
    background-color: #f8d7da !important;
    color: #721c24 !important;
    opacity: 1 !important;
    border: 1px solid #f5c6cb !important;
}

/* DATE BAR (HORIZONTAL SCROLL) */
[data-testid="stRadio"] > div {
    display: flex !important;
    overflow-x: auto !important;
    white-space: nowrap !important;
    gap: 15px !important;
    padding: 10px 5px !important;
}

/* HEADER STYLE */
.table-header-box {
    text-align: center;
    font-weight: bold;
    font-size: 11px;
    background-color: #222;
    color: #fff;
    padding: 6px 0;
    margin-bottom: 25px; 
    border-radius: 4px;
    width: 92%;
    margin: 0 auto;
}
</style>
""", unsafe_allow_html=True)

# =========================
# 3. APP LOGIC
# =========================
if "table_names" not in st.session_state:
    st.session_state.table_names = ["Table 1", "Table 2", "Table 3"]

st.title("RESERVE TABLE")

# Date Selection (Swipeable on mobile)
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

# 4. RENDER HEADERS (SPACED)
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
            user_name = match.iloc[0]["Name"]
            # LIGHT RED SLOT
            col.button(f"{t} | {user_name}", key=key, disabled=True)
        else:
            # GREEN SLOT
            if col.button(f"{t} 🟢", key=key):
                new_row = pd.DataFrame([[st.session_state.get("user", "guest"), "Me", str(selected_date), t_name, t]], 
                                     columns=["User", "Name", "Date", "Table", "Time"])
                save_bookings(pd.concat([df, new_row]))
                st.rerun()

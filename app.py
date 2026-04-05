import os
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

st.set_page_config(page_title="Pool Booking", layout="wide")

# =========================
# CSS (FORCE 3 COLUMNS & TIGHT ROWS)
# =========================
st.markdown("""
<style>
/* FORCE 3 COLUMNS ON MOBILE */
[data-testid="stHorizontalBlock"] {
    display: flex !important;
    flex-direction: row !important;
    flex-wrap: nowrap !important;
    gap: 5px !important;
}

[data-testid="column"] {
    width: 33% !important;
    flex: 1 1 33% !important;
    min-width: 33% !important;
}

/* FIX DATE PICKER VERTICAL TEXT */
[data-testid="stRadio"] > div {
    display: flex !important;
    flex-wrap: wrap !important;
    gap: 10px !important;
}
[data-testid="stRadio"] label {
    white-space: nowrap !important;
}

/* TIGHTEN ROWS (REMOVE GAPS) */
[data-testid="column"] > div {
    padding: 0px !important;
    margin-bottom: -12px !important; /* Forces rows closer */
}

.stButton button {
    width: 100% !important;
    height: 30px !important;
    font-size: 11px !important;
    padding: 0px !important;
    border-radius: 20px !important;
}

/* HEADER STYLE & SPACING */
.table-header-box {
    text-align: center;
    font-weight: bold;
    background-color: #000000;
    color: white;
    padding: 10px 5px;
    border-radius: 5px;
    margin-bottom: 25px; /* Creates space between header and first row */
}

/* 4-HOUR GROUPING BACKGROUNDS */
.hour-group-0 { background-color: rgba(255, 255, 255, 0.05); } /* 08:00 - 12:00 */
.hour-group-1 { background-color: rgba(0, 0, 0, 0.0); }        /* 12:00 - 16:00 */
.hour-group-2 { background-color: rgba(255, 255, 255, 0.05); } /* 16:00 - 20:00 */
/* etc... */

</style>
""", unsafe_allow_html=True)

# =========================
# DATA HELPERS
# =========================
if "table_names" not in st.session_state:
    st.session_state.table_names = ["Table 1", "Table 2", "Table 3"]

def load_bookings():
    if os.path.exists("bookings.csv"):
        return pd.read_csv("bookings.csv")
    return pd.DataFrame(columns=["User","Name","Date","Table","Time"])

# =========================
# MAIN UI
# =========================
st.title("RESERVE TABLE")

# Renamable Table Headers (Admin section)
with st.expander("⚙️ Rename Tables"):
    for i in range(3):
        st.session_state.table_names[i] = st.text_input(f"Table {i+1} Name", st.session_state.table_names[i])

# Date Selection
today = datetime.now().date()
dates = [today + timedelta(days=i) for i in range(14)]
labels = [d.strftime("%a %d") for d in dates]
selected_label = st.radio("", labels, horizontal=True)
selected_date = dates[labels.index(selected_label)]

df = load_bookings()

# Time range
HOURS = []
for h in list(range(8, 24)) + list(range(0, 3)):
    for m in ["00", "30"]:
        HOURS.append(f"{h:02d}:{m}")

# 1. RENDER HEADERS
h_cols = st.columns(3)
for i, col in enumerate(h_cols):
    col.markdown(f"<div class='table-header-box'>{st.session_state.table_names[i]}</div>", unsafe_allow_html=True)

# 2. RENDER TIME ROWS
for t in HOURS:
    hour_int = int(t.split(":")[0])
    # Logic: Group by 4-hour chunks
    # (h-8) because we start at 08:00. 
    # Use // 4 to get groups (08-11:59 = group 0, 12-15:59 = group 1)
    group_idx = ((hour_int - 8) % 24) // 4
    
    # We apply the background color using a container style if needed, 
    # but for simple buttons, let's keep the grid clean.
    
    t_cols = st.columns(3)
    for i, col in enumerate(t_cols):
        t_name = st.session_state.table_names[i]
        key = f"btn_{i}_{t}_{selected_date}"
        
        # Filter booking
        match = df[(df["Table"] == t_name) & (df["Time"] == t) & (df["Date"] == str(selected_date))]
        
        if not match.empty:
            user_name = match.iloc[0]["Name"]
            is_me = match.iloc[0]["User"] == st.session_state.get("user", "")
            btn_label = f"{t} ❌ {user_name}" if is_me else f"{t} 🔒 {user_name}"
            col.button(btn_label, key=key, disabled=not is_me)
        else:
            if col.button(f"{t} 🟢", key=key):
                # Save booking logic here
                st.success(f"Booked {t}")

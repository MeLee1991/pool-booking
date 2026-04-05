import os
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

st.set_page_config(page_title="Pool Booking", layout="wide")

# =========================
# 1. DATABASE & SESSION (STABLE)
# =========================
BOOKINGS_FILE = "bookings.csv"

def load_bookings():
    if os.path.exists(BOOKINGS_FILE):
        return pd.read_csv(BOOKINGS_FILE)
    return pd.DataFrame(columns=["User","Name","Date","Table","Time"])

def save_bookings(df):
    df.to_csv(BOOKINGS_FILE, index=False)

if "user" not in st.session_state:
    st.session_state.user = "user@example.com" # Mock user for testing
    st.session_state.name = "Player 1"
if "table_names" not in st.session_state:
    st.session_state.table_names = ["Table 1", "Table 2", "Table 3"]

# =========================
# 2. CSS (STRICT 3-COL & SLOTS)
# =========================
st.markdown("""
<style>
/* FORCE 3 COLUMNS & NARROW WIDTH */
[data-testid="column"] {
    flex: 0 0 30% !important;
    min-width: 80px !important;
    max-width: 100px !important;
    padding: 0px !important;
    margin: 0 auto !important;
}

[data-testid="stHorizontalBlock"] {
    justify-content: center !important;
    gap: 5px !important;
}

/* BUTTONS AS CLICKABLE SLOTS */
.stButton button {
    width: 100% !important;
    height: 45px !important;
    font-size: 10px !important;
    border: 1px solid #ddd !important;
    border-radius: 6px !important;
    white-space: pre-wrap !important;
    line-height: 1.2 !important;
    display: block !important;
    margin-bottom: -15px !important;
}

/* CLICKABLE (GREEN) */
div.stButton > button:not(:disabled) {
    background-color: #f0fdf4 !important;
    color: #166534 !important;
}

/* BOOKED (RED) */
div.stButton > button:disabled {
    background-color: #fee2e2 !important;
    color: #991b1b !important;
    opacity: 1 !important;
}

/* HEADER */
.table-header {
    text-align: center;
    font-weight: bold;
    font-size: 11px;
    background: #111;
    color: #fff;
    padding: 6px 0;
    margin-bottom: 30px;
    border-radius: 4px;
}
</style>
""", unsafe_allow_html=True)

# =========================
# 3. UI CONTROLS
# =========================
st.title("RESERVE TABLE")

# Date Picker
today = datetime.now().date()
dates = [today + timedelta(days=i) for i in range(14)]
labels = [d.strftime("%a %d") for d in dates]
selected_label = st.radio("", labels, horizontal=True)
selected_date = dates[labels.index(selected_label)]

# Rename Tables
with st.expander("⚙️ Rename Tables"):
    for i in range(3):
        st.session_state.table_names[i] = st.text_input(f"Rename Table {i+1}", st.session_state.table_names[i])

# =========================
# 4. THE BOOKING GRID
# =========================
df = load_bookings()

# Table Headers
h_cols = st.columns(3)
for i, col in enumerate(h_cols):
    col.markdown(f"<div class='table-header'>{st.session_state.table_names[i]}</div>", unsafe_allow_html=True)

# Generate Time Slots
HOURS = []
for h in list(range(8, 24)) + list(range(0, 3)):
    for m in ["00", "30"]:
        HOURS.append(f"{h:02d}:{m}")

for t in HOURS:
    t_cols = st.columns(3)
    for i, col in enumerate(t_cols):
        t_name = st.session_state.table_names[i]
        
        # Look for existing booking
        match = df[(df["Table"] == t_name) & (df["Time"] == t) & (df["Date"] == str(selected_date))]
        
        btn_key = f"btn_{t_name}_{t}_{selected_date}"
        
        if not match.empty:
            # BOOKED SLOT (Disabled)
            u_name = match.iloc[0]["Name"]
            col.button(f"{t}\n{u_name[:8]}", key=btn_key, disabled=True)
        else:
            # CLICKABLE SLOT
            if col.button(f"{t}\n🟢", key=btn_key):
                new_row = pd.DataFrame([{
                    "User": st.session_state.user,
                    "Name": st.session_state.name,
                    "Date": str(selected_date),
                    "Table": t_name,
                    "Time": t
                }])
                df = pd.concat([df, new_row], ignore_index=True)
                save_bookings(df)
                st.rerun()

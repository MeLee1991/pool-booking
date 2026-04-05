import os
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

st.set_page_config(page_title="Pool Booking", layout="wide")

# =========================
# FILES & CONFIG
# =========================
USERS_FILE = "users.csv"
BOOKINGS_FILE = "bookings.csv"

def load_users():
    if os.path.exists(USERS_FILE):
        df = pd.read_csv(USERS_FILE)
        return df
    return pd.DataFrame(columns=["Email","Name","Password","Role"])

def save_users(df):
    df.to_csv(USERS_FILE, index=False)

def load_bookings():
    if os.path.exists(BOOKINGS_FILE):
        return pd.read_csv(BOOKINGS_FILE)
    return pd.DataFrame(columns=["User","Name","Date","Table","Time"])

def save_bookings(df):
    df.to_csv(BOOKINGS_FILE, index=False)

# =========================
# SESSION STATE
# =========================
if "user" not in st.session_state:
    st.session_state.user = None
if "table_names" not in st.session_state:
    st.session_state.table_names = ["Table 1", "Table 2", "Table 3"]

# =========================
# CSS (FIXED & TIGHTENED)
# =========================
st.markdown("""
<style>
/* Fix the Date Picker vertical text issue */
[data-testid="stRadio"] > div {
    display: flex !important;
    flex-wrap: wrap !important;
    gap: 10px !important;
}
[data-testid="stRadio"] label {
    white-space: nowrap !important;
    min-width: 60px;
}

/* Tighten Table Columns and Rows */
[data-testid="stHorizontalBlock"] {
    gap: 0.5rem !important;
}

div[data-testid="column"] {
    padding: 0px 2px !important;
}

/* Shrink button height and margins */
.stButton button {
    margin-bottom: -10px !important;
    padding: 2px 5px !important;
    height: 28px !important;
    font-size: 12px !important;
}

/* Header Spacing */
.table-header {
    text-align: center;
    font-weight: bold;
    background-color: #262730;
    color: white;
    padding: 8px;
    border-radius: 5px;
    margin-bottom: 15px; /* Space between header and table */
}

/* Time Grouping Backgrounds */
.group-a { background-color: rgba(255, 255, 255, 0.05); border-radius: 5px; }
.group-b { background-color: transparent; }

</style>
""", unsafe_allow_html=True)

# =========================
# AUTHENTICATION (Simplified for logic)
# =========================
# ... (Keep your existing Login/Register logic here) ...
# For demonstration, bypassing to show the UI fixes:
if st.session_state.user is None:
    st.session_state.user = "demo@test.com"
    st.session_state.name = "Demo User"
    st.session_state.role = "admin"

# =========================
# MAIN INTERFACE
# =========================
st.title("RESERVE TABLE")

# Date Picker
today = datetime.now().date()
dates = [today + timedelta(days=i) for i in range(14)]
labels = [d.strftime("%a %d") for d in dates]
selected_label = st.radio("Select Date", labels, horizontal=True)
selected_date = dates[labels.index(selected_label)]

# Table Renaming (Editable by Admin)
if st.session_state.role == "admin":
    with st.expander("Edit Table Names"):
        for i in range(3):
            st.session_state.table_names[i] = st.text_input(f"Name for Table {i+1}", st.session_state.table_names[i])

# =========================
# THE GRID
# =========================
df = load_bookings()

# Time range calculation
HOURS = []
for h in list(range(8, 24)) + list(range(0, 3)):
    for m in ["00", "30"]:
        HOURS.append(f"{h:02d}:{m}")

# Header Row
cols = st.columns(3)
for i, col in enumerate(cols):
    col.markdown(f"<div class='table-header'>{st.session_state.table_names[i]}</div>", unsafe_allow_html=True)

# Data Rows
for t in HOURS:
    # Logic for background colors (Changes every 4 hours)
    hour_int = int(t.split(":")[0])
    group_color = "group-a" if (hour_int // 4) % 2 == 0 else "group-b"
    
    # We use a container to apply the background color to the "row"
    row_container = st.container()
    with row_container:
        row_cols = st.columns(3)
        for i, col in enumerate(row_cols):
            table_name = st.session_state.table_names[i]
            booked = df[(df["Table"] == table_name) & (df["Time"] == t) & (df["Date"] == str(selected_date))]
            
            key = f"btn_{i}_{t}_{selected_date}"
            
            if not booked.empty:
                b_name = booked.iloc[0]["Name"]
                icon = "❌" if booked.iloc[0]["User"] == st.session_state.user else "🔒"
                col.button(f"{t} {icon} {b_name}", key=key, disabled=(icon=="🔒"))
            else:
                if col.button(f"{t} 🟢", key=key):
                    new_row = pd.DataFrame([[st.session_state.user, st.session_state.name, str(selected_date), table_name, t]], 
                                         columns=["User","Name","Date","Table","Time"])
                    save_bookings(pd.concat([df, new_row]))
                    st.rerun()

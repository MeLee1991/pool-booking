import os
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

st.set_page_config(page_title="Pool Booking", layout="wide")

# =========================
# 1. DATABASE & SESSION
# =========================
BOOKINGS_FILE = "bookings.csv"

def load_bookings():
    if os.path.exists(BOOKINGS_FILE):
        return pd.read_csv(BOOKINGS_FILE)
    return pd.DataFrame(columns=["User","Name","Date","Table","Time"])

def save_bookings(df):
    df.to_csv(BOOKINGS_FILE, index=False)

if "user" not in st.session_state:
    st.session_state.user = "user@example.com"
    st.session_state.name = "Player"
if "table_names" not in st.session_state:
    st.session_state.table_names = ["Table 1", "Table 2", "Table 3"]

# =========================
# 2. CSS (HARD OVERRIDE)
# =========================
st.markdown("""
<style>
/* FORCE 3 COLUMNS - NO STACKING ON MOBILE */
[data-testid="stHorizontalBlock"] {
    display: grid !important;
    grid-template-columns: repeat(3, 85px) !important; /* STRICT NARROW COLUMNS */
    justify-content: center !important;
    gap: 4px !important;
    width: 100% !important;
}

[data-testid="column"] {
    width: 85px !important;
    flex: none !important;
}

/* SLOTS / BUTTONS STYLE */
.stButton button {
    width: 80px !important; 
    height: 40px !important;
    font-size: 10px !important;
    line-height: 1.1 !important;
    padding: 0px !important;
    border-radius: 4px !important;
    border: 1.5px solid #d1d1d1 !important; /* Visible button border */
    white-space: pre-wrap !important;
    display: block !important;
    margin-bottom: -15px !important; /* Tightens rows */
}

/* BUTTON COLORS */
div.stButton > button:not(:disabled) {
    background-color: #f0fdf4 !important; /* Light Green */
    color: #166534 !important;
    border-color: #dcfce7 !important;
}

div.stButton > button:disabled {
    background-color: #fee2e2 !important; /* Lighter Red */
    color: #991b1b !important;
    opacity: 1 !important;
    border-color: #fecaca !important;
}

/* HEADER STYLE */
.table-header {
    text-align: center;
    font-weight: bold;
    font-size: 10px;
    background: #000;
    color: #fff;
    padding: 5px 0;
    margin-bottom: 30px; /* Space between header and rows */
    border-radius: 4px;
    width: 80px;
}

/* 4-HOUR GROUP BACKGROUNDS */
.bg-group {
    background-color: rgba(0,0,0,0.04);
    border-radius: 5px;
}
</style>
""", unsafe_allow_html=True)

# =========================
# 3. UI & DATE
# =========================
st.title("RESERVE TABLE")

today = datetime.now().date()
dates = [today + timedelta(days=i) for i in range(14)]
labels = [d.strftime("%a %d") for d in dates]
selected_label = st.radio("", labels, horizontal=True)
selected_date = dates[labels.index(selected_label)]

# Table Renaming
with st.expander("⚙️ Rename Tables"):
    for i in range(3):
        st.session_state.table_names[i] = st.text_input(f"Name {i+1}", st.session_state.table_names[i])

# =========================
# 4. GRID GENERATION
# =========================
df = load_bookings()

# Render Table Headers
h_cols = st.columns(3)
for i, col in enumerate(h_cols):
    col.markdown(f"<div class='table-header'>{st.session_state.table_names[i]}</div>", unsafe_allow_html=True)

# Generate Time Slots
HOURS = []
for h in list(range(8, 24)) + list(range(0, 3)):
    for m in ["00", "30"]:
        HOURS.append(f"{h:02d}:{m}")

for t in HOURS:
    # 4-Hour Zebra Striping Logic
    hour_int = int(t.split(":")[0])
    # Shifts 0-3 AM to end of day logic
    adjusted_h = hour_int if hour_int >= 8 else hour_int + 24
    is_alt_bg = ((adjusted_h - 8) // 4) % 2 == 0
    
    # Render the 3 buttons for this time slot
    t_cols = st.columns(3)
    for i, col in enumerate(t_cols):
        t_name = st.session_state.table_names[i]
        match = df[(df["Table"] == t_name) & (df["Time"] == t) & (df["Date"] == str(selected_date))]
        btn_key = f"slot_{i}_{t}_{selected_date}"
        
        # Apply zebra striping to the column div if needed via custom class, 
        # but here we use the button colors to differentiate.
        
        if not match.empty:
            u_name = match.iloc[0]["Name"]
            col.button(f"{t}\n{u_name[:7]}", key=btn_key, disabled=True)
        else:
            if col.button(f"{t}\n🟢", key=btn_key):
                new_entry = pd.DataFrame([{
                    "User": st.session_state.user,
                    "Name": st.session_state.name,
                    "Date": str(selected_date),
                    "Table": t_name,
                    "Time": t
                }])
                df = pd.concat([df, new_entry], ignore_index=True)
                save_bookings(df)
                st.rerun()

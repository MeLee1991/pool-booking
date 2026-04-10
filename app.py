import os
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

# 1. SETUP
st.set_page_config(page_title="Pool", layout="wide", initial_sidebar_state="collapsed")

# 2. DATA
USERS_FILE = "users.csv"
BOOKINGS_FILE = "bookings.csv"

def load_data(file, columns):
    if os.path.exists(file): return pd.read_csv(file, dtype=str)
    return pd.DataFrame(columns=columns)

def save_data(df, file): df.to_csv(file, index=False)

users = load_data(USERS_FILE, ["Email", "Name", "Password", "Role"])
bookings = load_data(BOOKINGS_FILE, ["User", "Name", "Date", "Table", "Time"])

# 3. SESSION STATE
if "user" not in st.session_state: st.session_state.user = None
if "sel_date" not in st.session_state: st.session_state.sel_date = str(datetime.now().date())
if "confirm_delete" not in st.session_state: st.session_state.confirm_delete = None

# 4. CSS (CLEANED UP FOR TIGHT GRID & SCROLLING)
st.markdown("""
<style>
/* 1. PREVENT MOBILE STACKING & TIGHTEN GAPS */
[data-testid="stHorizontalBlock"] {
    display: flex !important;
    flex-wrap: nowrap !important;
    gap: 0.3rem !important; /* Brings columns much closer together */
    align-items: center !important;
}

/* Remove default heavy padding inside Streamlit columns */
[data-testid="column"] {
    padding-left: 0.1rem !important;
    padding-right: 0.1rem !important;
    min-width: 0 !important; /* Prevents columns from expanding unnecessarily */
}

/* 2. BUTTON SIZING & COLORS */
.stButton > button {
    width: 100% !important; 
    height: 35px !important; /* Slightly taller for easier tapping on mobile */
    padding: 0px !important; 
    border-radius: 4px !important; 
    font-weight: bold !important;
    font-size: 13px !important;
}

/* Free Slots (Secondary) -> Light Green */
button[kind="secondary"] { background-color: #e6ffed !important; color: #1a7f37 !important; border: 1px solid #4AC26B !important; }

/* Booked Slots (Primary/Disabled) -> Light Red */
button[kind="primary"], .stButton > button:disabled { 
    background-color: #ffebe9 !important; color: #cf222e !important; 
    border: 1px solid #FF8182 !important; opacity: 1 !important; 
}

/* 3. TEXT & HEADERS */
.time-label { 
    font-size: 12px; 
    font-weight: bold; 
    text-align: center; 
    line-height: 35px; /* Vertically aligns time text with the buttons */
}
.header-box { 
    background: #1E1E1E; 
    color: #fff; 
    text-align: center; 
    font-size: 13px; 
    font-weight: bold;
    padding: 4px;
    border-radius: 4px;
}

/* Constrain overall app width slightly to prevent extreme stretching on large screens */
[data-testid="stAppViewBlockContainer"] { 
    padding: 1rem 0.5rem !important; 
    max-width: 800px; 
}
</style>
""", unsafe_allow_html=True)

# 5. LOGIN
if st.session_state.user is None:
    st.title("🎱 RESERVE")
    e = st.text_input("Email").lower().strip()
    p = st.text_input("Password", type="password")
    if st.button("Login"):
        match = users[(users["Email"] == e) & (users["Password"] == p)]
        if not match.empty:
            st.session_state.user, st.session_state.name, st.session_state.role = e, match.iloc[0]["Name"], match.iloc[0]["Role"]
            st.rerun()
    st.stop()

# 6. DATES (Strictly 2 rows of 7, relying on Streamlit's native equal distribution)
st.write("### 📅 Dates")
today = datetime.now().date()
for r in range(2):
    cols = st.columns(7) # Automatically distributes 7 columns tightly due to our new CSS
    for i in range(7):
        d = today + timedelta(days=i + (r * 7))
        d_str = str(d)
        with cols[i]:
            is_active = (st.session_state.sel_date == d_str)
            if st.button(f"{d.strftime('%a')}\n{d.day}", key=f"d_{d_str}", type="primary" if is_active else "secondary"):
                st.session_state.sel_date = d_str; st.rerun()

# 7. ADMIN/USER CONFIRMATION DIALOG
if st.session_state.confirm_delete:
    idx_to_del, b_name = st.session_state.confirm_delete
    st.warning(f"Confirm Cancellation for {b_name}?")
    c1, c2 = st.columns([1,1])
    if c1.button("Confirm Cancel", type="primary"):
        bookings = bookings.drop(index=int(idx_to_del)); save_data(bookings, BOOKINGS_FILE)
        st.session_state.confirm_delete = None; st.rerun()
    if c2.button("Keep Booking"):
        st.session_state.confirm_delete = None; st.rerun()

st.divider()

# 8. BOOKING TABLE
# --- FIXED HEADERS ---
# Using an array [1.2, 2, 2, 2] makes the first column (times) narrower than the 3 table columns
h_cols = st.columns([1.2, 2, 2, 2])
with h_cols[0]: st.write("") # Empty placeholder above the times
with h_cols[1]: st.markdown('<div class="header-box">T1</div>', unsafe_allow_html=True)
with h_cols[2]: st.markdown('<div class="header-box">T2</div>', unsafe_allow_html=True)
with h_cols[3]: st.markdown('<div class="header-box">T3</div>', unsafe_allow_html=True)

# --- SCROLLING DATA ---
# st.container(height=400) creates a scrollable box. Adjust 400 up or down to fit your screen preference!
schedule_container = st.container(height=450)

HOURS = [f"{h:02d}:{m}" for h in (list(range(8, 24)) + list(range(0, 3))) for m in ["00", "30"]]

with schedule_container:
    for idx, t in enumerate(HOURS):
        # Match the header ratios exactly so they align
        r_cols = st.columns([1.2, 2, 2, 2])
        
        with r_cols[0]: 
            st.markdown(f'<div class="time-label">{t}</div>', unsafe_allow_html=True)
            
        for i in range(3):
            t_n = f"Table {i+1}"
            match = bookings[(bookings["Table"] == t_n) & (bookings["Time"] == t) & (bookings["Date"] == st.session_state.sel_date)]
            with r_cols[i+1]:
                if not match.empty:
                    b_user, b_name = match.iloc[0]["User"], match.iloc[0]["Name"]
                    
                    if st.session_state.user == b_user:
                        if st.button(f"❌ {b_name[:5]}", key=f"b_{t}_{i}", type="primary"):
                            bookings = bookings.drop(match.index); save_data(bookings, BOOKINGS_FILE); st.rerun()
                    elif st.session_state.role == "admin":
                        if st.button(f"🛡️ {b_name[:5]}", key=f"b_{t}_{i}", type="primary"):
                            st.session_state.confirm_delete = (match.index[0], b_name); st.rerun()
                    else:
                        st.button(f"🔒 {b_name[:5]}", key=f"b_{t}_{i}", disabled=True)
                else:
                    if st.button("Free", key=f"b_{t}_{i}", type="secondary"):
                        new_b = pd.DataFrame([{"User":st.session_state.user, "Name":st.session_state.name, "Date":st.session_state.sel_date, "Table":t_n, "Time":t}])
                        save_data(pd.concat([bookings, new_b]), BOOKINGS_FILE); st.rerun()

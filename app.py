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

# 4. ULTRA-COMPACT CSS
st.markdown("""
<style>
/* FORCE 4-COLUMN ROW (Time + 3 Tables) - NO STACKING */
[data-testid="stHorizontalBlock"] {
    display: grid !important;
    grid-template-columns: 42px 60px 60px 60px !important; /* FIXED NARROW WIDTHS */
    gap: 0px !important; /* ZERO SPACE BETWEEN COLUMNS */
    width: fit-content !important;
    border-left: 1px solid #ddd;
}

/* REMOVE ALL INTERNAL PADDING */
[data-testid="column"] { padding: 0px !important; flex: none !important; }

/* ROW STYLING: Borders and Padding */
.row-wrap { 
    border-bottom: 1px solid #ccc; 
    border-right: 1px solid #ddd;
    padding: 2px 0;
}

/* ALTERNATE ROW COLORS (Whole Row) */
.hour-even { background-color: #f9f9f9 !important; }
.hour-odd { background-color: #ffffff !important; }

/* BUTTONS: Shrunk height, exact width */
.stButton > button {
    width: 58px !important; /* Slightly less than 60px to allow for borders */
    height: 28px !important;
    font-size: 9px !important;
    padding: 0px !important;
    border-radius: 0px !important; /* Square for grid look */
    margin: 1px !important;
}

/* TIME BUTTON/LABEL: Extra narrow */
.time-col .stButton > button { width: 40px !important; font-weight: bold; background: none !important; border: none !important; color: #333 !important; }

/* HEADERS: Fixed width black boxes */
.header-box { 
    background: #000; color: #fff; text-align: center; 
    font-size: 9px; height: 20px; line-height: 20px;
    width: 60px; border: 1px solid #444;
}

/* DATE GRID: 7-Column */
.date-section [data-testid="stHorizontalBlock"] {
    grid-template-columns: repeat(7, 44px) !important;
    margin-bottom: -15px !important;
}
.date-section .stButton > button { width: 42px !important; height: 32px !important; }

/* LOGIN */
.login-box .stButton > button { width: 120px !important; height: 40px !important; margin: 0 auto; }

/* PAGE CLEANUP */
[data-testid="stAppViewBlockContainer"] { padding: 0.5rem 0.2rem !important; }
</style>
""", unsafe_allow_html=True)

# 5. LOGIN
if st.session_state.user is None:
    st.title("🎱 RESERVE")
    e = st.text_input("Email").lower().strip()
    p = st.text_input("Password", type="password")
    st.markdown('<div class="login-box">', unsafe_allow_html=True)
    if st.button("Login"):
        match = users[(users["Email"] == e) & (users["Password"] == p)]
        if not match.empty:
            st.session_state.user, st.session_state.name, st.session_state.role = e, match.iloc[0]["Name"], match.iloc[0]["Role"]
            st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# 6. DATES (7-Column Grid)
st.write("### 📅 Dates")
today = datetime.now().date()
for r in range(2):
    st.markdown('<div class="date-section">', unsafe_allow_html=True)
    cols = st.columns(7)
    for i in range(7):
        d = today + timedelta(days=i + (r * 7))
        d_str = str(d)
        with cols[i]:
            lbl = f"{d.strftime('%a')}\n{d.day}"
            is_active = (st.session_state.sel_date == d_str)
            if st.button(lbl, key=f"d_{d_str}", type="primary" if is_active else "secondary"):
                st.session_state.sel_date = d_str; st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

st.divider()

# 7. BOOKING TABLE
# Header Row
st.markdown('<div class="row-wrap">', unsafe_allow_html=True)
h_cols = st.columns(4)
h_cols[0].write("") # Empty corner
for i, name in enumerate(["T1", "T2", "T3"]):
    h_cols[i+1].markdown(f'<div class="header-box">{name}</div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# Schedule
HOURS = [f"{h:02d}:{m}" for h in (list(range(8, 24)) + list(range(0, 3))) for m in ["00", "30"]]

for idx, t in enumerate(HOURS):
    # Toggle color every 2 rows (every full hour)
    row_class = "hour-even" if (idx // 2) % 2 == 0 else "hour-odd"
    
    st.markdown(f'<div class="row-wrap {row_class}">', unsafe_allow_html=True)
    r_cols = st.columns(4)
    
    # Time Column
    with r_cols[0]:
        st.markdown('<div class="time-col">', unsafe_allow_html=True)
        st.button(t, key=f"t_{t}", disabled=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
    # Table Columns
    for i in range(3):
        t_n = f"Table {i+1}"
        match = bookings[(bookings["Table"] == t_n) & (bookings["Time"] == t) & (bookings["Date"] == st.session_state.sel_date)]
        with r_cols[i+1]:
            if not match.empty:
                b_user, b_name = match.iloc[0]["User"], match.iloc[0]["Name"]
                if st.session_state.role == "admin" or b_user == st.session_state.user:
                    if st.button(f"❌{b_name[:3]}", key=f"b_{t}_{i}"):
                        bookings = bookings.drop(match.index); save_data(bookings, BOOKINGS_FILE); st.rerun()
                else: st.button(f"🔒{b_name[:3]}", key=f"b_{t}_{i}", disabled=True)
            else:
                if st.button("Free", key=f"b_{t}_{i}"):
                    new_b = pd.DataFrame([{"User":st.session_state.user, "Name":st.session_state.name, "Date":st.session_state.sel_date, "Table":t_n, "Time":t}])
                    save_data(pd.concat([bookings, new_b]), BOOKINGS_FILE); st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

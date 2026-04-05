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

# 4. PRO CSS (ADJACENT SIBLING TARGETING)
st.markdown("""
<style>
/* Clean up global padding */
[data-testid="stAppViewBlockContainer"] { padding: 1rem 0.5rem !important; }
[data-testid="column"] { padding: 0px !important; }

/* --- DATES GRID (Exactly 7 columns) --- */
.date-marker + div[data-testid="stHorizontalBlock"] {
    display: grid !important;
    grid-template-columns: repeat(7, 46px) !important;
    gap: 2px !important;
    margin-bottom: 5px !important;
    justify-content: left !important;
}
.date-marker + div[data-testid="stHorizontalBlock"] .stButton > button {
    width: 100% !important; height: 35px !important; 
    border-radius: 4px !important; font-size: 10px !important; padding: 0 !important;
}
/* Selected Date Color */
button[kind="primary"] { background-color: #2c3e50 !important; color: #fff !important; border: none !important; }

/* --- TABLE GRID (Exactly 4 columns: 45px + 65px + 65px + 65px) --- */
.table-marker + div[data-testid="stHorizontalBlock"] {
    display: grid !important;
    grid-template-columns: 45px 65px 65px 65px !important;
    gap: 0px !important;
    width: 240px !important; /* Locked width to prevent stretching */
    align-items: center !important;
    border-bottom: 1px solid #ddd;
    border-right: 1px solid #ddd;
    border-left: 1px solid #ddd;
}
/* Header Styling */
.table-marker.header-row + div[data-testid="stHorizontalBlock"] {
    border-top: 1px solid #ddd;
    background-color: #222 !important;
}
/* Alternating Row Colors */
.table-marker.even-row + div[data-testid="stHorizontalBlock"] { background-color: #f8f9fa !important; }
.table-marker.odd-row + div[data-testid="stHorizontalBlock"] { background-color: #ffffff !important; }

/* Table Buttons */
.table-marker + div[data-testid="stHorizontalBlock"] .stButton > button {
    width: 65px !important; height: 32px !important;
    font-size: 11px !important; padding: 0px !important;
    border-radius: 0px !important; margin: 0px !important;
    border: none !important; border-left: 1px solid #ddd !important;
}

/* --- LIGHT GREEN / LIGHT RED LOGIC --- */
/* Free (Light Green) */
.table-marker + div[data-testid="stHorizontalBlock"] button:not(:disabled) {
    background-color: #f6ffed !important;
    color: #389e0d !important;
    font-weight: bold !important;
}
.table-marker + div[data-testid="stHorizontalBlock"] button:not(:disabled):hover {
    background-color: #d9f7be !important;
}

/* Booked/Locked (Light Red) */
.table-marker + div[data-testid="stHorizontalBlock"] button:disabled {
    background-color: #fff1f0 !important;
    color: #cf1322 !important;
    opacity: 1 !important;
}

/* Override for Admin Cancel (Light Red but Clickable) */
.admin-cancel button {
    background-color: #fff1f0 !important;
    color: #cf1322 !important;
    font-weight: bold !important;
}

/* Text Alignment inside Table */
.time-text { font-size: 11px; font-weight: bold; text-align: center; color: #333; height: 32px; line-height: 32px; }
.header-text { font-size: 11px; font-weight: bold; text-align: center; color: #fff; height: 25px; line-height: 25px; border-left: 1px solid #444; }
.header-text.no-border { border-left: none; }
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

# 6. DATES (7 Columns, 2 Rows)
st.write("### 📅 Dates")
today = datetime.now().date()
for r in range(2):
    # Hidden marker tells CSS to style the NEXT st.columns as a 7-day grid
    st.markdown('<div class="date-marker"></div>', unsafe_allow_html=True)
    cols = st.columns(7)
    for i in range(7):
        d = today + timedelta(days=i + (r * 7))
        d_str = str(d)
        with cols[i]:
            is_active = (st.session_state.sel_date == d_str)
            if st.button(f"{d.strftime('%a')}\n{d.day}", key=f"d_{d_str}", type="primary" if is_active else "secondary"):
                st.session_state.sel_date = d_str; st.rerun()

# 7. ADMIN CONFIRMATION DIALOG (Top of table)
if st.session_state.confirm_delete:
    idx_to_del, b_name = st.session_state.confirm_delete
    st.warning(f"Admin Action: Cancel booking for {b_name}?")
    c1, c2 = st.columns(2)
    if c1.button("Yes, Cancel It"):
        bookings = bookings.drop(index=int(idx_to_del)); save_data(bookings, BOOKINGS_FILE)
        st.session_state.confirm_delete = None; st.rerun()
    if c2.button("No, Keep It"):
        st.session_state.confirm_delete = None; st.rerun()

st.divider()

# 8. BOOKING TABLE
# Header Row
st.markdown('<div class="table-marker header-row"></div>', unsafe_allow_html=True)
h_cols = st.columns(4)
with h_cols[0]: st.markdown('<div class="header-text no-border"></div>', unsafe_allow_html=True)
with h_cols[1]: st.markdown('<div class="header-text">T1</div>', unsafe_allow_html=True)
with h_cols[2]: st.markdown('<div class="header-text">T2</div>', unsafe_allow_html=True)
with h_cols[3]: st.markdown('<div class="header-text">T3</div>', unsafe_allow_html=True)

# Hours Schedule
HOURS = [f"{h:02d}:{m}" for h in (list(range(8, 24)) + list(range(0, 3))) for m in ["00", "30"]]

for idx, t in enumerate(HOURS):
    # Alternating row logic (changes every 2 slots = 1 hour)
    row_class = "even-row" if (idx // 2) % 2 == 0 else "odd-row"
    
    # Hidden marker tells CSS to style the NEXT st.columns as a 4-column table row
    st.markdown(f'<div class="table-marker {row_class}"></div>', unsafe_allow_html=True)
    r_cols = st.columns(4)
    
    # Time Column
    with r_cols[0]:
        st.markdown(f'<div class="time-text">{t}</div>', unsafe_allow_html=True)
        
    # Table Columns
    for i in range(3):
        t_n = f"Table {i+1}"
        match = bookings[(bookings["Table"] == t_n) & (bookings["Time"] == t) & (bookings["Date"] == st.session_state.sel_date)]
        with r_cols[i+1]:
            if not match.empty:
                b_user, b_name = match.iloc[0]["User"], match.iloc[0]["Name"]
                if st.session_state.user == b_user:
                    # User cancels their own (Instant)
                    if st.button(f"❌ {b_name[:3]}", key=f"b_{t}_{i}"):
                        bookings = bookings.drop(match.index); save_data(bookings, BOOKINGS_FILE); st.rerun()
                elif st.session_state.role == "admin":
                    # Admin cancels someone else's (Requires Confirmation)
                    st.markdown('<div class="admin-cancel">', unsafe_allow_html=True)
                    if st.button(f"🛡️ {b_name[:3]}", key=f"b_{t}_{i}"):
                        st.session_state.confirm_delete = (match.index[0], b_name); st.rerun()
                    st.markdown('</div>', unsafe_allow_html=True)
                else:
                    # Booked by someone else (Locked)
                    st.button(f"🔒 {b_name[:3]}", key=f"b_{t}_{i}", disabled=True)
            else:
                # Free Slot
                if st.button("Free", key=f"b_{t}_{i}"):
                    new_b = pd.DataFrame([{"User":st.session_state.user, "Name":st.session_state.name, "Date":st.session_state.sel_date, "Table":t_n, "Time":t}])
                    save_data(pd.concat([bookings, new_b]), BOOKINGS_FILE); st.rerun()

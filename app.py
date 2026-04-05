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

# 4. ROCK-SOLID CSS
st.markdown("""
<style>
/* Remove default Streamlit padding */
[data-testid="stAppViewBlockContainer"] { padding: 1rem 0.5rem !important; }
[data-testid="column"] { padding: 0px !important; min-width: 0px !important; }

/* ----------------------------------- */
/* 1. DATES GRID (7 columns)           */
/* ----------------------------------- */
.date-section [data-testid="stHorizontalBlock"] {
    display: grid !important;
    grid-template-columns: repeat(7, 46px) !important;
    gap: 4px !important;
    margin-bottom: 5px !important;
}
.date-section button { 
    width: 100% !important; height: 35px !important; 
    border-radius: 4px !important; font-size: 10px !important; padding: 0 !important;
}
/* Selected Date (Blue) */
.date-section button[kind="primary"] { background-color: #1a73e8 !important; color: #fff !important; border: none !important; }

/* ----------------------------------- */
/* 2. TABLE GRID (4 columns exact)     */
/* ----------------------------------- */
.table-section [data-testid="stHorizontalBlock"] {
    display: grid !important;
    /* First col: 55px (10:00). Next cols: 85px (10 chars) */
    grid-template-columns: 55px 85px 85px 85px !important;
    gap: 2px !important;
    align-items: center !important;
    padding: 2px 0px !important;
}

/* ----------------------------------- */
/* 3. ROW ALTERNATING (Whole Row)      */
/* ----------------------------------- */
/* Using modern :has() to color the parent row based on the time marker */
[data-testid="stHorizontalBlock"]:has(.hour-even) { background-color: #f0f2f6 !important; border-bottom: 1px solid #e0e0e0; }
[data-testid="stHorizontalBlock"]:has(.hour-odd) { background-color: #ffffff !important; border-bottom: 1px solid #e0e0e0; }

.time-label { 
    font-size: 11px; font-weight: bold; text-align: center; 
    height: 32px; line-height: 32px; color: #333; 
}
.header-box { 
    background: #000; color: #fff; text-align: center; 
    font-size: 11px; height: 22px; line-height: 22px; 
}

/* ----------------------------------- */
/* 4. BUTTON COLORS: RED & GREEN       */
/* ----------------------------------- */
.table-section button {
    width: 100% !important; height: 32px !important;
    font-size: 11px !important; padding: 0px !important;
    border-radius: 3px !important; margin: 0px !important;
    font-weight: bold !important;
}

/* FREE (Secondary) -> Light Green */
.table-section button[kind="secondary"] {
    background-color: #e6ffed !important;
    color: #1a7f37 !important;
    border: 1px solid #4AC26B !important;
}

/* BOOKED (Primary or Disabled) -> Light Red */
.table-section button[kind="primary"],
.table-section button:disabled {
    background-color: #ffebe9 !important;
    color: #cf222e !important;
    border: 1px solid #FF8182 !important;
    opacity: 1 !important; /* Force opacity so disabled doesn't look washed out */
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

# 6. DATES (Strictly 2 rows of 7)
st.write("### 📅 Dates")
st.markdown('<div class="date-section">', unsafe_allow_html=True)
today = datetime.now().date()
for r in range(2):
    cols = st.columns(7)
    for i in range(7):
        d = today + timedelta(days=i + (r * 7))
        d_str = str(d)
        with cols[i]:
            is_active = (st.session_state.sel_date == d_str)
            # Primary = Blue (active), Secondary = Gray (inactive)
            if st.button(f"{d.strftime('%a')}\n{d.day}", key=f"d_{d_str}", type="primary" if is_active else "secondary"):
                st.session_state.sel_date = d_str; st.rerun()
st.markdown('</div>', unsafe_allow_html=True)

# 7. ADMIN CONFIRMATION
if st.session_state.confirm_delete:
    idx_to_del, b_name = st.session_state.confirm_delete
    st.warning(f"Admin: Cancel booking for {b_name}?")
    c1, c2 = st.columns(2)
    if c1.button("Yes, Cancel It"):
        bookings = bookings.drop(index=int(idx_to_del)); save_data(bookings, BOOKINGS_FILE)
        st.session_state.confirm_delete = None; st.rerun()
    if c2.button("No, Keep It"):
        st.session_state.confirm_delete = None; st.rerun()

st.divider()

# 8. BOOKING TABLE
st.markdown('<div class="table-section">', unsafe_allow_html=True)

# Header Row
h_cols = st.columns(4)
with h_cols[0]: st.write("")
for i, name in enumerate(["T1", "T2", "T3"]):
    with h_cols[i+1]: st.markdown(f'<div class="header-box">{name}</div>', unsafe_allow_html=True)

# Hours Schedule
HOURS = [f"{h:02d}:{m}" for h in (list(range(8, 24)) + list(range(0, 3))) for m in ["00", "30"]]

for idx, t in enumerate(HOURS):
    # This dictates the row background color
    hour_class = "hour-even" if (idx // 2) % 2 == 0 else "hour-odd"
    
    r_cols = st.columns(4)
    
    # 1st Column: Time
    with r_cols[0]:
        st.markdown(f'<div class="{hour_class} time-label">{t}</div>', unsafe_allow_html=True)
        
    # 2nd-4th Columns: Tables
    for i in range(3):
        t_n = f"Table {i+1}"
        match = bookings[(bookings["Table"] == t_n) & (bookings["Time"] == t) & (bookings["Date"] == st.session_state.sel_date)]
        with r_cols[i+1]:
            if not match.empty:
                b_user, b_name = match.iloc[0]["User"], match.iloc[0]["Name"]
                
                # BOOKED SLOTS -> type="primary" forces the Light Red CSS
                if st.session_state.user == b_user:
                    # User's own booking (Click to cancel)
                    if st.button(f"❌ {b_name[:8]}", key=f"b_{t}_{i}", type="primary"):
                        bookings = bookings.drop(match.index); save_data(bookings, BOOKINGS_FILE); st.rerun()
                elif st.session_state.role == "admin":
                    # Admin viewing (Click to confirm cancel)
                    if st.button(f"🛡️ {b_name[:8]}", key=f"b_{t}_{i}", type="primary"):
                        st.session_state.confirm_delete = (match.index[0], b_name); st.rerun()
                else:
                    # Someone else's booking (Disabled, automatically Light Red via CSS)
                    st.button(f"🔒 {b_name[:8]}", key=f"b_{t}_{i}", disabled=True)
            else:
                # FREE SLOTS -> type="secondary" forces the Light Green CSS
                if st.button("Free", key=f"b_{t}_{i}", type="secondary"):
                    new_b = pd.DataFrame([{"User":st.session_state.user, "Name":st.session_state.name, "Date":st.session_state.sel_date, "Table":t_n, "Time":t}])
                    save_data(pd.concat([bookings, new_b]), BOOKINGS_FILE); st.rerun()

st.markdown('</div>', unsafe_allow_html=True)

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

# 4. CSS (STRICT WIDTHS & CENTERING)
st.markdown("""
<style>
/* Reset and Global Cleanup */
[data-testid="stAppViewBlockContainer"] { padding: 1rem 0.2rem !important; }
[data-testid="column"] { padding: 0px !important; flex: none !important; }

/* ----------------------------------- */
/* 1. DATE PICKER GRID (7 Small Cols)  */
/* ----------------------------------- */
.date-grid [data-testid="stHorizontalBlock"] {
    display: grid !important;
    grid-template-columns: repeat(7, 42px) !important; /* Tiny boxes */
    gap: 3px !important;
    justify-content: start !important;
    margin-bottom: 5px !important;
}
.date-grid button { 
    width: 40px !important; height: 35px !important; 
    font-size: 9px !important; padding: 0 !important;
}

/* ----------------------------------- */
/* 2. MAIN TABLE GRID (Locked Width)   */
/* ----------------------------------- */
.table-grid [data-testid="stHorizontalBlock"] {
    display: grid !important;
    /* Time: 45px | Tables: 75px each (approx 12-15 chars) */
    grid-template-columns: 45px 75px 75px 75px !important;
    gap: 1px !important;
    width: 275px !important; /* FIXED TOTAL WIDTH */
    border-right: 1px solid #ddd;
    border-left: 1px solid #ddd;
}

/* Row Alternation */
.bg-even { background-color: #f1f3f5 !important; }
.bg-odd { background-color: #ffffff !important; }

/* ----------------------------------- */
/* 3. BUTTON STYLING (Centered/Fixed)  */
/* ----------------------------------- */
.table-grid button {
    width: 73px !important; /* Slightly smaller than column for padding effect */
    height: 30px !important;
    font-size: 10px !important;
    margin: 0 auto !important; /* Centered */
    display: block !important;
    border-radius: 2px !important;
}

/* COLORS */
button[kind="secondary"] { background-color: #e6ffed !important; color: #1a7f37 !important; border: 1px solid #b7eb8f !important; }
button[kind="primary"], .table-grid button:disabled { 
    background-color: #fff1f0 !important; color: #cf222e !important; 
    border: 1px solid #ffa39e !important; opacity: 1 !important; 
}

.time-txt { font-size: 10px; font-weight: bold; text-align: center; line-height: 30px; }
.hdr-txt { background: #000; color: #fff; text-align: center; font-size: 10px; height: 20px; line-height: 20px; }
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

# 6. DATES
st.write("📅 **Select Date**")
today = datetime.now().date()
for r in range(2):
    st.markdown('<div class="date-grid">', unsafe_allow_html=True)
    cols = st.columns(7)
    for i in range(7):
        d = today + timedelta(days=i + (r * 7))
        d_str = str(d)
        with cols[i]:
            is_active = (st.session_state.sel_date == d_str)
            if st.button(f"{d.strftime('%a')}\n{d.day}", key=f"d_{d_str}", type="primary" if is_active else "secondary"):
                st.session_state.sel_date = d_str; st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# 7. ADMIN CONFIRMATION
if st.session_state.confirm_delete:
    idx_to_del, b_name = st.session_state.confirm_delete
    st.warning(f"Admin: Cancel {b_name}?")
    c1, c2 = st.columns(2)
    if c1.button("Confirm"):
        bookings = bookings.drop(index=int(idx_to_del)); save_data(bookings, BOOKINGS_FILE)
        st.session_state.confirm_delete = None; st.rerun()
    if c2.button("Keep"):
        st.session_state.confirm_delete = None; st.rerun()

st.divider()

# 8. BOOKING TABLE
st.markdown('<div class="table-grid">', unsafe_allow_html=True)

# Header
h_cols = st.columns(4)
with h_cols[1]: st.markdown('<div class="hdr-txt">T1</div>', unsafe_allow_html=True)
with h_cols[2]: st.markdown('<div class="hdr-txt">T2</div>', unsafe_allow_html=True)
with h_cols[3]: st.markdown('<div class="hdr-txt">T3</div>', unsafe_allow_html=True)

# Schedule
HOURS = [f"{h:02d}:{m}" for h in (list(range(8, 24)) + list(range(0, 3))) for m in ["00", "30"]]

for idx, t in enumerate(HOURS):
    row_style = "bg-even" if (idx // 2) % 2 == 0 else "bg-odd"
    st.markdown(f'<div class="{row_style}">', unsafe_allow_html=True)
    r_cols = st.columns(4)
    
    with r_cols[0]: st.markdown(f'<div class="time-txt">{t}</div>', unsafe_allow_html=True)
        
    for i in range(3):
        t_n = f"Table {i+1}"
        match = bookings[(bookings["Table"] == t_n) & (bookings["Time"] == t) & (bookings["Date"] == st.session_state.sel_date)]
        with r_cols[i+1]:
            if not match.empty:
                b_user, b_name = match.iloc[0]["User"], match.iloc[0]["Name"]
                # Admin/User Logic
                if st.session_state.user == b_user:
                    if st.button(f"X {b_name[:6]}", key=f"b_{t}_{i}", type="primary"):
                        bookings = bookings.drop(match.index); save_data(bookings, BOOKINGS_FILE); st.rerun()
                elif st.session_state.role == "admin":
                    if st.button(f"A {b_name[:6]}", key=f"b_{t}_{i}", type="primary"):
                        st.session_state.confirm_delete = (match.index[0], b_name); st.rerun()
                else:
                    st.button(f"L {b_name[:6]}", key=f"b_{t}_{i}", disabled=True)
            else:
                if st.button("Free", key=f"b_{t}_{i}", type="secondary"):
                    new_b = pd.DataFrame([{"User":st.session_state.user, "Name":st.session_state.name, "Date":st.session_state.sel_date, "Table":t_n, "Time":t}])
                    save_data(pd.concat([bookings, new_b]), BOOKINGS_FILE); st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

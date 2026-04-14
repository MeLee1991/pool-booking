import streamlit as st
import pandas as pd
import os
from datetime import datetime, timedelta

st.set_page_config(page_title="Poolhall", layout="centered", initial_sidebar_state="collapsed")

# ===============================
# CONFIG & FILES
# ===============================
USERS_FILE = "users.csv"
BOOKINGS_FILE = "bookings.csv"
OWNER_EMAIL = "admin@gmail.com"

# ===============================
# THE MASTER CSS GRID
# ===============================
st.markdown("""
<style>
    /* 1. App Spacing */
    .block-container { padding: 1rem 4px !important; max-width: 100% !important; }
    
    /* 2. FORCE STRICT GRID ON ALL COLUMNS */
    div[data-testid="stHorizontalBlock"] {
        display: grid !important;
        gap: 4px !important;
        margin-bottom: 4px !important;
        width: 100% !important;
    }
    div[data-testid="column"] { min-width: 0 !important; width: 100% !important; flex: none !important; }

    /* 3. TARGET SPECIFIC ROWS BY INDEX */
    /* Rows 1 & 2: The 14-Day Date Selectors (7 columns) */
    div[data-testid="stHorizontalBlock"]:nth-of-type(1),
    div[data-testid="stHorizontalBlock"]:nth-of-type(2) {
        grid-template-columns: repeat(7, 1fr) !important;
    }

    /* Row 3: The Header Row (4 columns) - With Bottom Gap! */
    div[data-testid="stHorizontalBlock"]:nth-of-type(3) {
        grid-template-columns: repeat(4, 1fr) !important;
        margin-bottom: 20px !important; 
    }

    /* Rows 4+: The Main Table Data (4 columns) */
    div[data-testid="stHorizontalBlock"]:nth-of-type(n+4) {
        grid-template-columns: repeat(4, 1fr) !important;
    }

    /* 4. UNIFORM BUTTON SIZES & TEXT */
    .stButton > button {
        width: 100% !important;
        height: 44px !important; 
        padding: 0 !important;
        border-radius: 6px !important;
        border: 1px solid rgba(0,0,0,0.05) !important;
        box-shadow: 0 1px 2px rgba(0,0,0,0.1) !important;
    }
    .stButton > button p {
        font-size: 11px !important;
        font-weight: 800 !important;
        line-height: 1.2 !important;
        white-space: pre-wrap !important; /* Allows multi-line text for dates */
        margin: 0 !important;
    }

    /* 5. COLOR CODING THE BUTTONS */
    /* Date Buttons (Gray unselected, Blue selected) */
    div[data-testid="stHorizontalBlock"]:nth-of-type(1) button[kind="secondary"],
    div[data-testid="stHorizontalBlock"]:nth-of-type(2) button[kind="secondary"] {
        background-color: #f0f2f6 !important; color: #333 !important;
    }
    div[data-testid="stHorizontalBlock"]:nth-of-type(1) button[kind="primary"],
    div[data-testid="stHorizontalBlock"]:nth-of-type(2) button[kind="primary"] {
        background-color: #5c6bc0 !important; color: white !important;
    }

    /* Table Buttons (Green Free, Red Booked) */
    div[data-testid="stHorizontalBlock"]:nth-of-type(n+4) button[kind="secondary"] {
        background-color: #a5d6a7 !important; /* FREE = GREEN */
        color: #1b5e20 !important;
    }
    div[data-testid="stHorizontalBlock"]:nth-of-type(n+4) button[kind="primary"] {
        background-color: #ef5350 !important; /* BOOKED = RED */
        color: white !important;
    }

    /* 6. TIME COLUMN LABELS (Pastel blocks) */
    .time-label {
        height: 44px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 12px;
        font-weight: 800;
        border-radius: 6px;
        color: #333;
    }
    .t-blue { background-color: #e3f2fd; } 
    .t-yellow { background-color: #fff9c4; } 
    .t-orange { background-color: #ffe0b2; } 
    .t-purple { background-color: #f3e5f5; } 

    /* 7. HEADERS */
    .grid-header {
        background-color: #111;
        color: #fff;
        text-align: center;
        font-size: 12px;
        font-weight: bold;
        height: 40px;
        line-height: 40px;
        border-radius: 6px;
    }

    /* Hide default streamlit header */
    [data-testid="stHeader"] {display: none;}
</style>
""", unsafe_allow_html=True)

# ===============================
# DATA HELPERS
# ===============================
def load_data(file, cols):
    if not os.path.exists(file): pd.DataFrame(columns=cols).to_csv(file, index=False)
    try: return pd.read_csv(file)
    except: return pd.DataFrame(columns=cols)

def save_data(df, file): df.to_csv(file, index=False)

# ===============================
# LOGIN SYSTEM
# ===============================
if "user" not in st.session_state:
    st.markdown("<h2 style='text-align:center;'>🎱 Pool Login</h2>", unsafe_allow_html=True)
    email = st.text_input("Email").lower()
    pw = st.text_input("Password", type="password")
    
    if st.button("Continue", use_container_width=True):
        if email and pw == "1234":
            st.session_state.user = email
            st.session_state.name = email.split('@')[0].capitalize()
            st.session_state.role = "admin" if email == OWNER_EMAIL else "user"
            st.rerun()
        else: st.error("Wrong password. Use '1234'.")
    st.stop()

# ===============================
# APP HEADER
# ===============================
if "sel_date" not in st.session_state: 
    st.session_state.sel_date = datetime.now().date()

# Top text 
st.markdown(f"**👤 {st.session_state.name}** &nbsp;|&nbsp; {st.session_state.sel_date}")

# ===============================
# 14-DAY SELECTOR (Exactly 2 Rows)
# ===============================
today = datetime.now().date()
dates = [today + timedelta(days=i) for i in range(14)]

# ROW 1 (Next 7 days)
d_cols1 = st.columns(7)
for i in range(7):
    d = dates[i]
    lbl = f"TOD\n{d.day}" if d == today else f"TOM\n{d.day}" if d == today + timedelta(days=1) else f"{d.strftime('%a').upper()}\n{d.day}"
    with d_cols1[i]:
        if st.button(lbl, key=f"d_{d}", type="primary" if d == st.session_state.sel_date else "secondary"):
            st.session_state.sel_date = d; st.rerun()

# ROW 2 (Following 7 days)
d_cols2 = st.columns(7)
for i in range(7, 14):
    d = dates[i]
    lbl = f"{d.strftime('%a').upper()}\n{d.day}"
    with d_cols2[i - 7]:
        if st.button(lbl, key=f"d_{d}", type="primary" if d == st.session_state.sel_date else "secondary"):
            st.session_state.sel_date = d; st.rerun()

# ===============================
# MAIN TABLE
# ===============================
times = [f"{h:02d}:{m}" for h in range(6, 24) for m in ("00","30")]
tables = ["T1", "T2", "T3"]
bookings = load_data(BOOKINGS_FILE, ["user", "date", "table", "time"])
df_day = bookings[bookings["date"] == str(st.session_state.sel_date)]

# TABLE HEADER (Row 3)
h_cols = st.columns(4)
for title in ["Time", "T1", "T2", "T3"]:
    with h_cols[["Time", "T1", "T2", "T3"].index(title)]:
        st.markdown(f"<div class='grid-header'>{title}</div>", unsafe_allow_html=True)

# TABLE DATA (Rows 4+)
for t in times:
    r_cols = st.columns(4)
    
    # Time Colors
    h_int = int(t[:2])
    if 6 <= h_int < 10: c_cls = "t-blue"
    elif 10 <= h_int < 14: c_cls = "t-yellow"
    elif 14 <= h_int < 18: c_cls = "t-orange"
    else: c_cls = "t-purple"
    
    with r_cols[0]:
        st.markdown(f"<div class='time-label {c_cls}'>{t}</div>", unsafe_allow_html=True)
        
    for i, table in enumerate(tables):
        with r_cols[i+1]:
            match = df_day[(df_day["table"] == table) & (df_day["time"] == t)]
            if not match.empty:
                owner = match.iloc[0]["user"]
                is_me_or_admin = (owner == st.session_state.user) or (st.session_state.role == "admin")
                display_name = owner.split("@")[0].capitalize()[:6] if is_me_or_admin else ""
                label = f"X {display_name}" if is_me_or_admin else "🔒"
                
                # type="primary" forces RED color via our CSS
                if st.button(label, key=f"b_{table}_{t}", type="primary"):
                    if is_me_or_admin:
                        new_df = bookings[~((bookings["table"]==table) & (bookings["time"]==t) & (bookings["date"]==str(st.session_state.sel_date)))]
                        save_data(new_df, BOOKINGS_FILE); st.rerun()
            else:
                # type="secondary" forces GREEN color via our CSS
                if st.button("➕", key=f"b_{table}_{t}", type="secondary"):
                    new_row = pd.DataFrame([[st.session_state.user, str(st.session_state.sel_date), table, t]], columns=bookings.columns)
                    save_data(pd.concat([bookings, new_row]), BOOKINGS_FILE); st.rerun()

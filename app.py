import streamlit as st
import pandas as pd
import os
from datetime import datetime, timedelta

st.set_page_config(page_title="Poolhall", layout="centered", initial_sidebar_state="collapsed")

# ===============================
# CONFIG & ADMIN
# ===============================
USERS_FILE = "users.csv"
BOOKINGS_FILE = "bookings.csv"
OWNER_EMAIL = "admin@gmail.com" # This is your Admin account

# ===============================
# ULTRA-STRICT CSS
# ===============================
st.markdown("""
<style>
/* 1. Reset App Spacing */
.block-container {
    padding: 1rem 5px !important;
    max-width: 100% !important;
}

/* 2. FIXED 4-COLUMN GRID (No Stacking) */
div[data-testid="stHorizontalBlock"] {
    display: grid !important;
    grid-template-columns: repeat(4, 1fr) !important; 
    gap: 4px !important;
    margin-bottom: 2px !important; /* Tightens vertical row gap */
}

/* 3. BUTTON STYLING (Fixed width for 10 chars) */
.stButton > button {
    width: 100% !important;
    height: 38px !important;
    padding: 0 !important;
    border-radius: 4px !important;
    border: 1px solid #ddd !important;
}

.stButton > button p {
    font-size: 11px !important;
    font-weight: bold !important;
    white-space: nowrap !important;
    overflow: hidden !important;
    text-overflow: ellipsis !important;
}

/* 4. HEADERS & SPACING */
.grid-header {
    background-color: #000;
    color: #fff;
    text-align: center;
    font-size: 12px;
    font-weight: bold;
    height: 40px;
    line-height: 40px;
    border-radius: 4px;
    margin-bottom: 8px; /* Gap between header and table */
}

/* 5. TIME BUTTON COLORS */
/* We simulate time buttons with markdown to ensure color stays */
.time-btn {
    height: 38px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 12px;
    font-weight: bold;
    border-radius: 4px;
    border: 1px solid #ccc;
    color: #000;
}
.t-white { background-color: #ffffff; }
.t-gray { background-color: #f0f2f5; }

/* 6. HIDE ELEMENTS */
[data-testid="stHeader"] {display: none;}
</style>
""", unsafe_allow_html=True)

# ===============================
# CORE FUNCTIONS
# ===============================
def load_data(file, cols):
    if not os.path.exists(file): pd.DataFrame(columns=cols).to_csv(file, index=False)
    try:
        df = pd.read_csv(file)
        return df if not df.empty and cols[0] in df.columns else pd.DataFrame(columns=cols)
    except: return pd.DataFrame(columns=cols)

def save_data(df, file): df.to_csv(file, index=False)

# ===============================
# LOGIN PAGE
# ===============================
if "user" not in st.session_state:
    st.markdown("### 🎱 Pool Login")
    email = st.text_input("Email").lower()
    pw = st.text_input("Password", type="password")
    
    if st.button("Continue"):
        # Temporary easy access: any password works for now, or use '1234'
        if email:
            st.session_state.user = email
            st.session_state.name = email.split('@')[0].capitalize()
            st.session_state.role = "admin" if email == OWNER_EMAIL else "user"
            st.rerun()
    st.stop()

# ===============================
# NAVIGATION
# ===============================
if "selected_date" not in st.session_state:
    st.session_state.selected_date = datetime.now().date()

# Simple Date Nav
c1, c2, c3 = st.columns([1,2,1])
with c1: 
    if st.button("⬅️"): st.session_state.selected_date -= timedelta(days=1); st.rerun()
with c2: st.markdown(f"<center><b>{st.session_state.selected_date}</b></center>", unsafe_allow_html=True)
with c3: 
    if st.button("➡️"): st.session_state.selected_date += timedelta(days=1); st.rerun()

if st.session_state.role == "admin":
    if st.button("⚙️ Admin Panel"): st.info("Admin functionality goes here.")

# ===============================
# MAIN TABLE
# ===============================
times = [f"{h:02d}:{m}" for h in range(6, 24) for m in ("00","30")]
tables = ["T1", "T2", "T3"]
bookings = load_data(BOOKINGS_FILE, ["user", "date", "table", "time"])
df_day = bookings[bookings["date"] == str(st.session_state.selected_date)]

# Header
h_cols = st.columns(4)
titles = ["Time", "T1", "T2", "T3"]
for i, title in enumerate(titles):
    with h_cols[i]: st.markdown(f"<div class='grid-header'>{title}</div>", unsafe_allow_html=True)

# Data Rows
for t in times:
    r_cols = st.columns(4)
    
    # Time Color (Alternating 4-hour blocks)
    hour = int(t[:2])
    color_class = "t-white" if (hour // 4) % 2 == 0 else "t-gray"
    
    with r_cols[0]:
        st.markdown(f"<div class='time-btn {color_class}'>{t}</div>", unsafe_allow_html=True)
        
    for i, table in enumerate(tables):
        with r_cols[i+1]:
            match = df_day[(df_day["table"] == table) & (df_day["time"] == t)]
            if not match.empty:
                owner = match.iloc[0]["user"]
                is_me = owner == st.session_state.user
                label = f"X {st.session_state.name[:8]}" if is_me else "🔒"
                
                if st.button(label, key=f"b_{table}_{t}", type="primary" if is_me else "secondary"):
                    if is_me:
                        new_df = bookings[~((bookings["table"]==table) & (bookings["time"]==t) & (bookings["date"]==str(st.session_state.selected_date)))]
                        save_data(new_df, BOOKINGS_FILE)
                        st.rerun()
            else:
                if st.button("➕", key=f"b_{table}_{t}"):
                    new_row = pd.DataFrame([[st.session_state.user, str(st.session_state.selected_date), table, t]], columns=bookings.columns)
                    save_data(pd.concat([bookings, new_row]), BOOKINGS_FILE)
                    st.rerun()

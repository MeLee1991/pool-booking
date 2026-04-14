import streamlit as st
import pandas as pd
import os
from datetime import datetime, timedelta

st.set_page_config(page_title="Poolhall", layout="centered", initial_sidebar_state="collapsed")

# ===============================
# FILES & INIT (Fixes KeyError)
# ===============================
USERS_FILE = "users.csv"
BOOKINGS_FILE = "bookings.csv"

def load_data(file, columns):
    if not os.path.exists(file):
        pd.DataFrame(columns=columns).to_csv(file, index=False)
    try:
        df = pd.read_csv(file)
        if df.empty or columns[0] not in df.columns:
            return pd.DataFrame(columns=columns)
        return df
    except:
        return pd.DataFrame(columns=columns)

# ===============================
# THE "NO-STACKING" CSS
# ===============================
st.markdown("""
<style>
/* 1. Eliminate all side padding to give columns room */
.block-container {
    padding: 1rem 5px !important;
    max-width: 100% !important;
}

/* 2. FORCE 4 COLUMNS - NO WRAPPING */
/* We target the horizontal block and force it into a 4-column grid */
div[data-testid="stHorizontalBlock"] {
    display: grid !important;
    grid-template-columns: repeat(4, 1fr) !important;
    gap: 4px !important;
    flex-wrap: nowrap !important;
}

/* 3. RESET COLUMN DEFAULTS */
div[data-testid="column"] {
    width: 100% !important;
    min-width: 0 !important;
    flex: none !important;
}

/* 4. BUTTONS - FIXED HEIGHT & TRUNCATED TEXT */
.stButton > button {
    width: 100% !important;
    height: 40px !important;
    padding: 0 !important;
    border-radius: 4px !important;
}

.stButton > button p {
    font-size: 10px !important; /* Tiny font to fit names */
    white-space: nowrap !important;
    overflow: hidden !important;
    text-overflow: ellipsis !important;
}

/* 5. TIME CELLS & HEADERS */
.grid-header {
    background-color: #000;
    color: #fff;
    text-align: center;
    font-size: 11px;
    font-weight: bold;
    padding: 10px 0;
    border-radius: 4px;
}

.time-cell {
    height: 40px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 11px;
    font-weight: bold;
    border-radius: 4px;
    border: 1px solid #ddd;
}

/* Light alternating 4-hour colors */
.bg-light { background-color: #ffffff; }
.bg-dark { background-color: #f0f2f5; }

</style>
""", unsafe_allow_html=True)

# ===============================
# APP LOGIC
# ===============================
if "user" not in st.session_state:
    st.session_state.user = None
if "selected_date" not in st.session_state:
    st.session_state.selected_date = datetime.now().date()

# Simple Login for Demo
if not st.session_state.user:
    email = st.text_input("Email")
    name = st.text_input("Name")
    if st.button("Login"):
        st.session_state.user = email
        st.session_state.name = name
        st.rerun()
    st.stop()

# Date Picker (Simplified to avoid layout conflicts)
st.write(f"Logged in as: **{st.session_state.name}**")
d_col1, d_col2 = st.columns(2)
with d_col1:
    if st.button("⬅️ Prev Day"):
        st.session_state.selected_date -= timedelta(days=1)
        st.rerun()
with d_col2:
    if st.button("Next Day ➡️"):
        st.session_state.selected_date += timedelta(days=1)
        st.rerun()

st.markdown(f"### {st.session_state.selected_date}")

# ===============================
# MAIN TABLE
# ===============================
times = [f"{h:02d}:{m}" for h in range(6, 24) for m in ("00","30")]
tables = ["T1", "T2", "T3"]

# Header Row
h_cols = st.columns(4)
titles = ["Time", "T1", "T2", "T3"]
for i, title in enumerate(titles):
    with h_cols[i]:
        st.markdown(f"<div class='grid-header'>{title}</div>", unsafe_allow_html=True)

# Data Rows
bookings = load_data(BOOKINGS_FILE, ["user", "date", "table", "time"])
df_day = bookings[bookings["date"] == str(st.session_state.selected_date)]

for t in times:
    r_cols = st.columns(4)
    
    # Color logic
    hour = int(t[:2])
    color_class = "bg-light" if (hour // 4) % 2 == 0 else "bg-dark"
    
    with r_cols[0]:
        st.markdown(f"<div class='time-cell {color_class}'>{t}</div>", unsafe_allow_html=True)
        
    for i, table in enumerate(tables):
        with r_cols[i+1]:
            match = df_day[(df_day["table"] == table) & (df_day["time"] == t)]
            if not match.empty:
                owner = match.iloc[0]["user"]
                btn_label = f"X {st.session_state.name}" if owner == st.session_state.user else "🔒"
                if st.button(btn_label, key=f"{table}_{t}"):
                    # Delete logic here
                    pass
            else:
                if st.button("+", key=f"{table}_{t}"):
                    # Save logic here
                    pass

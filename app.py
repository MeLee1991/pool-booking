import os
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

st.set_page_config(page_title="Pool", layout="centered")

# ================= DATA =================
USERS_FILE = "users.csv"
BOOKINGS_FILE = "bookings.csv"

def load_data(file, cols):
    if os.path.exists(file):
        return pd.read_csv(file, dtype=str)
    return pd.DataFrame(columns=cols)

def save_data(df, file):
    df.to_csv(file, index=False)

users = load_data(USERS_FILE, ["Email","Name","Password","Role"])
bookings = load_data(BOOKINGS_FILE, ["User","Name","Date","Table","Time"])

# ================= SESSION =================
if "user" not in st.session_state:
    st.session_state.user = None
if "name" not in st.session_state:
    st.session_state.name = None
if "role" not in st.session_state:
    st.session_state.role = None
if "sel_date" not in st.session_state:
    st.session_state.sel_date = str(datetime.now().date())

# ================= LOGIN =================
if st.session_state.user is None:
    st.title("Pool")

    e = st.text_input("Email")
    p = st.text_input("Password", type="password")

    if st.button("Login"):
        m = users[(users["Email"]==e)&(users["Password"]==p)]
        if not m.empty:
            st.session_state.user = e
            st.session_state.name = m.iloc[0]["Name"]
            st.session_state.role = m.iloc[0]["Role"]
            st.rerun()
    st.stop()

# ================= CSS =================
st.markdown("""
<style>

/* FORCE WIDTH */
.block-container {
    max-width: 140px !important;
    margin: auto !important;
}

/* GRID */
.grid {
    display: grid;
    grid-template-columns: repeat(4, 25px);
    gap: 2px;
}

/* CELLS */
.cell {
    width: 25px;
    height: 22px;
    font-size: 7px;
    display:flex;
    align-items:center;
    justify-content:center;
    border-radius:4px;
}

/* HEADER */
.header {
    font-weight:bold;
    background:#111;
    color:white;
}

/* STATES */
.free { background:#bbf7d0; }
.mine { background:#93c5fd; }
.taken { background:#e5e7eb; }

/* TIME COLORS */
.timeA { background:#f3f4f6; }
.timeB { background:#e0f2fe; }
.timeC { background:#fef3c7; }
.timeD { background:#ede9fe; }

</style>
""", unsafe_allow_html=True)

# ================= TABLE =================

st.markdown('<div class="grid">', unsafe_allow_html=True)

# HEADER (NO GAP)
st.markdown('<div class="cell header">T</div>', unsafe_allow_html=True)
st.markdown('<div class="cell header">1</div>', unsafe_allow_html=True)
st.markdown('<div class="cell header">2</div>', unsafe_allow_html=True)
st.markdown('<div class="cell header">3</div>', unsafe_allow_html=True)

# HOURS (START 06:00)
HOURS = [f"{h:02d}:{m}" for h in range(6,24) for m in ["00","30"]]

for idx, t in enumerate(HOURS):

    block = ["timeA","timeB","timeC","timeD"][(idx // 8) % 4]

    # TIME CELL
    st.markdown(f'<div class="cell {block}">{t}</div>', unsafe_allow_html=True)

    # TABLES
    for i in range(3):
        t_n = f"Table {i+1}"

        match = bookings[
            (bookings["Table"]==t_n)&
            (bookings["Time"]==t)&
            (bookings["Date"]==st.session_state.sel_date)
        ]

        if not match.empty:
            b_user = match.iloc[0]["User"]
            b_name = match.iloc[0]["Name"][:3]

            if b_user == st.session_state.user:
                st.markdown(f'<div class="cell mine">{b_name}</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="cell taken">{b_name}</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="cell free">+</div>', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

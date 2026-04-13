import streamlit as st
import pandas as pd
import os
from datetime import datetime, timedelta

st.set_page_config(layout="wide")

# ===== CSS GRID (REAL CONTROL) =====
st.markdown("""
<style>

.block-container { padding: 6px !important; }

/* MAIN GRID */
.table-grid {
    display: grid;
    grid-template-columns: 70px repeat(3, 1fr);
    gap: 4px;
    align-items: center;
}

/* CELL */
.cell {
    height: 42px;
    display:flex;
    align-items:center;
    justify-content:center;
    border-radius:10px;
    font-size:10px;
}

/* TIME */
.time {
    background:#e5e7eb;
}

/* FREE */
.free {
    background:#bbf7d0;
}

/* TAKEN */
.taken {
    background:#fecaca;
}

/* BUTTON RESET */
.cell button {
    width:100%;
    height:100%;
    font-size:10px !important;
    border:none;
    background:transparent;
}

</style>
""", unsafe_allow_html=True)

# ===== DATA =====
FILE = "bookings.csv"

def load():
    if os.path.exists(FILE):
        return pd.read_csv(FILE, dtype=str)
    return pd.DataFrame(columns=["Name","Date","Table","Time"])

def save(df):
    df.to_csv(FILE, index=False)

bookings = load()

if "date" not in st.session_state:
    st.session_state.date = str(datetime.now().date())

# ===== TIMES =====
HOURS = [f"{h:02d}:{m}" for h in range(6,22) for m in ["00","30"]]

st.write("### Schedule")

# ===== HEADER =====
st.markdown('<div class="table-grid">', unsafe_allow_html=True)

st.markdown('<div class="cell time">Time</div>', unsafe_allow_html=True)
st.markdown('<div class="cell">T1</div>', unsafe_allow_html=True)
st.markdown('<div class="cell">T2</div>', unsafe_allow_html=True)
st.markdown('<div class="cell">T3</div>', unsafe_allow_html=True)

# ===== ROWS =====
for t in HOURS:

    st.markdown(f'<div class="cell time">{t}</div>', unsafe_allow_html=True)

    for i in range(1,4):
        table = f"T{i}"

        match = bookings[
            (bookings["Date"]==st.session_state.date) &
            (bookings["Table"]==table) &
            (bookings["Time"]==t)
        ]

        key = f"{t}_{table}"

        if not match.empty:
            name = match.iloc[0]["Name"][:10]

            clicked = st.button(f"✖ {name}", key=key)

            st.markdown('<div class="cell taken"></div>', unsafe_allow_html=True)

            if clicked:
                bookings = bookings[~(
                    (bookings["Date"]==st.session_state.date) &
                    (bookings["Table"]==table) &
                    (bookings["Time"]==t)
                )]
                save(bookings)
                st.rerun()

        else:
            clicked = st.button("+", key=key)

            st.markdown('<div class="cell free"></div>', unsafe_allow_html=True)

            if clicked:
                bookings = pd.concat([bookings, pd.DataFrame([{
                    "Name": "Tom",
                    "Date": st.session_state.date,
                    "Table": table,
                    "Time": t
                }])])
                save(bookings)
                st.rerun()

st.markdown('</div>', unsafe_allow_html=True)

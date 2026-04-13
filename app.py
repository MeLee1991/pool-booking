import streamlit as st
import pandas as pd
import os
from datetime import datetime, timedelta

st.set_page_config(layout="wide")

FILE = "bookings.csv"

# ===== DATA =====
def load():
    if os.path.exists(FILE):
        return pd.read_csv(FILE, dtype=str)
    return pd.DataFrame(columns=["Name","Date","Table","Time"])

def save(df):
    df.to_csv(FILE, index=False)

bookings = load()

if "date" not in st.session_state:
    st.session_state.date = str(datetime.now().date())

if "click" not in st.session_state:
    st.session_state.click = None

# ===== HANDLE CLICK =====
params = st.query_params
if "slot" in params:
    st.session_state.click = params["slot"]
    st.query_params.clear()

if st.session_state.click:
    t, table = st.session_state.click.split("|")

    match = bookings[
        (bookings["Date"]==st.session_state.date) &
        (bookings["Table"]==table) &
        (bookings["Time"]==t)
    ]

    if not match.empty:
        bookings = bookings[~(
            (bookings["Date"]==st.session_state.date) &
            (bookings["Table"]==table) &
            (bookings["Time"]==t)
        )]
    else:
        bookings = pd.concat([bookings, pd.DataFrame([{
            "Name": "Tom",
            "Date": st.session_state.date,
            "Table": table,
            "Time": t
        }])])

    save(bookings)
    st.session_state.click = None
    st.rerun()

# ===== TIMES =====
HOURS = [f"{h:02d}:{m}" for h in range(6,22) for m in ["00","30"]]

# ===== HTML GRID =====
html = """
<style>
.grid {
    display: grid;
    grid-template-columns: 70px repeat(3, 1fr);
    gap: 6px;
}
.cell {
    height: 42px;
    display:flex;
    align-items:center;
    justify-content:center;
    border-radius:10px;
    font-size:10px;
    cursor:pointer;
}
.time { background:#e5e7eb; }
.free { background:#bbf7d0; }
.taken { background:#fecaca; }
</style>

<div class="grid">
"""

# HEADER
html += '<div class="cell time">Time</div>'
html += '<div class="cell">T1</div>'
html += '<div class="cell">T2</div>'
html += '<div class="cell">T3</div>'

# ROWS
for t in HOURS:

    html += f'<div class="cell time">{t}</div>'

    for i in range(1,4):
        table = f"T{i}"

        match = bookings[
            (bookings["Date"]==st.session_state.date) &
            (bookings["Table"]==table) &
            (bookings["Time"]==t)
        ]

        if not match.empty:
            name = match.iloc[0]["Name"][:10]
            html += f"""
            <div class="cell taken"
                onclick="window.location.search='?slot={t}|{table}'">
                ✖ {name}
            </div>
            """
        else:
            html += f"""
            <div class="cell free"
                onclick="window.location.search='?slot={t}|{table}'">
                +
            </div>
            """

html += "</div>"

st.markdown(html, unsafe_allow_html=True)

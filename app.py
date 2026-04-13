import streamlit as st
import pandas as pd
import os
from datetime import datetime, timedelta

st.set_page_config(layout="wide")

# ===== CSS: HARD GRID CONTROL =====
st.markdown("""
<style>

/* remove padding */
.block-container {
    padding: 6px !important;
}

/* FORCE GRID (no stacking EVER) */
.grid4 {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 6px;
}

/* buttons SAME SIZE */
button[kind="secondary"] {
    width: 100% !important;
    height: 40px !important;
    font-size: 10px !important;
    border-radius: 10px !important;
    padding: 0 !important;
}

/* colors */
.free button {
    background: #bbf7d0 !important;
}
.taken button {
    background: #fecaca !important;
}

/* time */
.timebox {
    background: #e5e7eb;
    text-align: center;
    border-radius: 10px;
    height: 40px;
    line-height: 40px;
    font-size: 10px;
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

# ===== SESSION =====
if "date" not in st.session_state:
    st.session_state.date = str(datetime.now().date())

# ===== DATES (LINEAR FIX) =====
st.write("### Select date")

dates = [datetime.now().date() + timedelta(days=i) for i in range(7)]

# TRUE linear grid
for i in range(0, len(dates), 4):
    cols = st.columns(4)

    for j in range(4):
        if i + j < len(dates):
            d = dates[i+j]
            ds = str(d)

            if cols[j].button(f"{d.strftime('%a')} {d.day}", key=f"d{ds}"):
                st.session_state.date = ds
                st.rerun()
        else:
            cols[j].empty()

# ===== TABLE =====
HOURS = [f"{h:02d}:{m}" for h in range(6,22) for m in ["00","30"]]

st.write("### Schedule")

# HEADER
cols = st.columns(4)
cols[0].markdown("**Time**")
cols[1].markdown("**T1**")
cols[2].markdown("**T2**")
cols[3].markdown("**T3**")

# ROWS
for t in HOURS:

    cols = st.columns(4)

    cols[0].markdown(f"<div class='timebox'>{t}</div>", unsafe_allow_html=True)

    for i in range(1,4):
        table = f"T{i}"

        match = bookings[
            (bookings["Date"]==st.session_state.date) &
            (bookings["Table"]==table) &
            (bookings["Time"]==t)
        ]

        if not match.empty:
            name = match.iloc[0]["Name"][:10]

            with cols[i]:
                st.markdown('<div class="taken">', unsafe_allow_html=True)
                if st.button(f"✖ {name}", key=f"{t}_{table}"):
                    bookings = bookings[~(
                        (bookings["Date"]==st.session_state.date) &
                        (bookings["Table"]==table) &
                        (bookings["Time"]==t)
                    )]
                    save(bookings)
                    st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)

        else:
            with cols[i]:
                st.markdown('<div class="free">', unsafe_allow_html=True)
                if st.button("+", key=f"{t}_{table}"):
                    bookings = pd.concat([bookings, pd.DataFrame([{
                        "Name": "Tom",
                        "Date": st.session_state.date,
                        "Table": table,
                        "Time": t
                    }])])
                    save(bookings)
                    st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)

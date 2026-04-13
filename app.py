import streamlit as st
import pandas as pd
import os
from datetime import datetime

st.set_page_config(layout="wide")

# ===== CSS FIX =====
st.markdown("""
<style>

/* remove padding */
.block-container {
    padding: 4px !important;
}

/* remove gaps between columns */
div[data-testid="column"] {
    padding: 2px !important;
}

/* buttons SAME SIZE */
button {
    width: 100% !important;
    height: 38px !important;
    font-size: 10px !important;
    border-radius: 10px !important;
    padding: 0 !important;
}

/* colors */
.free button {
    background-color: #bbf7d0 !important;
}
.taken button {
    background-color: #fecaca !important;
}

/* time */
.timebox {
    background: #e5e7eb;
    border-radius: 10px;
    text-align: center;
    height: 38px;
    line-height: 38px;
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

if "date" not in st.session_state:
    st.session_state.date = str(datetime.now().date())

# ===== TIMES =====
HOURS = [f"{h:02d}:{m}" for h in range(6,22) for m in ["00","30"]]

st.write("### Schedule")

# HEADER
cols = st.columns([1,1,1,1], gap="small")

cols[0].markdown("**Time**")
cols[1].markdown("**T1**")
cols[2].markdown("**T2**")
cols[3].markdown("**T3**")

# ROWS
for t in HOURS:

    cols = st.columns([1,1,1,1], gap="small")

    cols[0].markdown(f"<div class='timebox'>{t}</div>", unsafe_allow_html=True)

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

            with cols[i]:
                st.markdown('<div class="taken">', unsafe_allow_html=True)
                if st.button(f"✖ {name}", key=key):
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
                if st.button("+", key=key):
                    bookings = pd.concat([bookings, pd.DataFrame([{
                        "Name": "Tom",
                        "Date": st.session_state.date,
                        "Table": table,
                        "Time": t
                    }])])
                    save(bookings)
                    st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)

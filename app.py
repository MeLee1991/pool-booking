import streamlit as st
import pandas as pd
import os
from datetime import datetime

st.set_page_config(layout="wide")

# ===== STYLE =====
st.markdown("""
<style>
.block-container { padding: 6px !important; }

/* horizontal scroll */
.scroll {
    overflow-x: auto;
}

/* table width */
.table-wrap {
    min-width: 420px;
}

/* buttons */
button {
    width: 100% !important;
    height: 42px !important;
    font-size: 10px !important;
    border-radius: 10px !important;
}

/* colors */
.free button { background-color: #bbf7d0 !important; }
.taken button { background-color: #fecaca !important; }

/* time */
.timebox {
    background: #e5e7eb;
    text-align: center;
    border-radius: 10px;
    height: 42px;
    line-height: 42px;
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

# ===== SCROLL START =====
st.markdown('<div class="scroll"><div class="table-wrap">', unsafe_allow_html=True)

# HEADER
cols = st.columns([1,1,1,1])
cols[0].markdown("**Time**")
cols[1].markdown("**T1**")
cols[2].markdown("**T2**")
cols[3].markdown("**T3**")

# ROWS
for t in HOURS:

    cols = st.columns([1,1,1,1])

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

# ===== SCROLL END =====
st.markdown('</div></div>', unsafe_allow_html=True)

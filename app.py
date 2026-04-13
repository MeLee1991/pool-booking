import streamlit as st
import pandas as pd
import os
from datetime import datetime, timedelta

st.set_page_config(layout="centered")

# ===== STYLE FIX (IMPORTANT) =====
st.markdown("""
<style>
/* prevent column stacking */
div[data-testid="column"] {
    min-width: 70px !important;
    flex: 1 1 0% !important;
}

/* tighter gaps */
.block-container {
    padding-left: 8px;
    padding-right: 8px;
}

/* buttons full width */
.stButton button {
    width: 100%;
    height: 38px;
    font-size: 10px;
    border-radius: 10px;
}

/* colors */
.free button { background-color: #bbf7d0 !important; }
.taken button { background-color: #fecaca !important; }
.timebox {
    background: #e5e7eb;
    border-radius: 10px;
    text-align: center;
    padding: 8px 0;
    font-size: 10px;
}
</style>
""", unsafe_allow_html=True)

# ===== FILE =====
FILE = "bookings.csv"

def load():
    if os.path.exists(FILE):
        return pd.read_csv(FILE, dtype=str)
    return pd.DataFrame(columns=["Name","Date","Table","Time"])

def save(df):
    df.to_csv(FILE, index=False)

bookings = load()

# ===== SESSION =====
if "name" not in st.session_state:
    st.session_state.name = "Tom"

if "date" not in st.session_state:
    st.session_state.date = str(datetime.now().date())

# ===== HEADER =====
st.markdown(f"### 👤 {st.session_state.name} | {st.session_state.date}")

# ===== DATES GRID =====
today = datetime.now().date()
date_cols = st.columns(4)

for i in range(7):
    d = today + timedelta(days=i)
    ds = str(d)

    col = date_cols[i % 4]

    label = f"{d.strftime('%a')} {d.day}"

    if col.button(label, key=f"d{i}"):
        st.session_state.date = ds
        st.rerun()

# ===== TABLE =====
HOURS = [f"{h:02d}:{m}" for h in range(6,22) for m in ["00","30"]]

# header row
cols = st.columns([1,1,1,1])
cols[0].markdown("**Time**")
cols[1].markdown("**T1**")
cols[2].markdown("**T2**")
cols[3].markdown("**T3**")

# rows
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
                        "Name": st.session_state.name,
                        "Date": st.session_state.date,
                        "Table": table,
                        "Time": t
                    }])])
                    save(bookings)
                    st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)

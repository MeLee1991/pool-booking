import streamlit as st
import pandas as pd
import os
from datetime import datetime, timedelta

st.set_page_config(layout="wide")

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

# ===== SIDEBAR =====
with st.sidebar:
    st.title("⚙️ Menu")

    st.markdown(f"👤 {st.session_state.name}")

    if st.button("Logout"):
        st.session_state.name = ""
        st.rerun()

    st.divider()

    st.subheader("Stats")
    st.write(f"Bookings: {len(bookings)}")

    st.divider()

    st.subheader("Admin")

    df_edit = st.data_editor(bookings, use_container_width=True)

    if st.button("Save changes"):
        save(df_edit)
        st.success("Saved")

# ===== HEADER =====
st.markdown(f"### 👤 {st.session_state.name} | {st.session_state.date}")

# ===== DATES =====
today = datetime.now().date()

cols = st.columns(4)

for i in range(7):
    d = today + timedelta(days=i)
    ds = str(d)

    col = cols[i % 4]

    if col.button(f"{d.strftime('%a')} {d.day}", key=f"d{i}"):
        st.session_state.date = ds
        st.rerun()

# ===== TABLE =====
HOURS = [f"{h:02d}:{m}" for h in range(6,22) for m in ["00","30"]]

st.markdown("###")

header = st.columns([1,1,1,1])
header[0].markdown("**Time**")
header[1].markdown("**T1**")
header[2].markdown("**T2**")
header[3].markdown("**T3**")

for idx, t in enumerate(HOURS):

    # alternating background (every 4 hours)
    block = (idx // 8) % 2
    bg = "#f3f4f6" if block == 0 else "#e5e7eb"

    row = st.columns([1,1,1,1], gap="small")

    row[0].markdown(f"<div style='text-align:center'>{t}</div>", unsafe_allow_html=True)

    for i in range(1,4):
        table = f"T{i}"

        match = bookings[
            (bookings["Date"]==st.session_state.date) &
            (bookings["Table"]==table) &
            (bookings["Time"]==t)
        ]

        if not match.empty:
            name = match.iloc[0]["Name"][:10]

            if row[i].button(f"✖ {name}", key=f"{t}_{table}"):
                bookings = bookings[~(
                    (bookings["Date"]==st.session_state.date) &
                    (bookings["Table"]==table) &
                    (bookings["Time"]==t)
                )]
                save(bookings)
                st.rerun()

        else:
            if row[i].button("+", key=f"{t}_{table}"):
                bookings = pd.concat([bookings, pd.DataFrame([{
                    "Name": st.session_state.name,
                    "Date": st.session_state.date,
                    "Table": table,
                    "Time": t
                }])])
                save(bookings)
                st.rerun()

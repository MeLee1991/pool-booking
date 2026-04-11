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

# ================= CLICK HANDLER =================
params = st.query_params

if "book" in params:
    t, table = params["book"].split("|")

    match = bookings[
        (bookings["Table"]==table)&
        (bookings["Time"]==t)&
        (bookings["Date"]==st.session_state.sel_date)
    ]

    if match.empty:
        new = pd.DataFrame([{
            "User": st.session_state.user,
            "Name": st.session_state.name,
            "Date": st.session_state.sel_date,
            "Table": table,
            "Time": t
        }])
        bookings = pd.concat([bookings,new])
        save_data(bookings, BOOKINGS_FILE)

    st.query_params.clear()
    st.rerun()

if "del" in params:
    t, table = params["del"].split("|")

    match = bookings[
        (bookings["Table"]==table)&
        (bookings["Time"]==t)&
        (bookings["Date"]==st.session_state.sel_date)
    ]

    bookings = bookings.drop(match.index)
    save_data(bookings, BOOKINGS_FILE)

    st.query_params.clear()
    st.rerun()

# ================= CSS =================
st.markdown("""
<style>

.block-container {
    max-width: 140px;
    margin:auto;
}

/* GRID */
.grid {
    display:grid;
    grid-template-columns: repeat(4, 30px);
    gap:2px;
}

/* CELL */
.cell {
    width:30px;
    height:24px;
    font-size:8px;
    display:flex;
    align-items:center;
    justify-content:center;
    border-radius:5px;
    text-decoration:none;
}

/* HEADER */
.header {
    background:#111;
    color:white;
    font-weight:bold;
}

/* STATES */
.free { background:#bbf7d0; }
.mine { background:#93c5fd; }
.taken { background:#e5e7eb; }

/* TIME COLORS */
.tA { background:#f3f4f6; }
.tB { background:#e0f2fe; }
.tC { background:#fef3c7; }
.tD { background:#ede9fe; }

</style>
""", unsafe_allow_html=True)

# ================= BUILD GRID =================
HOURS = [f"{h:02d}:{m}" for h in range(6,24) for m in ["00","30"]]

html = '<div class="grid">'

# HEADER
html += '<div class="cell header">T</div>'
html += '<div class="cell header">1</div>'
html += '<div class="cell header">2</div>'
html += '<div class="cell header">3</div>'

for idx, t in enumerate(HOURS):

    color = ["tA","tB","tC","tD"][(idx//8)%4]

    # TIME
    html += f'<div class="cell {color}">{t}</div>'

    for i in range(3):
        table = f"Table {i+1}"

        match = bookings[
            (bookings["Table"]==table)&
            (bookings["Time"]==t)&
            (bookings["Date"]==st.session_state.sel_date)
        ]

        if not match.empty:
            b_user = match.iloc[0]["User"]
            name = match.iloc[0]["Name"][:3]

            if b_user == st.session_state.user:
                html += f'<a href="?del={t}|{table}" class="cell mine">{name}</a>'
            else:
                html += f'<div class="cell taken">{name}</div>'
        else:
            html += f'<a href="?book={t}|{table}" class="cell free">+</a>'

html += '</div>'

st.markdown(html, unsafe_allow_html=True)

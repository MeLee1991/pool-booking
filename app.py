


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


# ================= SIDEBAR =================

with st.sidebar:

    st.write(f"👤 {st.session_state.name}")


    if st.session_state.role == "admin":

        st.markdown("### Admin")

        st.write(f"Bookings: {len(bookings)}")


        st.download_button(

            "Download CSV",

            bookings.to_csv(index=False),

            "bookings.csv"

        )


    if st.button("Logout"):

        st.session_state.clear()

        st.rerun()


# ================= ACTION HANDLER =================

action = st.session_state.get("action", None)


if action:

    typ, t, table = action.split("|")


    if typ == "book":

        new = pd.DataFrame([{

            "User": st.session_state.user,

            "Name": st.session_state.name,

            "Date": st.session_state.sel_date,

            "Table": table,

            "Time": t

        }])

        bookings = pd.concat([bookings,new])

        save_data(bookings, BOOKINGS_FILE)


    if typ == "del":

        bookings = bookings[

            ~((bookings["Table"]==table)&

              (bookings["Time"]==t)&

              (bookings["Date"]==st.session_state.sel_date))

        ]

        save_data(bookings, BOOKINGS_FILE)


    st.session_state.action = None

    st.rerun()


# ================= CSS =================

st.markdown("""

<style>


.block-container { max-width: 300px; margin:auto; }


/* DATE GRID */

.dates {

    display:grid;

    grid-template-columns: repeat(7, 1fr);

    gap:3px;

    margin-bottom:6px;

}


.date {

    font-size:9px;

    padding:5px;

    text-align:center;

    border-radius:6px;

    background:#eee;

}


.date.sel { background:#4f46e5; color:white; }

.date-today { background:#22c55e; color:white; }

.date-tomorrow { background:#3b82f6; color:white; }


/* GRID */

.grid {

    display:grid;

    grid-template-columns: repeat(4, 60px);

    gap:3px;

}


.cell {

    width:60px;

    height:28px;

    font-size:9px;

    display:flex;

    align-items:center;

    justify-content:center;

    border-radius:6px;

    cursor:pointer;

}


/* HEADER */

.header { background:#111; color:white; }


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


# ================= DATE PICKER =================

today = datetime.now().date()


html = '<div class="dates">'

for i in range(14):

    d = today + timedelta(days=i)

    d_str = str(d)


    cls = "date"

    label = f"{d.day}.{d.strftime('%a')}"


    if i == 0:

        cls += " date-today"

        label = "TOD"

    elif i == 1:

        cls += " date-tomorrow"

        label = "TOM"


    if d_str == st.session_state.sel_date:

        cls += " sel"


    html += f'<div class="{cls}" onclick="window.parent.postMessage({{type: \'streamlit:setSessionState\', key: \'sel_date\', value: \'{d_str}\'}}, \'*\')">{label}</div>'

html += '</div>'


# ================= GRID =================

HOURS = [f"{h:02d}:{m}" for h in range(6,24) for m in ["00","30"]]


html += '<div class="grid">'

html += '<div class="cell header">T</div>'

html += '<div class="cell header">1</div>'

html += '<div class="cell header">2</div>'

html += '<div class="cell header">3</div>'


for idx, t in enumerate(HOURS):


    color = ["tA","tB","tC","tD"][(idx//8)%4]

    html += f'<div class="cell {color}">{t}</div>'


    for i in range(3):

        table = f"Table {i+1}"


        match = bookings[

            (bookings["Table"]==table)&

            (bookings["Time"]==t)&

            (bookings["Date"]==st.session_state.sel_date)

        ]


        if not match.empty:

            user = match.iloc[0]["User"]

            name = match.iloc[0]["Name"][:3]


            if user == st.session_state.user:

                html += f'<div class="cell mine" onclick="window.parent.postMessage({{type: \'streamlit:setSessionState\', key: \'action\', value: \'del|{t}|{table}\'}} , \'*\')">{name}</div>'

            else:

                html += f'<div class="cell taken">{name}</div>'

        else:

            html += f'<div class="cell free" onclick="window.parent.postMessage({{type: \'streamlit:setSessionState\', key: \'action\', value: \'book|{t}|{table}\'}} , \'*\')">+</div>'


html += '</div>'


st.markdown(html, unsafe_allow_html=True)

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
if "page" not in st.session_state:
    st.session_state.page = "booking"

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

if "date" in params:
    st.session_state.sel_date = params["date"]
    st.query_params.clear()
    st.rerun()

if "nav" in params:
    st.session_state.page = params["nav"]
    st.query_params.clear()
    st.rerun()

if "book" in params:
    t, table = params["book"].split("|")

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
    max-width: 160px;
    margin:auto;
}

/* DATE GRID */
.dates {
    display:grid;
    grid-template-columns: repeat(7, 1fr);
    gap:4px;
    margin-bottom:6px;
}

.date {
    font-size:8px;
    padding:4px;
    text-align:center;
    border-radius:6px;
    background:#eee;
    text-decoration:none;
    color:black;
}

.date.sel {
    background:#4f46e5;
    color:white;
}

/* NAV */
.nav {
    text-align:center;
    margin-bottom:6px;
}

/* TABLE GRID */
.grid {
    display:grid;
    grid-template-columns: repeat(4, 30px);
    gap:2px;
}

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

# ================= NAV BAR =================
html = '<div class="nav">'
html += f'{st.session_state.name} | '
html += '<a href="?nav=booking">Booking</a> '
if st.session_state.role == "admin":
    html += '| <a href="?nav=admin">Admin</a>'
html += '</div>'

# ================= DATE PICKER =================
today = datetime.now().date()

html += '<div class="dates">'
for i in range(14):
    d = today + timedelta(days=i)
    d_str = str(d)
    cls = "date sel" if d_str == st.session_state.sel_date else "date"
    label = f"{d.day}.{d.strftime('%a')}"
    html += f'<a href="?date={d_str}" class="{cls}">{label}</a>'
html += '</div>'

# ================= PAGE =================
if st.session_state.page == "booking":

    HOURS = [f"{h:02d}:{m}" for h in range(6,24) for m in ["00","30"]]

    html += '<div class="grid">'

    # HEADER
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
                b_user = match.iloc[0]["User"]
                name = match.iloc[0]["Name"][:3]

                if b_user == st.session_state.user:
                    html += f'<a href="?del={t}|{table}" class="cell mine">{name}</a>'
                else:
                    html += f'<div class="cell taken">{name}</div>'
            else:
                html += f'<a href="?book={t}|{table}" class="cell free">+</a>'

    html += '</div>'

elif st.session_state.page == "admin":

    html += "<b>Admin Panel</b><br><br>"
    html += f"Bookings: {len(bookings)}<br><br>"
    html += "Download CSV below ⬇️"

    st.markdown(html, unsafe_allow_html=True)

    st.download_button(
        "Download bookings",
        bookings.to_csv(index=False),
        "bookings.csv"
    )

    st.stop()

st.markdown(html, unsafe_allow_html=True)

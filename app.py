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

if "users" not in st.session_state:
    st.session_state.users = load_data(USERS_FILE, ["Email","Name","Password","Role"])
if "bookings" not in st.session_state:
    st.session_state.bookings = load_data(BOOKINGS_FILE, ["User","Name","Date","Table","Time"])

for k in ["user","name","role","sel_date"]:
    if k not in st.session_state:
        st.session_state[k] = None

if not st.session_state.sel_date:
    st.session_state.sel_date = str(datetime.now().date())

# ================= LOGIN =================
if st.session_state.user is None:
    st.title("Pool")

    e = st.text_input("Email")
    p = st.text_input("Password", type="password")

    if st.button("Login"):
        m = st.session_state.users[
            (st.session_state.users["Email"]==e)&
            (st.session_state.users["Password"]==p)
        ]
        if not m.empty:
            st.session_state.user = e
            st.session_state.name = m.iloc[0]["Name"]
            st.session_state.role = m.iloc[0]["Role"]
            st.rerun()
    st.stop()

# ================= CSS =================
st.markdown("""
<style>
.block-container { max-width:340px; margin:auto; }

/* FORCE 4 COLUMN GRID */
.row {
    display:flex;
    gap:4px;
    margin-bottom:4px;
}

/* each cell */
.cell {
    width:70px;
    height:32px;
    font-size:10px;
    display:flex;
    align-items:center;
    justify-content:center;
    border-radius:6px;
}

/* headers */
.header {
    background:#111;
    color:white;
    font-weight:bold;
}

/* states */
.free button { background:#bbf7d0 !important; }
.mine button { background:#93c5fd !important; }
.taken button { background:#e5e7eb !important; }

/* time color blocks */
.timeA { background:#f3f4f6; }
.timeB { background:#e0f2fe; }
.timeC { background:#fef3c7; }
.timeD { background:#ede9fe; }

/* buttons EXACT size */
.stButton > button {
    width:70px !important;
    height:32px !important;
    font-size:10px !important;
    border-radius:6px !important;
    padding:0 !important;
}

/* dates */
.date button {
    width:42px !important;
    height:34px !important;
    font-size:9px !important;
}

.sel button { background:#4f46e5 !important; color:white; }
.tod button { background:#22c55e !important; color:white; }
.tom button { background:#3b82f6 !important; color:white; }

</style>
""", unsafe_allow_html=True)

# ================= DATES =================
today = datetime.now().date()

for week in [range(7), range(7,14)]:
    cols = st.columns(7)
    for i in week:
        d = today + timedelta(days=i)
        d_str = str(d)

        label = f"{d.day}.{d.strftime('%a')}"
        cls = "date"

        if i == 0:
            label = "TOD"
            cls += " tod"
        elif i == 1:
            label = "TOM"
            cls += " tom"

        if d_str == st.session_state.sel_date:
            cls += " sel"

        with cols[i % 7]:
            st.markdown(f'<div class="{cls}">', unsafe_allow_html=True)
            if st.button(label, key=f"d_{d_str}"):
                st.session_state.sel_date = d_str
                st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)

st.divider()

# ================= TABLE =================
HOURS = [f"{h:02d}:{m}" for h in range(6,24) for m in ["00","30"]]

# HEADER ROW
cols = st.columns(4)
cols[0].markdown('<div class="cell header">Time</div>', unsafe_allow_html=True)
cols[1].markdown('<div class="cell header">T1</div>', unsafe_allow_html=True)
cols[2].markdown('<div class="cell header">T2</div>', unsafe_allow_html=True)
cols[3].markdown('<div class="cell header">T3</div>', unsafe_allow_html=True)

# DATA ROWS
for idx, t in enumerate(HOURS):

    cols = st.columns(4)
    block = ["timeA","timeB","timeC","timeD"][(idx//8)%4]

    # TIME (aligned properly now)
    with cols[0]:
        st.markdown(f'<div class="cell {block}">{t}</div>', unsafe_allow_html=True)

    # TABLES
    for i in range(3):
        table = f"Table {i+1}"

        match = st.session_state.bookings[
            (st.session_state.bookings["Table"]==table)&
            (st.session_state.bookings["Time"]==t)&
            (st.session_state.bookings["Date"]==st.session_state.sel_date)
        ]

        with cols[i+1]:

            if not match.empty:
                user = match.iloc[0]["User"]
                name = match.iloc[0]["Name"][:4]

                if user == st.session_state.user:
                    st.markdown('<div class="mine">', unsafe_allow_html=True)
                    if st.button(f"✕ {name}", key=f"{t}_{i}"):
                        st.session_state.bookings = st.session_state.bookings.drop(match.index)
                        save_data(st.session_state.bookings, BOOKINGS_FILE)
                        st.rerun()
                    st.markdown("</div>", unsafe_allow_html=True)
                else:
                    st.markdown('<div class="taken">', unsafe_allow_html=True)
                    st.button(name, key=f"{t}_{i}", disabled=True)
                    st.markdown("</div>", unsafe_allow_html=True)

            else:
                st.markdown('<div class="free">', unsafe_allow_html=True)
                if st.button("+", key=f"{t}_{i}"):
                    new = pd.DataFrame([{
                        "User": st.session_state.user,
                        "Name": st.session_state.name,
                        "Date": st.session_state.sel_date,
                        "Table": table,
                        "Time": t
                    }])
                    st.session_state.bookings = pd.concat([st.session_state.bookings,new], ignore_index=True)
                    save_data(st.session_state.bookings, BOOKINGS_FILE)
                    st.rerun()
                st.markdown("</div>", unsafe_allow_html=True)

# ================= HEADER =================
st.write(f"👤 {st.session_state.name} | {st.session_state.sel_date}")

import os
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

st.set_page_config(page_title="Pool", layout="centered")

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

# SESSION
if "user" not in st.session_state: st.session_state.user = None
if "name" not in st.session_state: st.session_state.name = None
if "role" not in st.session_state: st.session_state.role = None
if "sel_date" not in st.session_state: st.session_state.sel_date = str(datetime.now().date())

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

# ================= DATE =================
d = datetime.fromisoformat(st.session_state.sel_date)

c1,c2,c3 = st.columns([1,2,1])
with c1:
    if st.button("◀"):
        st.session_state.sel_date = str(d - timedelta(days=1))
        st.rerun()
with c2:
    st.markdown(f"### {d.strftime('%d %b')}")
with c3:
    if st.button("▶"):
        st.session_state.sel_date = str(d + timedelta(days=1))
        st.rerun()

# ================= CSS GRID =================
st.markdown("""
<style>

.block-container {
    max-width: 240px !important;
    margin: auto !important;
    padding: 0 !important;
}

.grid {
    display: grid;
    grid-template-columns: 50px 50px 50px 50px;
    gap: 2px;
}

/* BUTTON CELLS */
.grid button {
    width: 50px !important;
    height: 34px !important;
    font-size: 9px !important;
    padding: 0 !important;
    border-radius: 4px !important;
}

/* HEADER */
.header {
    background: #222 !important;
    color: white !important;
}

/* FREE */
.free {
    background: #e8fbe8 !important;
    color: #1a7f37 !important;
}

/* TAKEN */
.taken {
    background: #eee !important;
}

/* MINE */
.mine {
    background: #e6f0ff !important;
    color: #1d4ed8 !important;
}

.time {
    font-size: 9px;
    font-weight: bold;
    text-align: center;
}

</style>
""", unsafe_allow_html=True)

# ================= GRID =================
st.markdown('<div class="grid">', unsafe_allow_html=True)

# HEADER
st.markdown("<div></div>", unsafe_allow_html=True)
for t in ["T1","T2","T3"]:
    st.markdown(f"<div class='header'>{t}</div>", unsafe_allow_html=True)

HOURS = [f"{h:02d}:{m}" for h in (list(range(8,24))+list(range(0,3))) for m in ["00","30"]]

for t in HOURS:
    st.markdown(f"<div class='time'>{t}</div>", unsafe_allow_html=True)

    for i in range(3):
        t_n = f"Table {i+1}"

        match = bookings[
            (bookings["Table"]==t_n)&
            (bookings["Time"]==t)&
            (bookings["Date"]==st.session_state.sel_date)
        ]

        key = f"{t}_{i}"

        if not match.empty:
            b_user = match.iloc[0]["User"]
            b_name = match.iloc[0]["Name"]

            if b_user == st.session_state.user:
                if st.button(f"❌", key=key):
                    bookings = bookings.drop(match.index)
                    save_data(bookings, BOOKINGS_FILE)
                    st.rerun()
                st.markdown(f"<style>button[key='{key}']{{background:#e6f0ff}}</style>", unsafe_allow_html=True)

            else:
                st.button(b_name[:3], key=key, disabled=True)

        else:
            if st.button("+", key=key):
                new_b = pd.DataFrame([{
                    "User": st.session_state.user,
                    "Name": st.session_state.name,
                    "Date": st.session_state.sel_date,
                    "Table": t_n,
                    "Time": t
                }])
                save_data(pd.concat([bookings,new_b]), BOOKINGS_FILE)
                st.rerun()

st.markdown("</div>", unsafe_allow_html=True)

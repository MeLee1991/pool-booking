import os
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

st.set_page_config(page_title="Pool", layout="centered")

# ================= DATA =================
USERS_FILE = "users.csv"
BOOKINGS_FILE = "bookings.csv"

def load(file, cols):
    if os.path.exists(file) and os.path.getsize(file) > 0:
        return pd.read_csv(file, dtype=str)
    return pd.DataFrame(columns=cols)

def save(df, file):
    df.to_csv(file, index=False)

users = load(USERS_FILE, ["Email","Name","Password","Role"])
bookings = load(BOOKINGS_FILE, ["User","Name","Date","Table","Time"])

# AUTO USER
if "tom3@gmail.com" not in users["Email"].values:
    users = pd.concat([users, pd.DataFrame([{
        "Email":"tom3@gmail.com",
        "Name":"Tom",
        "Password":"1234",
        "Role":"admin"
    }])])
    save(users, USERS_FILE)

# SESSION
if "user" not in st.session_state: st.session_state.user=None
if "name" not in st.session_state: st.session_state.name=None
if "role" not in st.session_state: st.session_state.role=None
if "date" not in st.session_state: st.session_state.date=str(datetime.now().date())

# LOGIN
if st.session_state.user is None:
    st.title("Pool")
    e = st.text_input("Email", value="tom3@gmail.com")
    p = st.text_input("Password", type="password", value="1234")

    if st.button("Login"):
        m = users[(users["Email"]==e)&(users["Password"]==p)]
        if not m.empty:
            st.session_state.user=e
            st.session_state.name=m.iloc[0]["Name"]
            st.session_state.role=m.iloc[0]["Role"]
            st.rerun()
    st.stop()

# ================= STYLE =================
st.markdown("""
<style>
.block-container { max-width:340px; margin:auto; }

.grid {
    display:grid;
    grid-template-columns: 60px 1fr 1fr 1fr;
    gap:6px;
}

.cell {
    height:36px;
    display:flex;
    align-items:center;
    justify-content:center;
    border-radius:8px;
    font-size:11px;
    cursor:pointer;
}

.header { background:#111; color:white; font-weight:bold; }
.free { background:#bbf7d0; }
.mine { background:#93c5fd; }
.taken { background:#e5e7eb; }

.time { background:#f3f4f6; }

.date-row {
    display:grid;
    grid-template-columns:repeat(7,1fr);
    gap:6px;
    margin-bottom:8px;
}

.date {
    padding:8px 0;
    background:#e5e7eb;
    text-align:center;
    border-radius:8px;
    font-size:10px;
    cursor:pointer;
}

.sel { background:#4f46e5 !important; color:white; }
</style>
""", unsafe_allow_html=True)

# ================= DATE PICKER =================
today = datetime.now().date()

for w in [0,7]:
    st.markdown('<div class="date-row">', unsafe_allow_html=True)
    for i in range(w, w+7):
        d = today + timedelta(days=i)
        d_str = str(d)

        cls = "date"
        if d_str == st.session_state.date:
            cls += " sel"

        if st.button(f"{d.day}.{d.strftime('%a')}", key=f"d_{d_str}"):
            st.session_state.date = d_str
            st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown("---")

# ================= TABLE =================
HOURS = [f"{h:02d}:{m}" for h in range(6,24) for m in ["00","30"]]

# HEADER
st.markdown('<div class="grid">', unsafe_allow_html=True)
for h in ["Time","T1","T2","T3"]:
    st.markdown(f'<div class="cell header">{h}</div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# ROWS
for t in HOURS:
    st.markdown('<div class="grid">', unsafe_allow_html=True)

    # TIME
    st.markdown(f'<div class="cell time">{t}</div>', unsafe_allow_html=True)

    for i in range(3):
        table = f"Table {i+1}"

        match = bookings[
            (bookings["Table"]==table)&
            (bookings["Time"]==t)&
            (bookings["Date"]==st.session_state.date)
        ]

        key = f"{t}_{i}"

        if not match.empty:
            user = match.iloc[0]["User"]
            name = match.iloc[0]["Name"][:3]

            if user == st.session_state.user:
                if st.button(f"❌{name}", key=key):
                    bookings = bookings.drop(match.index)
                    save(bookings, BOOKINGS_FILE)
                    st.rerun()
            else:
                st.button(name, key=key, disabled=True)

        else:
            if st.button("+", key=key):
                bookings = pd.concat([bookings, pd.DataFrame([{
                    "User": st.session_state.user,
                    "Name": st.session_state.name,
                    "Date": st.session_state.date,
                    "Table": table,
                    "Time": t
                }])])
                save(bookings, BOOKINGS_FILE)
                st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)

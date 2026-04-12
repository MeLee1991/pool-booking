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

# ================= SESSION =================
if "user" not in st.session_state: st.session_state.user=None
if "name" not in st.session_state: st.session_state.name=None
if "role" not in st.session_state: st.session_state.role=None
if "date" not in st.session_state: st.session_state.date=str(datetime.now().date())

# ================= LOGIN =================
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

# ================= CSS (THIS IS THE FIX) =================
st.markdown("""
<style>

/* container */
.block-container {
    max-width: 240px !important;
    margin:auto;
    padding:0.3rem !important;
}

/* keep rows horizontal */
div[data-testid="stHorizontalBlock"] {
    display:flex !important;
    flex-wrap:nowrap !important;
    gap:3px !important;
}

/* 🔥 narrower columns */
div[data-testid="column"] {
    flex: 0 0 45px !important;
    width: 45px !important;
    min-width: 45px !important;
}

/* buttons fill column */
.stButton > button {
    width: 100% !important;
    height: 34px !important;
    font-size: 9px !important;
    border-radius: 8px !important;
    padding:0 !important;
}

/* states */
.free button { background:#bbf7d0 !important; }
.mine button { background:#93c5fd !important; }
.taken button { background:#e5e7eb !important; }

/* dates */
.date button {
    width:100% !important;
    height:30px !important;
    font-size:8px !important;
}

.sel button {
    background:#4f46e5 !important;
    color:white !important;
}

</style>
""", unsafe_allow_html=True)

# ================= HEADER =================
st.write(f"👤 {st.session_state.name} | {st.session_state.date}")

# ================= DATES =================
today = datetime.now().date()

for week in [range(7), range(7,14)]:
    cols = st.columns(7)
    for i in week:
        d = today + timedelta(days=i)
        d_str = str(d)

        label = f"{d.day}.{d.strftime('%a')}"
        cls = "sel" if d_str == st.session_state.date else ""

        with cols[i % 7]:
            st.markdown(f'<div class="{cls} date">', unsafe_allow_html=True)
            if st.button(label, key=f"d_{d_str}"):
                st.session_state.date = d_str
                st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)

st.divider()

# ================= TABLE =================
HOURS = [f"{h:02d}:{m}" for h in range(6,24) for m in ["00","30"]]

# header
h = st.columns(4)
h[0].write("T")
h[1].write("1")
h[2].write("2")
h[3].write("3")

for t in HOURS:
    cols = st.columns(4)

    cols[0].write(t)

    for i in range(3):
        table = f"Table {i+1}"

        match = bookings[
            (bookings["Table"]==table)&
            (bookings["Time"]==t)&
            (bookings["Date"]==st.session_state.date)
        ]

        with cols[i+1]:
            if not match.empty:
                user = match.iloc[0]["User"]
                name = match.iloc[0]["Name"][:3]

                if user == st.session_state.user:
                    st.markdown('<div class="mine">', unsafe_allow_html=True)
                    if st.button(f"❌{name}", key=f"{t}_{i}"):
                        bookings = bookings.drop(match.index)
                        save(bookings, BOOKINGS_FILE)
                        st.rerun()
                    st.markdown("</div>", unsafe_allow_html=True)
                else:
                    st.markdown('<div class="taken">', unsafe_allow_html=True)
                    st.button(name, key=f"{t}_{i}", disabled=True)
                    st.markdown("</div>", unsafe_allow_html=True)
            else:
                st.markdown('<div class="free">', unsafe_allow_html=True)
                if st.button("+", key=f"{t}_{i}"):
                    bookings = pd.concat([bookings, pd.DataFrame([{
                        "User": st.session_state.user,
                        "Name": st.session_state.name,
                        "Date": st.session_state.date,
                        "Table": table,
                        "Time": t
                    }])])
                    save(bookings, BOOKINGS_FILE)
                    st.rerun()
                st.markdown("</div>", unsafe_allow_html=True)

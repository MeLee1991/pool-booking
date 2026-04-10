import os
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

# =========================
# SETUP
# =========================
st.set_page_config(page_title="Pool", layout="wide")

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

# =========================
# SESSION
# =========================
if "user" not in st.session_state: st.session_state.user = None
if "name" not in st.session_state: st.session_state.name = None
if "role" not in st.session_state: st.session_state.role = None
if "sel_date" not in st.session_state: st.session_state.sel_date = str(datetime.now().date())

# =========================
# CSS (REAL GRID SYSTEM)
# =========================
st.markdown("""
<style>

/* ===== ROOT ===== */
html, body {
    overflow-x: hidden !important;
    margin: 0 !important;
}

/* FULL WIDTH APP */
.block-container {
    padding: 4px !important;
    max-width: 100vw !important;
}

/* ===== GRID (4 columns) ===== */
.row {
    display: flex;
    width: 100vw;
}

/* EACH COLUMN = EXACTLY 25% */
.col {
    width: 25vw;
    max-width: 25vw;
    min-width: 25vw;
    display: flex;
    justify-content: center;
    align-items: center;
}

/* ===== BUTTONS (FIT COLUMN) ===== */
.stButton > button {
    width: 90% !important;
    height: 38px !important;
    font-size: 11px !important;
    border-radius: 8px !important;
    padding: 0 !important;
}

/* COLORS */
button[kind="secondary"] {
    background: #e6f7e6 !important;
    color: #1a7f37 !important;
}

button[kind="primary"] {
    background: #ffeaea !important;
    color: #cf222e !important;
}

button:disabled {
    background: #f2f2f2 !important;
    color: #999 !important;
}

/* HEADER */
.header {
    width: 90%;
    height: 36px;
    border-radius: 8px;
    background: #2f3542;
    color: white;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 11px;
}

/* TIME */
.time {
    font-size: 10px;
    font-weight: bold;
}

/* ===== FIXED DATE BAR ===== */
.date-bar {
    position: sticky;
    top: 0;
    background: white;
    z-index: 100;
    padding: 4px 0;
    border-bottom: 1px solid #ddd;
}

/* ===== SCROLL ===== */
.scroll {
    height: 75vh;
    overflow-y: auto;
}

</style>
""", unsafe_allow_html=True)

# =========================
# LOGIN
# =========================
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

# =========================
# DATE BAR (ALWAYS VISIBLE)
# =========================
d = datetime.fromisoformat(st.session_state.sel_date)

st.markdown('<div class="date-bar">', unsafe_allow_html=True)

c1, c2, c3 = st.columns([1,2,1])

with c1:
    if st.button("◀"):
        st.session_state.sel_date = str(d - timedelta(days=1))
        st.rerun()

with c2:
    st.markdown(f"**{d.strftime('%A %d %b')}**")

with c3:
    if st.button("▶"):
        st.session_state.sel_date = str(d + timedelta(days=1))
        st.rerun()

st.markdown('</div>', unsafe_allow_html=True)

# =========================
# HEADER (NO GAP)
# =========================
st.markdown("""
<div class="row">
    <div class="col"></div>
    <div class="col"><div class="header">T1</div></div>
    <div class="col"><div class="header">T2</div></div>
    <div class="col"><div class="header">T3</div></div>
</div>
""", unsafe_allow_html=True)

# =========================
# TABLE
# =========================
st.markdown('<div class="scroll">', unsafe_allow_html=True)

HOURS = [f"{h:02d}:{m}" for h in (list(range(8,24))+list(range(0,3))) for m in ["00","30"]]

for t in HOURS:

    cols = st.columns(4)

    with cols[0]:
        st.markdown(f"<div class='time'>{t}</div>", unsafe_allow_html=True)

    user_has = not bookings[
        (bookings["User"]==st.session_state.user)&
        (bookings["Time"]==t)&
        (bookings["Date"]==st.session_state.sel_date)
    ].empty

    for i in range(3):
        t_n = f"Table {i+1}"

        match = bookings[
            (bookings["Table"]==t_n)&
            (bookings["Time"]==t)&
            (bookings["Date"]==st.session_state.sel_date)
        ]

        with cols[i+1]:

            if not match.empty:
                b_user = match.iloc[0]["User"]
                b_name = match.iloc[0]["Name"]

                if b_user == st.session_state.user:
                    if st.button(f"❌ {b_name[:4]}", key=f"{t}_{i}"):
                        bookings = bookings.drop(match.index)
                        save_data(bookings, BOOKINGS_FILE)
                        st.rerun()
                else:
                    st.button(b_name[:4], key=f"{t}_{i}", disabled=True)

            else:
                if st.button("Free", key=f"{t}_{i}", type="secondary"):
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

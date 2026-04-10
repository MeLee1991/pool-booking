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
# CSS (STREAMLIT-COMPATIBLE FIX)
# =========================
st.markdown("""
<style>

/* remove horizontal scroll */
html, body, .stApp {
    overflow-x: hidden !important;
}

/* remove padding */
.block-container {
    padding: 4px !important;
}

/* FORCE 4-COLUMN GRID */
[data-testid="stHorizontalBlock"] {
    display: flex !important;
    flex-wrap: nowrap !important;
    gap: 2px !important;
}

/* equal width columns (25% each) */
[data-testid="column"] {
    flex: 1 1 0 !important;
    min-width: 0 !important;
}

/* === BUTTONS === */
.stButton > button {
    width: 100% !important;
    height: 36px !important;
    padding: 0 !important;
    font-size: 10px !important;
    border-radius: 6px !important;
}

/* colors */
button[kind="secondary"] {
    background: #e8fbe8 !important;
    color: #1a7f37 !important;
}

button[kind="primary"] {
    background: #ffeaea !important;
    color: #cf222e !important;
}

/* disabled */
button:disabled {
    background: #f1f1f1 !important;
    color: #999 !important;
}

/* header */
.header {
    text-align: center;
    background: #2f3542;
    color: white;
    padding: 6px 0;
    border-radius: 6px;
    font-size: 11px;
}

/* time column */
.time {
    text-align: center;
    font-size: 10px;
    font-weight: bold;
}

/* sticky date bar */
.date-bar {
    position: sticky;
    top: 0;
    background: white;
    z-index: 100;
    padding: 4px 0;
}

/* scroll */
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
# DATE NAV (VISIBLE)
# =========================
d = datetime.fromisoformat(st.session_state.sel_date)

st.markdown('<div class="date-bar">', unsafe_allow_html=True)

c1,c2,c3 = st.columns([1,2,1])

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
h = st.columns(4)

with h[0]: st.markdown("<div class='time'></div>", unsafe_allow_html=True)
with h[1]: st.markdown("<div class='header'>T1</div>", unsafe_allow_html=True)
with h[2]: st.markdown("<div class='header'>T2</div>", unsafe_allow_html=True)
with h[3]: st.markdown("<div class='header'>T3</div>", unsafe_allow_html=True)

# =========================
# TABLE
# =========================
st.markdown('<div class="scroll">', unsafe_allow_html=True)

HOURS = [f"{h:02d}:{m}" for h in (list(range(8,24))+list(range(0,3))) for m in ["00","30"]]

for t in HOURS:
    row = st.columns(4)

    with row[0]:
        st.markdown(f"<div class='time'>{t}</div>", unsafe_allow_html=True)

    for i in range(3):
        t_n = f"Table {i+1}"

        match = bookings[
            (bookings["Table"]==t_n)&
            (bookings["Time"]==t)&
            (bookings["Date"]==st.session_state.sel_date)
        ]

        with row[i+1]:

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

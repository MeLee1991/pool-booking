import os
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

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

# ================= SESSION =================
if "user" not in st.session_state: st.session_state.user = None
if "name" not in st.session_state: st.session_state.name = None
if "role" not in st.session_state: st.session_state.role = None
if "sel_date" not in st.session_state: st.session_state.sel_date = str(datetime.now().date())

# ================= LOGIN =================
if st.session_state.user is None:
    st.title("🎱 Pool")

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

# ================= CSS (REAL FIX) =================
st.markdown("""
<style>

/* ===== GLOBAL WIDTH (SAFE, DOESN'T BREAK TOP UI) ===== */
.block-container {
    max-width: 380px !important;
    margin: auto !important;
    padding-top: 10px !important;
}

/* ===== REMOVE RANDOM GAPS ===== */
div[data-testid="stVerticalBlock"] > div {
    gap: 2px !important;
}

/* ===== FORCE ROW BEHAVIOR ===== */
[data-testid="stHorizontalBlock"] {
    display: flex !important;
    flex-wrap: nowrap !important;
    gap: 2px !important;
}

/* ===== CRITICAL: FIX COLUMN WIDTH ===== */
[data-testid="column"] {
    flex: 0 0 auto !important;
    width: 75px !important;
    min-width: 75px !important;
    max-width: 75px !important;
    padding: 0 !important;
}

/* ===== BUTTONS (IDENTICAL SIZE ALWAYS) ===== */
.stButton > button {
    width: 75px !important;
    height: 36px !important;
    border-radius: 10px !important;
    font-size: 10px !important;
    padding: 0 !important;
}

/* ===== DATE BUTTONS (BIGGER BUT TIGHT) ===== */
.date-row [data-testid="column"] {
    width: 48px !important;
    min-width: 48px !important;
    max-width: 48px !important;
}

.date-row button {
    width: 48px !important;
    height: 36px !important;
    font-size: 11px !important;
}

/* ===== COLORS ===== */
.free button {
    background: linear-gradient(135deg,#d9fdd3,#b6f2b0) !important;
    color: #146c2e !important;
}

.mine button {
    background: linear-gradient(135deg,#cfe2ff,#a8c7ff) !important;
    color: #0b3d91 !important;
}

.taken button {
    background: #eeeeee !important;
    color: #666 !important;
}

/* ===== HEADER ===== */
.header {
    text-align:center;
    background:#2f3542;
    color:white;
    padding:6px 0;
    border-radius:10px;
    font-size:11px;
}

/* ===== TIME ===== */
.time {
    text-align:center;
    font-size:10px;
    font-weight:bold;
}

/* ===== SCROLL ===== */
.scroll {
    height:65vh;
    overflow-y:auto;
}

</style>
""", unsafe_allow_html=True)

# ================= DATES (COMPACT) =================
today = datetime.now().date()

st.write("### 📅 Dates")

row1 = st.columns(7, gap="small")
for i in range(7):
    d = today + timedelta(days=i)
    with row1[i]:
        st.markdown('<div class="date-row">', unsafe_allow_html=True)
        if st.button(d.strftime("%d"), key=f"d1_{i}",
                     type="primary" if str(d)==st.session_state.sel_date else "secondary"):
            st.session_state.sel_date = str(d)
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

row2 = st.columns(7, gap="small")
for i in range(7,14):
    d = today + timedelta(days=i)
    with row2[i-7]:
        st.markdown('<div class="date-row">', unsafe_allow_html=True)
        if st.button(d.strftime("%d"), key=f"d2_{i}",
                     type="primary" if str(d)==st.session_state.sel_date else "secondary"):
            st.session_state.sel_date = str(d)
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

st.divider()

# ================= HEADER =================
h = st.columns(4)
with h[0]: st.write("")
with h[1]: st.markdown("<div class='header'>T1</div>", unsafe_allow_html=True)
with h[2]: st.markdown("<div class='header'>T2</div>", unsafe_allow_html=True)
with h[3]: st.markdown("<div class='header'>T3</div>", unsafe_allow_html=True)

# ================= TABLE =================
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
                    st.markdown('<div class="mine">', unsafe_allow_html=True)
                    if st.button(f"❌ {b_name[:4]}", key=f"{t}_{i}"):
                        bookings = bookings.drop(match.index)
                        save_data(bookings, BOOKINGS_FILE)
                        st.rerun()
                    st.markdown('</div>', unsafe_allow_html=True)
                else:
                    st.markdown('<div class="taken">', unsafe_allow_html=True)
                    st.button(b_name[:5], key=f"{t}_{i}", disabled=True)
                    st.markdown('</div>', unsafe_allow_html=True)

            else:
                st.markdown('<div class="free">', unsafe_allow_html=True)
                if st.button("Free", key=f"{t}_{i}"):
                    new_b = pd.DataFrame([{
                        "User": st.session_state.user,
                        "Name": st.session_state.name,
                        "Date": st.session_state.sel_date,
                        "Table": t_n,
                        "Time": t
                    }])
                    save_data(pd.concat([bookings,new_b]), BOOKINGS_FILE)
                    st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)

st.markdown("</div>", unsafe_allow_html=True)

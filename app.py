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

# SESSION
if "user" not in st.session_state: st.session_state.user = None
if "name" not in st.session_state: st.session_state.name = None
if "role" not in st.session_state: st.session_state.role = None
if "sel_date" not in st.session_state: st.session_state.sel_date = str(datetime.now().date())

# ================= LOGIN =================
if st.session_state.user is None:
    st.title("🎱 Pool Booking")

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

# ================= CSS =================
st.markdown("""
<style>

/* ===== GLOBAL WIDTH ===== */
.block-container {
    max-width: 420px !important;
    margin: auto !important;
    padding: 6px !important;
}

/* ===== NO STACKING EVER ===== */
[data-testid="stHorizontalBlock"] {
    display: flex !important;
    flex-wrap: nowrap !important;
    gap: 4px !important;
}

/* ===== FORCE EQUAL COLUMN WIDTH ===== */
[data-testid="column"] {
    flex: 1 1 0 !important;
    min-width: 0 !important;
}

/* ===== TABLE BUTTONS (FIXED WIDTH) ===== */
.table-btn button {
    width: 80px !important;
    min-width: 80px !important;
    max-width: 80px !important;
    height: 38px !important;
    border-radius: 10px !important;
    font-size: 11px !important;
}

/* ===== DATE BUTTONS (4x BIGGER) ===== */
.date-btn button {
    width: 100% !important;
    height: 40px !important;
    font-size: 12px !important;
    border-radius: 12px !important;
}

/* ===== COLORS ===== */
.free button {
    background: linear-gradient(135deg,#e8fbe8,#d2f5d2) !important;
    color: #1a7f37 !important;
}

.mine button {
    background: linear-gradient(135deg,#e6f0ff,#cfe2ff) !important;
    color: #1d4ed8 !important;
}

.taken button {
    background: #f1f1f1 !important;
    color: #666 !important;
}

/* ===== HEADER ===== */
.header {
    text-align:center;
    background: linear-gradient(135deg,#2f3542,#4a5568);
    color:white;
    padding:8px 0;
    border-radius:10px;
    font-size:12px;
}

/* ===== TIME ===== */
.time {
    text-align:center;
    font-size:11px;
    font-weight:600;
}

/* ===== SCROLL ===== */
.scroll {
    height:65vh;
    overflow-y:auto;
}

</style>
""", unsafe_allow_html=True)

# ================= DATES (BIG BUTTONS) =================
today = datetime.now().date()
st.write("### 📅 Dates")

row1 = st.columns(7)
for i in range(7):
    d = today + timedelta(days=i)
    d_str = str(d)
    with row1[i]:
        st.markdown('<div class="date-btn">', unsafe_allow_html=True)
        if st.button(d.strftime("%d"), key=f"d1_{i}",
                     type="primary" if st.session_state.sel_date == d_str else "secondary"):
            st.session_state.sel_date = d_str
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

row2 = st.columns(7)
for i in range(7,14):
    d = today + timedelta(days=i)
    d_str = str(d)
    with row2[i-7]:
        st.markdown('<div class="date-btn">', unsafe_allow_html=True)
        if st.button(d.strftime("%d"), key=f"d2_{i}",
                     type="primary" if st.session_state.sel_date == d_str else "secondary"):
            st.session_state.sel_date = d_str
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
            st.markdown('<div class="table-btn">', unsafe_allow_html=True)

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

            st.markdown('</div>', unsafe_allow_html=True)

st.markdown("</div>", unsafe_allow_html=True)

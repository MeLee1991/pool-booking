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

# ================= SIDEBAR (ADMIN FIXED) =================
with st.sidebar:
    st.write(f"👤 {st.session_state.name}")

    if st.session_state.role == "admin":
        st.write(f"Bookings: {len(bookings)}")
        st.download_button("Download CSV", bookings.to_csv(index=False), "bookings.csv")

    if st.button("Logout"):
        st.session_state.clear()
        st.rerun()

# ================= CSS =================
st.markdown("""
<style>
.block-container {
    max-width: 360px;
    margin:auto;
    padding-top: 10px;
}

/* columns FIX */
div[data-testid="stHorizontalBlock"] {
    display:flex !important;
    flex-wrap:nowrap !important;
    gap:4px !important;
}

/* EXACT 4 columns */
[data-testid="column"] {
    flex:1 !important;
    min-width:0 !important;
}

/* buttons */
.stButton > button {
    width:100% !important;
    height:32px !important;
    font-size:10px !important;
    border-radius:8px !important;
    padding:0 !important;
}

/* DATE buttons */
.date button { height:34px !important; }

/* COLORS */
.tod button { background:#22c55e !important; color:white; }
.tom button { background:#3b82f6 !important; color:white; }
.sel button { background:#4f46e5 !important; color:white; }

.free button { background:#bbf7d0 !important; }
.mine button { background:#93c5fd !important; }
.taken button { background:#e5e7eb !important; }

/* TIME COLORS (every 4 hours) */
.time0 { background:#f3f4f6 !important; }
.time1 { background:#e0f2fe !important; }
.time2 { background:#fef3c7 !important; }
.time3 { background:#ede9fe !important; }

.timebox {
    height:32px;
    border-radius:8px;
    display:flex;
    align-items:center;
    justify-content:center;
    font-size:10px;
    font-weight:600;
}
</style>
""", unsafe_allow_html=True)

# ================= DATES (2 ROWS FIXED) =================
today = datetime.now().date()

for row in [range(7), range(7,14)]:
    cols = st.columns(7)
    for i in row:
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

st.markdown("<hr style='margin:6px 0'>", unsafe_allow_html=True)

# ================= TABLE =================
HOURS = [f"{h:02d}:{m}" for h in range(6,24) for m in ["00","30"]]

# HEADER
h = st.columns(4)
h[0].markdown("**T**")
h[1].markdown("**1**")
h[2].markdown("**2**")
h[3].markdown("**3**")

# ROWS
for idx, t in enumerate(HOURS):

    cols = st.columns(4)

    color_class = f"time{(idx//8)%4}"

    # TIME (NOT CLICKABLE anymore)
    with cols[0]:
        st.markdown(
            f'<div class="timebox {color_class}">{t}</div>',
            unsafe_allow_html=True
        )

    # TABLES
    for i in range(3):
        table = f"Table {i+1}"

        match = bookings[
            (bookings["Table"]==table)&
            (bookings["Time"]==t)&
            (bookings["Date"]==st.session_state.sel_date)
        ]

        with cols[i+1]:
            if not match.empty:
                user = match.iloc[0]["User"]
                name = match.iloc[0]["Name"][:4]

                if user == st.session_state.user:
                    st.markdown('<div class="mine">', unsafe_allow_html=True)
                    if st.button(f"❌ {name}", key=f"{t}_{i}"):
                        bookings = bookings.drop(match.index)
                        save_data(bookings, BOOKINGS_FILE)
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
                    bookings = pd.concat([bookings,new])
                    save_data(bookings, BOOKINGS_FILE)
                    st.rerun()
                st.markdown("</div>", unsafe_allow_html=True)

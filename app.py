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

# ================= SIMPLE CSS (SAFE) =================
st.markdown("""
<style>
.block-container { max-width: 420px; margin:auto; }

/* buttons */
.stButton > button {
    height:34px;
    font-size:11px;
    border-radius:8px;
}

/* states */
.free button { background:#bbf7d0 !important; }
.mine button { background:#93c5fd !important; }
.taken button { background:#e5e7eb !important; }

/* dates */
.sel button { background:#4f46e5 !important; color:white; }
.tod button { background:#22c55e !important; color:white; }
.tom button { background:#3b82f6 !important; color:white; }

/* time blocks */
.timeA { background:#f3f4f6; padding:6px; border-radius:8px; text-align:center; }
.timeB { background:#e0f2fe; padding:6px; border-radius:8px; text-align:center; }
.timeC { background:#fef3c7; padding:6px; border-radius:8px; text-align:center; }
.timeD { background:#ede9fe; padding:6px; border-radius:8px; text-align:center; }
</style>
""", unsafe_allow_html=True)

# ================= DATES (WORKING CLEAN) =================
today = datetime.now().date()

for row in [range(7), range(7,14)]:
    cols = st.columns(7)
    for i in row:
        d = today + timedelta(days=i)
        d_str = str(d)

        label = f"{d.day}.{d.strftime('%a')}"
        cls = ""

        if i == 0:
            label = "TOD"
            cls = "tod"
        elif i == 1:
            label = "TOM"
            cls = "tom"

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

# header
h = st.columns(4)
h[0].write("T")
h[1].write("1")
h[2].write("2")
h[3].write("3")

for idx, t in enumerate(HOURS):

    cols = st.columns(4)

    # time color group (every 4h)
    group = ["timeA","timeB","timeC","timeD"][(idx//8)%4]

    # TIME (not clickable)
    with cols[0]:
        st.markdown(f'<div class="{group}">{t}</div>', unsafe_allow_html=True)

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

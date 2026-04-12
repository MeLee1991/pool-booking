import os
import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(layout="wide")

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

# test user
if "tom3@gmail.com" not in users["Email"].values:
    users = pd.concat([users, pd.DataFrame([{
        "Email":"tom3@gmail.com",
        "Name":"Tom",
        "Password":"1234",
        "Role":"admin"
    }])])
    save(users, USERS_FILE)

# ================= SESSION =================
for k in ["user","name","role","date"]:
    if k not in st.session_state:
        st.session_state[k] = None

if not st.session_state.date:
    st.session_state.date = str(datetime.now().date())

# ================= LOGIN =================
if st.session_state.user is None:
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

# ================= CSS =================
st.markdown("""
<style>

.block-container {
    max-width: 100% !important;
    padding: 0.4rem !important;
}

/* GRID */
div[data-testid="stHorizontalBlock"] {
    display:grid !important;
    grid-template-columns: repeat(4, 1fr) !important;
    gap:3px !important;
}

/* BUTTONS */
.stButton > button {
    width:100% !important;
    height:36px !important;
    font-size:9px !important;
    border-radius:8px !important;
    padding:0 2px !important;
    overflow:hidden !important;
    white-space:nowrap !important;
    text-overflow:ellipsis !important;
}

/* COLORS */
.free button { background:#bbf7d0 !important; }   /* light green */
.taken button { background:#fecaca !important; }  /* light red */
.mine button { background:#93c5fd !important; }   /* blue */

/* TIME BANDS */
.band0 button { background:#f3f4f6 !important; }
.band1 button { background:#e0f2fe !important; }
.band2 button { background:#fef3c7 !important; }
.band3 button { background:#ede9fe !important; }

</style>
""", unsafe_allow_html=True)

# ================= HEADER =================
st.write(f"👤 {st.session_state.name} | {st.session_state.date}")

# ================= TABLE =================
HOURS = [f"{h:02d}:{m}" for h in range(6,24) for m in ["00","30"]]

# header
h = st.columns(4)
h[0].button("Time", disabled=True)
h[1].button("T1", disabled=True)
h[2].button("T2", disabled=True)
h[3].button("T3", disabled=True)

# rows
for idx, t in enumerate(HOURS):

    cols = st.columns(4)

    # 4-hour band (8 slots)
    band = f"band{(idx//8)%4}"

    # TIME COLUMN (same button!)
    with cols[0]:
        st.markdown(f'<div class="{band}">', unsafe_allow_html=True)
        st.button(t, disabled=True, key=f"time_{t}")
        st.markdown("</div>", unsafe_allow_html=True)

    for i in range(3):
        table = f"Table {i+1}"

        match = bookings[
            (bookings["Table"]==table) &
            (bookings["Time"]==t) &
            (bookings["Date"]==st.session_state.date)
        ]

        with cols[i+1]:

            if not match.empty:
                user = match.iloc[0]["User"]
                name = match.iloc[0]["Name"][:6]  # FIT TEXT

                if user == st.session_state.user:
                    st.markdown('<div class="mine">', unsafe_allow_html=True)
                    if st.button(f"✕{name}", key=f"{t}_{i}"):
                        bookings = bookings.drop(match.index)
                        save(bookings, BOOKINGS_FILE)
                        st.rerun()
                    st.markdown("</div>", unsafe_allow_html=True)

                else:
                    st.markdown('<div class="taken">', unsafe_allow_html=True)
                    st.button(name, disabled=True, key=f"{t}_{i}")
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

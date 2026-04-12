import os
import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(layout="centered")

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

/* compact container */
.block-container {
    max-width: 300px !important;
    margin: auto;
    padding: 0.3rem !important;
}

/* 4 tight columns */
div[data-testid="stHorizontalBlock"] {
    display:flex !important;
    flex-wrap:nowrap !important;
    gap:3px !important;
}

/* fixed column width */
div[data-testid="column"] {
    flex: 0 0 65px !important;
    max-width: 65px !important;
    min-width: 65px !important;
}

/* FIXED BUTTON SIZE */
.stButton > button {
    width:65px !important;
    height:34px !important;
    font-size:9px !important;
    border-radius:8px !important;
    padding:0 !important;

    display:flex !important;
    align-items:center !important;
    justify-content:center !important;
}

/* COLORS */
.free button {
    background:#bbf7d0 !important;   /* green */
}

.taken button {
    background:#fecaca !important;   /* red */
}

.mine button {
    background:#93c5fd !important;   /* blue */
}

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
for t in HOURS:
    cols = st.columns(4)

    # TIME COLUMN (same size button)
    with cols[0]:
        st.button(t, disabled=True, key=f"time_{t}")

    for i in range(3):
        table = f"Table {i+1}"

        match = bookings[
            (bookings["Table"] == table) &
            (bookings["Time"] == t) &
            (bookings["Date"] == st.session_state.date)
        ]

        with cols[i+1]:

            if not match.empty:
                user = match.iloc[0]["User"]

                if user == st.session_state.user:
                    st.markdown('<div class="mine">', unsafe_allow_html=True)
                    if st.button("X", key=f"{t}_{i}"):
                        bookings = bookings.drop(match.index)
                        save(bookings, BOOKINGS_FILE)
                        st.rerun()
                    st.markdown("</div>", unsafe_allow_html=True)

                else:
                    st.markdown('<div class="taken">', unsafe_allow_html=True)
                    st.button("X", key=f"{t}_{i}", disabled=True)
                    st.markdown("</div>", unsafe_allow_html=True)

            else:
                st.markdown('<div class="free">', unsafe_allow_html=True)
                if st.button("", key=f"{t}_{i}"):
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

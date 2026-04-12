import os
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

st.set_page_config(page_title="Pool", layout="centered")

# ================= FILES =================
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

# ================= TEST USER =================
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
    st.title("Pool")

    email = st.text_input("Email", value="tom3@gmail.com")
    password = st.text_input("Password", type="password", value="1234")

    if st.button("Login"):
        m = users[(users["Email"] == email) & (users["Password"] == password)]
        if not m.empty:
            st.session_state.user = email
            st.session_state.name = m.iloc[0]["Name"]
            st.session_state.role = m.iloc[0]["Role"]
            st.rerun()

    st.stop()

# ================= CSS =================
st.markdown("""
<style>
.block-container {
    max-width: 300px !important;
    margin: auto;
    padding: 0.2rem !important;
}

/* horizontal rows */
div[data-testid="stHorizontalBlock"] {
    display: flex !important;
    flex-wrap: nowrap !important;
    gap: 2px !important;
}

/* FIXED compact columns */
div[data-testid="column"] {
    flex: 0 0 65px !important;
    width: 65px !important;
    min-width: 65px !important;
}

/* buttons */
.stButton > button {
    width: 100% !important;
    height: 34px !important;
    font-size: 9px !important;
    border-radius: 8px !important;
    padding: 0 !important;
}

/* states */
.free button { background:#bbf7d0 !important; }
.mine button { background:#93c5fd !important; }
.taken button { background:#e5e7eb !important; }

/* date buttons */
.date button {
    width: 100% !important;
    height: 30px !important;
    font-size: 9px !important;
}

.sel button {
    background:#4f46e5 !important;
    color:white !important;
}
</style>
""", unsafe_allow_html=True)

# ================= HEADER =================
st.write(f"👤 {st.session_state.name} | {st.session_state.date}")

# ================= DATE PICKER =================
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
h[0].write("Time")
h[1].write("T1")
h[2].write("T2")
h[3].write("T3")

# rows
for t in HOURS:
    cols = st.columns(4)

    cols[0].write(t)

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
                    new = pd.DataFrame([{
                        "User": st.session_state.user,
                        "Name": st.session_state.name,
                        "Date": st.session_state.date,
                        "Table": table,
                        "Time": t
                    }])
                    bookings = pd.concat([bookings, new], ignore_index=True)
                    save(bookings, BOOKINGS_FILE)
                    st.rerun()
                st.markdown("</div>", unsafe_allow_html=True)

import streamlit as st
import pandas as pd
import os
from datetime import datetime, timedelta

st.set_page_config(layout="centered")

# ================= DATA =================
USERS_FILE = "users.csv"
BOOKINGS_FILE = "bookings.csv"

def load(file, cols):
    if os.path.exists(file):
        return pd.read_csv(file, dtype=str)
    return pd.DataFrame(columns=cols)

def save(df, file):
    df.to_csv(file, index=False)

users = load(USERS_FILE, ["Email","Name","Password","Role"])
bookings = load(BOOKINGS_FILE, ["User","Name","Date","Table","Time"])

# default user
if "tom3@gmail.com" not in users["Email"].values:
    users = pd.concat([users, pd.DataFrame([{
        "Email":"tom3@gmail.com",
        "Name":"Tom",
        "Password":"1234",
        "Role":"admin"
    }])])
    save(users, USERS_FILE)

# ================= SESSION =================
for k in ["user","name","role","date","page"]:
    if k not in st.session_state:
        st.session_state[k] = None

if not st.session_state.date:
    st.session_state.date = str(datetime.now().date())

if not st.session_state.page:
    st.session_state.page = "grid"

# ================= LOGIN =================
if st.session_state.user is None:
    e = st.text_input("Email", value="tom3@gmail.com")
    p = st.text_input("Password", type="password", value="1234")

    if st.button("Login"):
        m = users[(users["Email"]==e)&(users["Password"]==p)]
        if not m.empty:
            st.session_state.user = e
            st.session_state.name = m.iloc[0]["Name"]
            st.session_state.role = m.iloc[0]["Role"]
            st.rerun()
    st.stop()

# ================= ADMIN =================
if st.session_state.page == "admin":
    st.title("Admin")

    if st.button("← Back"):
        st.session_state.page = "grid"
        st.rerun()

    edited = st.data_editor(users, use_container_width=True)

    if st.button("Save"):
        save(edited, USERS_FILE)

    st.stop()

# ================= HEADER =================
st.markdown(f"👤 **{st.session_state.name} | {st.session_state.date}**")

if st.session_state.role == "admin":
    if st.button("⚙️ Admin", use_container_width=True):
        st.session_state.page = "admin"
        st.rerun()

# ================= CSS =================
st.markdown("""
<style>

.block-container {
    max-width:360px !important;
    margin:auto !important;
}

/* DATE GRID */
.date-row {
    display:flex;
    gap:4px;
    margin-bottom:4px;
}
.date-row button {
    flex:1;
    height:34px;
    font-size:10px;
    border-radius:10px;
}

/* TABLE GRID */
.table {
    display:grid;
    grid-template-columns: 60px repeat(3, 1fr);
    gap:4px;
}

/* BUTTONS */
.cell button {
    width:100%;
    height:34px;
    font-size:10px;
    border-radius:10px;
    padding:0;
}

/* COLORS */
.free button { background:#bbf7d0 !important; }
.taken button { background:#fecaca !important; }
.mine button { background:#93c5fd !important; }

/* TIME COLORS */
.tA button { background:#f3f4f6 !important; }
.tB button { background:#e0f2fe !important; }
.tC button { background:#fef3c7 !important; }
.tD button { background:#ede9fe !important; }

</style>
""", unsafe_allow_html=True)

# ================= DATES =================
today = datetime.now().date()

for r in [range(7), range(7,14)]:
    st.markdown('<div class="date-row">', unsafe_allow_html=True)
    for i in r:
        d = today + timedelta(days=i)
        ds = str(d)

        label = "TOD" if i==0 else ("TOM" if i==1 else d.strftime("%a"))

        if st.button(f"{label}\n{d.day}", key=f"d_{ds}"):
            st.session_state.date = ds
            st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

st.divider()

# ================= TABLE =================
HOURS = [f"{h:02d}:{m}" for h in range(6,24) for m in ["00","30"]]

st.markdown('<div class="table">', unsafe_allow_html=True)

# HEADER
st.markdown("**Time**")
st.markdown("**T1**")
st.markdown("**T2**")
st.markdown("**T3**")

for idx, t in enumerate(HOURS):

    band = ["tA","tB","tC","tD"][(idx//8)%4]

    # TIME
    st.markdown(f'<div class="cell {band}">', unsafe_allow_html=True)
    st.button(t, key=f"time_{t}")
    st.markdown('</div>', unsafe_allow_html=True)

    # TABLES
    for i in range(3):
        table = f"Table {i+1}"

        match = bookings[
            (bookings["Table"]==table)&
            (bookings["Time"]==t)&
            (bookings["Date"]==st.session_state.date)
        ]

        if not match.empty:
            name = match.iloc[0]["Name"][:10]
            user = match.iloc[0]["User"]

            if user == st.session_state.user:
                st.markdown('<div class="cell mine">', unsafe_allow_html=True)
                if st.button(f"✖ {name}", key=f"{t}_{i}"):
                    bookings = bookings.drop(match.index)
                    save(bookings, BOOKINGS_FILE)
                    st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)
            else:
                st.markdown('<div class="cell taken">', unsafe_allow_html=True)
                st.button(name, key=f"{t}_{i}", disabled=True)
                st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="cell free">', unsafe_allow_html=True)
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
            st.markdown('</div>', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

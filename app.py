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

if "users" not in st.session_state:
    st.session_state.users = load_data(USERS_FILE, ["Email","Name","Password","Role"])
if "bookings" not in st.session_state:
    st.session_state.bookings = load_data(BOOKINGS_FILE, ["User","Name","Date","Table","Time"])

for k in ["user","name","role","sel_date","page"]:
    if k not in st.session_state:
        st.session_state[k] = None

if not st.session_state.sel_date:
    st.session_state.sel_date = str(datetime.now().date())
if not st.session_state.page:
    st.session_state.page = "Booking"

# ================= LOGIN =================
if st.session_state.user is None:
    st.title("Pool Login")

    e = st.text_input("Email")
    p = st.text_input("Password", type="password")

    if st.button("Login"):
        m = st.session_state.users[
            (st.session_state.users["Email"]==e)&
            (st.session_state.users["Password"]==p)
        ]
        if not m.empty:
            st.session_state.user = e
            st.session_state.name = m.iloc[0]["Name"]
            st.session_state.role = m.iloc[0]["Role"]
            st.rerun()
    st.stop()

# ================= ADMIN =================
if st.session_state.page == "Admin":
    st.title("⚙️ Admin")

    if st.button("← Back"):
        st.session_state.page = "Booking"
        st.rerun()

    # TABLE VIEW
    st.subheader("Users")
    st.dataframe(st.session_state.users, use_container_width=True)

    st.divider()

    # ADD USER
    st.subheader("Add User")
    e = st.text_input("Email", key="a_email")
    n = st.text_input("Name", key="a_name")
    p = st.text_input("Password", key="a_pass")
    r = st.selectbox("Role", ["user","admin"], key="a_role")

    if st.button("Add"):
        new = pd.DataFrame([{"Email":e,"Name":n,"Password":p,"Role":r}])
        st.session_state.users = pd.concat([st.session_state.users,new], ignore_index=True)
        save_data(st.session_state.users, USERS_FILE)

        # reset
        st.session_state.a_email = ""
        st.session_state.a_name = ""
        st.session_state.a_pass = ""

        st.rerun()

    st.divider()

    # DELETE USER
    st.subheader("Delete User")
    u = st.selectbox("Select user", st.session_state.users["Email"])
    if st.button("Delete"):
        df = st.session_state.users
        st.session_state.users = df[df["Email"]!=u]
        save_data(st.session_state.users, USERS_FILE)
        st.rerun()

    st.stop()

# ================= HEADER =================
st.write(f"👤 {st.session_state.name} | {st.session_state.sel_date}")

if st.session_state.role == "admin":
    if st.button("⚙️ Admin"):
        st.session_state.page = "Admin"
        st.rerun()

# ================= CSS =================
st.markdown("""
<style>
.block-container { max-width:340px; margin:auto; }

div[data-testid="stHorizontalBlock"] {
    display:flex !important;
    flex-wrap:nowrap !important;
    gap:3px !important;
}

[data-testid="column"] {
    flex:0 0 auto !important;
    width:70px !important;
}

.stButton > button {
    width:70px !important;
    height:30px !important;
    font-size:9px !important;
    border-radius:6px !important;
}

/* states */
.free button { background:#bbf7d0 !important; }
.mine button { background:#93c5fd !important; }
.taken button { background:#e5e7eb !important; }

/* time */
.timeA { background:#f3f4f6; }
.timeB { background:#e0f2fe; }
.timeC { background:#fef3c7; }
.timeD { background:#ede9fe; }
</style>
""", unsafe_allow_html=True)

# ================= DATES =================
today = datetime.now().date()

for week in [range(7), range(7,14)]:
    cols = st.columns(7)
    for i in week:
        d = today + timedelta(days=i)
        d_str = str(d)

        label = f"{d.day}.{d.strftime('%a')}"
        if i == 0: label = "TOD"
        if i == 1: label = "TOM"

        with cols[i % 7]:
            if st.button(label, key=f"d_{d_str}"):
                st.session_state.sel_date = d_str
                st.rerun()

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
    block = ["timeA","timeB","timeC","timeD"][(idx//8)%4]

    # time
    cols[0].markdown(f"<div class='{block}'>{t}</div>", unsafe_allow_html=True)

    for i in range(3):
        table = f"Table {i+1}"

        match = st.session_state.bookings[
            (st.session_state.bookings["Table"]==table)&
            (st.session_state.bookings["Time"]==t)&
            (st.session_state.bookings["Date"]==st.session_state.sel_date)
        ]

        with cols[i+1]:
            if not match.empty:
                user = match.iloc[0]["User"]
                name = match.iloc[0]["Name"][:4]

                if user == st.session_state.user:
                    if st.button(f"❌ {name}", key=f"{t}_{i}"):
                        st.session_state.bookings = st.session_state.bookings.drop(match.index)
                        save_data(st.session_state.bookings, BOOKINGS_FILE)
                        st.rerun()
                else:
                    st.button(name, key=f"{t}_{i}", disabled=True)

            else:
                if st.button("+", key=f"{t}_{i}"):
                    new = pd.DataFrame([{
                        "User": st.session_state.user,
                        "Name": st.session_state.name,
                        "Date": st.session_state.sel_date,
                        "Table": table,
                        "Time": t
                    }])
                    st.session_state.bookings = pd.concat([st.session_state.bookings,new], ignore_index=True)
                    save_data(st.session_state.bookings, BOOKINGS_FILE)
                    st.rerun()

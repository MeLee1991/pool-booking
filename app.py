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

    e = st.text_input("Email").lower().strip()
    p = st.text_input("Password", type="password")

    if st.button("Login"):
        m = st.session_state.users[
            (st.session_state.users["Email"]==e) &
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
    st.title("Admin")

    if st.button("← Back"):
        st.session_state.page = "Booking"
        st.rerun()

    st.subheader("Users")
    st.dataframe(st.session_state.users)

    e = st.text_input("Email")
    n = st.text_input("Name")
    p = st.text_input("Password")
    r = st.selectbox("Role", ["user","admin"])

    if st.button("Add User"):
        new = pd.DataFrame([{"Email":e,"Name":n,"Password":p,"Role":r}])
        st.session_state.users = pd.concat([st.session_state.users,new], ignore_index=True)
        save_data(st.session_state.users, USERS_FILE)
        st.rerun()

    st.download_button("Download bookings", st.session_state.bookings.to_csv(index=False))
    st.stop()

# ================= CSS =================
st.markdown("""
<style>
.block-container { max-width: 320px; margin:auto; }

div[data-testid="stHorizontalBlock"] {
    display:flex !important;
    flex-wrap:nowrap !important;
    gap:3px !important;
}

[data-testid="column"] {
    flex:0 0 auto !important;
    width:70px !important;
}

/* buttons */
.stButton > button {
    width:70px !important;
    height:28px !important;
    font-size:9px !important;
    border-radius:6px !important;
}

/* date */
.date button { width:45px !important; height:30px !important; }
.sel button { background:#4f46e5 !important; color:white; }
.tod button { background:#22c55e !important; color:white; }
.tom button { background:#3b82f6 !important; color:white; }

/* states */
.free button { background:#bbf7d0 !important; }
.mine button { background:#93c5fd !important; }
.taken button { background:#e5e7eb !important; }

/* time blocks */
.timeA { background:#f3f4f6; padding:4px; border-radius:6px; text-align:center; }
.timeB { background:#e0f2fe; padding:4px; border-radius:6px; text-align:center; }
.timeC { background:#fef3c7; padding:4px; border-radius:6px; text-align:center; }
.timeD { background:#ede9fe; padding:4px; border-radius:6px; text-align:center; }
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

st.divider()

# ================= TABLE =================
HOURS = [f"{h:02d}:{m}" for h in range(6,24) for m in ["00","30"]]

# header
h = st.columns(4)
h[0].markdown("**T**")
h[1].markdown("**1**")
h[2].markdown("**2**")
h[3].markdown("**3**")

for idx, t in enumerate(HOURS):

    cols = st.columns(4)
    block = ["timeA","timeB","timeC","timeD"][(idx//8)%4]

    # TIME (not clickable)
    with cols[0]:
        st.markdown(f'<div class="{block}">{t}</div>', unsafe_allow_html=True)

    for i in range(3):
        table = f"Table {i+1}"

        match = st.session_state.bookings[
            (st.session_state.bookings["Table"]==table) &
            (st.session_state.bookings["Time"]==t) &
            (st.session_state.bookings["Date"]==st.session_state.sel_date)
        ]

        with cols[i+1]:
            if not match.empty:
                user = match.iloc[0]["User"]
                name = match.iloc[0]["Name"][:4]

                if user == st.session_state.user:
                    st.markdown('<div class="mine">', unsafe_allow_html=True)
                    if st.button(f"❌ {name}", key=f"{t}_{i}"):
                        st.session_state.bookings = st.session_state.bookings.drop(match.index)
                        save_data(st.session_state.bookings, BOOKINGS_FILE)
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
                    st.session_state.bookings = pd.concat([st.session_state.bookings,new], ignore_index=True)
                    save_data(st.session_state.bookings, BOOKINGS_FILE)
                    st.rerun()
                st.markdown("</div>", unsafe_allow_html=True)

# ================= HEADER =================
st.write(f"👤 {st.session_state.name} | {st.session_state.sel_date}")

if st.session_state.role == "admin":
    if st.button("Admin"):
        st.session_state.page = "Admin"
        st.rerun()

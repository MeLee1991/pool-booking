import streamlit as st
import pandas as pd
import os
from datetime import datetime, timedelta

st.set_page_config(layout="centered")

# ================= FILES =================
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

    edited = st.data_editor(users, num_rows="dynamic", use_container_width=True)

    if st.button("💾 Save"):
        save(edited, USERS_FILE)
        st.success("Saved")

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
    padding:0.5rem !important;
}

div[data-testid="stHorizontalBlock"] {
    display:flex !important;
    flex-wrap:nowrap !important;
    gap:4px !important;
}

[data-testid="column"] {
    flex:1 1 0 !important;
    min-width:0 !important;
}

.stButton > button {
    width:100% !important;
    height:36px !important;
    font-size:9px !important;
    border-radius:12px !important;
    padding:0 !important;
}

.free button { background:#bbf7d0 !important; }
.taken button { background:#fecaca !important; }
.mine button  { background:#93c5fd !important; }

.timeA button { background:#f3f4f6 !important; }
.timeB button { background:#e0f2fe !important; }
.timeC button { background:#fef3c7 !important; }
.timeD button { background:#ede9fe !important; }

</style>
""", unsafe_allow_html=True)

# ================= DATE PICKER =================
today = datetime.now().date()

cols = st.columns(7)
for i in range(14):
    d = today + timedelta(days=i)
    ds = str(d)

    label = "TOD" if i==0 else ("TOM" if i==1 else d.strftime("%a"))

    with cols[i % 7]:
        if st.button(f"{label}\n{d.day}", key=f"d_{ds}"):
            st.session_state.date = ds
            st.rerun()

# ================= TABLE =================
HOURS = [f"{h:02d}:{m}" for h in range(6,24) for m in ["00","30"]]

h = st.columns(4)
h[0].markdown("**Time**")
h[1].markdown("**T1**")
h[2].markdown("**T2**")
h[3].markdown("**T3**")

for idx, t in enumerate(HOURS):
    cols = st.columns(4)
    band = ["timeA","timeB","timeC","timeD"][(idx//8)%4]

    with cols[0]:
        st.markdown(f'<div class="{band}">', unsafe_allow_html=True)
        st.button(t, key=f"time_{t}")
        st.markdown("</div>", unsafe_allow_html=True)

    for i in range(3):
        table = f"Table {i+1}"

        match = bookings[
            (bookings["Table"]==table)&
            (bookings["Time"]==t)&
            (bookings["Date"]==st.session_state.date)
        ]

        with cols[i+1]:
            if not match.empty:
                name = match.iloc[0]["Name"][:10]
                user = match.iloc[0]["User"]

                if user == st.session_state.user:
                    st.markdown('<div class="mine">', unsafe_allow_html=True)
                    if st.button(f"✖ {name}", key=f"{t}_{i}"):
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

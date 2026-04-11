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
if "page" not in st.session_state:
    st.session_state.page = "booking"

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

# ================= TOP NAV =================
c1, c2 = st.columns([3,1])
c1.write(f"👤 {st.session_state.name}")
if st.session_state.role == "admin":
    if c2.button("Admin"):
        st.session_state.page = "admin"
        st.rerun()

if st.session_state.page == "admin":
    st.title("Admin")
    st.write(f"Bookings: {len(bookings)}")
    st.download_button("Download CSV", bookings.to_csv(index=False), "bookings.csv")
    if st.button("⬅ Back"):
        st.session_state.page = "booking"
        st.rerun()
    st.stop()

# ================= DATE PICKER =================
today = datetime.now().date()

weeks = [
    [today + timedelta(days=i) for i in range(7)],
    [today + timedelta(days=i) for i in range(7,14)]
]

for week in weeks:
    cols = st.columns(7)
    for i, d in enumerate(week):
        d_str = str(d)

        label = f"{d.day}.{d.strftime('%a')}"

        if d == today:
            label = "TOD"
        elif d == today + timedelta(days=1):
            label = "TOM"

        if cols[i].button(label, key=f"d_{d_str}"):
            st.session_state.sel_date = d_str
            st.rerun()

st.divider()

# ================= GRID =================
HOURS = [f"{h:02d}:{m}" for h in range(6,24) for m in ["00","30"]]

# headers
hcols = st.columns(4)
hcols[0].markdown("**Time**")
hcols[1].markdown("**T1**")
hcols[2].markdown("**T2**")
hcols[3].markdown("**T3**")

# rows
for idx, t in enumerate(HOURS):

    cols = st.columns(4)

    # time (colored blocks every 4h)
    block = (idx // 8) % 4
    colors = ["#f3f4f6","#e0f2fe","#fef3c7","#ede9fe"]
    cols[0].markdown(
        f"<div style='background:{colors[block]};padding:6px;border-radius:6px;text-align:center;font-size:11px'>{t}</div>",
        unsafe_allow_html=True
    )

    for i in range(3):
        table = f"Table {i+1}"

        match = bookings[
            (bookings["Table"]==table)&
            (bookings["Time"]==t)&
            (bookings["Date"]==st.session_state.sel_date)
        ]

        if not match.empty:
            user = match.iloc[0]["User"]
            name = match.iloc[0]["Name"][:4]

            if user == st.session_state.user:
                if cols[i+1].button(f"❌ {name}", key=f"{t}_{i}"):
                    bookings = bookings.drop(match.index)
                    save_data(bookings, BOOKINGS_FILE)
                    st.rerun()
            else:
                cols[i+1].button(name, key=f"{t}_{i}", disabled=True)

        else:
            if cols[i+1].button("+", key=f"{t}_{i}"):
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

import streamlit as st
import pandas as pd
import os
from datetime import datetime, timedelta

st.set_page_config(layout="wide")

# ===== CSS (FORCE GRID, NO STACKING) =====
st.markdown("""
<style>

/* FORCE columns to stay in one row */
[data-testid="column"] {
    flex: 1 1 0% !important;
    min-width: 0 !important;
}

/* remove big side paddings */
.block-container {
    padding: 6px 6px 6px 6px !important;
}

/* buttons tight + same size */
.stButton button {
    width: 100%;
    height: 36px;
    font-size: 10px;
    border-radius: 10px;
    padding: 0;
}

/* colors */
.free button { background:#bbf7d0 !important; }
.taken button { background:#fecaca !important; }

/* time cell */
.timebox {
    background:#e5e7eb;
    border-radius:10px;
    text-align:center;
    padding:6px 0;
    font-size:10px;
}

</style>
""", unsafe_allow_html=True)

# ===== USERS =====
USERS = {
    "tom3@gmail.com": {"pass": "1234", "role": "admin"},
    "user@gmail.com": {"pass": "1234", "role": "user"}
}

# ===== FILE =====
FILE = "bookings.csv"

def load():
    if os.path.exists(FILE):
        return pd.read_csv(FILE, dtype=str)
    return pd.DataFrame(columns=["Name","Date","Table","Time"])

def save(df):
    df.to_csv(FILE, index=False)

bookings = load()

# ===== SESSION =====
if "logged" not in st.session_state:
    st.session_state.logged = False

if "user" not in st.session_state:
    st.session_state.user = ""

if "role" not in st.session_state:
    st.session_state.role = "user"

if "date" not in st.session_state:
    st.session_state.date = str(datetime.now().date())

# ===== LOGIN =====
if not st.session_state.logged:

    st.title("Login")

    email = st.text_input("Email", value="tom3@gmail.com")
    password = st.text_input("Password", type="password", value="1234")

    if st.button("Login"):
        if email in USERS and USERS[email]["pass"] == password:
            st.session_state.logged = True
            st.session_state.user = email
            st.session_state.role = USERS[email]["role"]
            st.rerun()
        else:
            st.error("Wrong login")

    st.stop()

# ===== SIDEBAR =====
with st.sidebar:
    st.write(f"👤 {st.session_state.user}")

    if st.button("Logout"):
        st.session_state.logged = False
        st.rerun()

    if st.session_state.role == "admin":
        st.divider()
        st.subheader("Admin")

        df_edit = st.data_editor(bookings, use_container_width=True)

        if st.button("Save"):
            save(df_edit)
            st.success("Saved")

# ===== HEADER =====
st.markdown(f"### 👤 {st.session_state.user} | {st.session_state.date}")

# ===== DATES (GRID 4 COLS) =====
today = datetime.now().date()
date_cols = st.columns(4)

for i in range(7):
    d = today + timedelta(days=i)
    ds = str(d)

    col = date_cols[i % 4]

    if col.button(f"{d.strftime('%a')} {d.day}", key=f"d{i}"):
        st.session_state.date = ds
        st.rerun()

# ===== TABLE =====
HOURS = [f"{h:02d}:{m}" for h in range(6,22) for m in ["00","30"]]

# header
cols = st.columns([1,1,1,1], gap="small")
cols[0].markdown("**Time**")
cols[1].markdown("**T1**")
cols[2].markdown("**T2**")
cols[3].markdown("**T3**")

# rows
for t in HOURS:

    cols = st.columns([1,1,1,1], gap="small")

    cols[0].markdown(f"<div class='timebox'>{t}</div>", unsafe_allow_html=True)

    for i in range(1,4):
        table = f"T{i}"

        match = bookings[
            (bookings["Date"]==st.session_state.date) &
            (bookings["Table"]==table) &
            (bookings["Time"]==t)
        ]

        if not match.empty:
            name = match.iloc[0]["Name"][:10]

            with cols[i]:
                st.markdown('<div class="taken">', unsafe_allow_html=True)
                if st.button(f"✖ {name}", key=f"{t}_{table}"):
                    bookings = bookings[~(
                        (bookings["Date"]==st.session_state.date) &
                        (bookings["Table"]==table) &
                        (bookings["Time"]==t)
                    )]
                    save(bookings)
                    st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)

        else:
            with cols[i]:
                st.markdown('<div class="free">', unsafe_allow_html=True)
                if st.button("+", key=f"{t}_{table}"):
                    bookings = pd.concat([bookings, pd.DataFrame([{
                        "Name": st.session_state.user.split("@")[0],
                        "Date": st.session_state.date,
                        "Table": table,
                        "Time": t
                    }])])
                    save(bookings)
                    st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)

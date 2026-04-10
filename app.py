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
if "user" not in st.session_state: st.session_state.user = None
if "name" not in st.session_state: st.session_state.name = None
if "role" not in st.session_state: st.session_state.role = None
if "sel_date" not in st.session_state:
    st.session_state.sel_date = str(datetime.now().date())

# ================= LOGIN =================
if st.session_state.user is None:
    st.title("🎱 Pool Booking")

    e = st.text_input("Email")
    p = st.text_input("Password", type="password")

    if st.button("Login"):
        match = users[(users["Email"]==e)&(users["Password"]==p)]
        if not match.empty:
            st.session_state.user = e
            st.session_state.name = match.iloc[0]["Name"]
            st.session_state.role = match.iloc[0]["Role"]
            st.rerun()
    st.stop()

# ================= NAV =================
st.sidebar.write(f"👤 {st.session_state.name}")
page = st.sidebar.radio("Menu",
    ["Booking","Admin"] if st.session_state.role=="admin" else ["Booking"]
)

if st.sidebar.button("Logout"):
    st.session_state.clear()
    st.rerun()

# ================= CSS =================
st.markdown("""
<style>

/* layout */
.block-container {
    max-width: 320px !important;
    margin: auto !important;
}

/* dates */
.date-grid {
    display: grid;
    grid-template-columns: repeat(7, 1fr);
    gap: 4px;
    margin-bottom: 6px;
}

.date-btn button {
    width: 100%;
    height: 36px;
    font-size: 11px;
    border-radius: 10px;
}

.sel button {
    background:#4f46e5 !important;
    color:white !important;
}

/* table */
.grid {
    display: grid;
    grid-template-columns: 60px 60px 60px 60px;
    gap: 2px;
}

.cell {
    width: 60px;
    height: 28px;
    display:flex;
    align-items:center;
    justify-content:center;
}

/* button */
.cell button {
    width:100%;
    height:100%;
    font-size:9px;
    border-radius:6px;
}

/* states */
.free button { background:#dcfce7; }
.mine button { background:#dbeafe; }
.taken button { background:#f3f4f6; }
.time button { background:#e5e7eb; font-weight:bold; }

/* 4h grouping */
.rowA { background:#ffffff; }
.rowB { background:#eef2ff; }

/* scroll */
.scroll {
    height: 70vh;
    overflow-y:auto;
}

</style>
""", unsafe_allow_html=True)

# ================= BOOKING =================
if page == "Booking":

    today = datetime.now().date()

    # ===== DATES =====
    st.markdown('<div class="date-grid">', unsafe_allow_html=True)
    for i in range(14):
        d = today + timedelta(days=i)
        cls = "sel" if str(d)==st.session_state.sel_date else ""
        st.markdown(f'<div class="date-btn {cls}">', unsafe_allow_html=True)
        if st.button(d.strftime("%d"), key=f"d_{i}"):
            st.session_state.sel_date = str(d)
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # ===== GRID TABLE =====
    st.markdown('<div class="scroll"><div class="grid">', unsafe_allow_html=True)

    HOURS = [f"{h:02d}:{m}" for h in range(8,24) for m in ["00","30"]]

    for idx, t in enumerate(HOURS):

        block = "rowA" if (idx // 8) % 2 == 0 else "rowB"

        # TIME
        st.markdown(f'<div class="cell time {block}">', unsafe_allow_html=True)
        st.button(t, key=f"time_{t}")
        st.markdown('</div>', unsafe_allow_html=True)

        for i in range(3):
            t_n = f"Table {i+1}"

            match = bookings[
                (bookings["Table"]==t_n)&
                (bookings["Time"]==t)&
                (bookings["Date"]==st.session_state.sel_date)
            ]

            st.markdown(f'<div class="cell {block}">', unsafe_allow_html=True)

            if not match.empty:
                b_user = match.iloc[0]["User"]
                b_name = match.iloc[0]["Name"]

                if b_user == st.session_state.user:
                    st.markdown('<div class="mine">', unsafe_allow_html=True)
                    if st.button(f"❌ {b_name[:3]}", key=f"{t}_{i}"):
                        bookings = bookings.drop(match.index)
                        save_data(bookings, BOOKINGS_FILE)
                        st.rerun()
                    st.markdown('</div>', unsafe_allow_html=True)
                else:
                    st.markdown('<div class="taken">', unsafe_allow_html=True)
                    st.button(b_name[:4], key=f"{t}_{i}", disabled=True)
                    st.markdown('</div>', unsafe_allow_html=True)
            else:
                st.markdown('<div class="free">', unsafe_allow_html=True)
                if st.button("+", key=f"{t}_{i}"):
                    new = pd.DataFrame([{
                        "User": st.session_state.user,
                        "Name": st.session_state.name,
                        "Date": st.session_state.sel_date,
                        "Table": t_n,
                        "Time": t
                    }])
                    save_data(pd.concat([bookings,new]), BOOKINGS_FILE)
                    st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)

            st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('</div></div>', unsafe_allow_html=True)

# ================= ADMIN =================
if page == "Admin":

    st.title("🛠 Admin")

    st.subheader("Users")
    st.dataframe(users)

    st.subheader("Add user")
    email = st.text_input("Email")
    name = st.text_input("Name")
    pwd = st.text_input("Password")
    role = st.selectbox("Role", ["user","admin"])

    if st.button("Add user"):
        new = pd.DataFrame([[email,name,pwd,role]], columns=users.columns)
        save_data(pd.concat([users,new]), USERS_FILE)
        st.success("User added")

    st.divider()

    st.subheader("Stats")
    st.write(f"Total bookings: {len(bookings)}")

    csv = bookings.to_csv(index=False).encode("utf-8")
    st.download_button("Download CSV", csv, "bookings.csv")

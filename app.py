import os
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

st.set_page_config(page_title="Pool", layout="wide")

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
for k in ["user","name","role","sel_date"]:
    if k not in st.session_state:
        st.session_state[k] = None

if st.session_state.sel_date is None:
    st.session_state.sel_date = str(datetime.now().date())

# ================= LOGIN =================
if st.session_state.user is None:
    st.title("🎱 Pool Booking")

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

# ================= SIDEBAR =================
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

.block-container {
    max-width: 340px !important;
    margin: auto !important;
    padding-top: 6px !important;
}

/* remove gaps */
div[data-testid="stVerticalBlock"] > div { gap:0 !important; }
.element-container { margin:0 !important; padding:0 !important; }

/* row */
[data-testid="stHorizontalBlock"] {
    display:flex !important;
    flex-wrap:nowrap !important;
    gap:2px !important;
    align-items:center !important;
}

/* columns */
[data-testid="column"] {
    flex:0 0 auto !important;
    width:72px !important;
    min-width:72px !important;
    max-width:72px !important;
}

/* buttons */
.stButton > button {
    width:72px !important;
    height:28px !important;
    font-size:9px !important;
    border-radius:6px !important;
    padding:0 !important;
}

/* dates */
.date button {
    width:48px !important;
    height:32px !important;
    font-size:10px !important;
}

/* selected date */
.sel button {
    background:#4f46e5 !important;
    color:white !important;
}

/* states */
.free button { background:#d1fae5 !important; }
.mine button { background:#bfdbfe !important; }
.taken button { background:#e5e7eb !important; }

/* time */
.time button {
    background:#f3f4f6 !important;
    font-weight:600 !important;
}

/* row color blocks */
.rowA { background:#ffffff; }
.rowB { background:#f8fafc; }

/* header */
.header {
    text-align:center;
    font-size:10px;
    font-weight:700;
}

/* scroll */
.scroll {
    height:70vh;
    overflow-y:auto;
}

</style>
""", unsafe_allow_html=True)

# ================= BOOKING =================
if page == "Booking":

    today = datetime.now().date()

    def fmt(d):
        return f"{d.day}. {d.strftime('%a')}"

    # ===== DATES =====
    r1 = st.columns(7)
    for i in range(7):
        d = today + timedelta(days=i)
        cls = "sel" if str(d)==st.session_state.sel_date else ""
        with r1[i]:
            st.markdown(f'<div class="date {cls}">', unsafe_allow_html=True)
            if st.button(fmt(d), key=f"d1_{i}"):
                st.session_state.sel_date = str(d)
                st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)

    r2 = st.columns(7)
    for i in range(7,14):
        d = today + timedelta(days=i)
        cls = "sel" if str(d)==st.session_state.sel_date else ""
        with r2[i-7]:
            st.markdown(f'<div class="date {cls}">', unsafe_allow_html=True)
            if st.button(fmt(d), key=f"d2_{i}"):
                st.session_state.sel_date = str(d)
                st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)

    st.markdown('<div class="header">Time&nbsp;&nbsp;&nbsp;T1&nbsp;&nbsp;&nbsp;T2&nbsp;&nbsp;&nbsp;T3</div>', unsafe_allow_html=True)

    # ===== TABLE =====
    st.markdown('<div class="scroll">', unsafe_allow_html=True)

    HOURS = [f"{h:02d}:{m}" for h in range(8,24) for m in ["00","30"]]

    for idx, t in enumerate(HOURS):

        block = "rowA" if (idx // 8) % 2 == 0 else "rowB"

        row = st.columns(4)

        # TIME
        with row[0]:
            st.markdown(f'<div class="time {block}">', unsafe_allow_html=True)
            st.button(t, key=f"time_{t}")
            st.markdown("</div>", unsafe_allow_html=True)

        # TABLES
        for i in range(3):
            t_n = f"Table {i+1}"

            match = bookings[
                (bookings["Table"]==t_n)&
                (bookings["Time"]==t)&
                (bookings["Date"]==st.session_state.sel_date)
            ]

            with row[i+1]:
                st.markdown(f'<div class="{block}">', unsafe_allow_html=True)

                if not match.empty:
                    b_user = match.iloc[0]["User"]
                    b_name = match.iloc[0]["Name"]

                    if b_user == st.session_state.user:
                        st.markdown('<div class="mine">', unsafe_allow_html=True)
                        if st.button(f"❌ {b_name[:3]}", key=f"{t}_{i}"):
                            bookings = bookings.drop(match.index)
                            save_data(bookings, BOOKINGS_FILE)
                            st.rerun()
                        st.markdown("</div>", unsafe_allow_html=True)
                    else:
                        st.markdown('<div class="taken">', unsafe_allow_html=True)
                        st.button(b_name[:4], key=f"{t}_{i}", disabled=True)
                        st.markdown("</div>", unsafe_allow_html=True)

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
                    st.markdown("</div>", unsafe_allow_html=True)

                st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

# ================= ADMIN =================
if page == "Admin":

    st.title("🛠 Admin")

    st.subheader("Users")
    st.dataframe(users, use_container_width=True)

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

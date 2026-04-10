import os
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

st.set_page_config(page_title="Pool", layout="wide")

# ================= FILES =================
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
for key in ["user","name","role","sel_date"]:
    if key not in st.session_state:
        st.session_state[key] = None

if st.session_state.sel_date is None:
    st.session_state.sel_date = str(datetime.now().date())

# ================= CSS =================
st.markdown("""
<style>

/* container width */
.block-container {
    max-width: 420px !important;
    margin: auto !important;
    padding-top: 10px !important;
}

/* no stacking */
[data-testid="stHorizontalBlock"] {
    display: flex !important;
    flex-wrap: nowrap !important;
    gap: 4px !important;
}

/* columns fixed width */
[data-testid="column"] {
    flex: 0 0 auto !important;
    width: 85px !important;
    min-width: 85px !important;
    max-width: 85px !important;
}

/* buttons */
.stButton > button {
    width: 85px !important;
    height: 38px !important;
    border-radius: 10px !important;
    font-size: 11px !important;
}

/* DATE BUTTONS */
.date-btn button {
    width: 48px !important;
    height: 38px !important;
    font-size: 12px !important;
    border-radius: 12px !important;
}

/* selected date */
.selected-date button {
    background: linear-gradient(135deg,#4f46e5,#6366f1) !important;
    color: white !important;
    font-weight: bold;
}

/* normal date */
.normal-date button {
    background: #f1f5f9 !important;
}

/* header */
.header {
    text-align:center;
    background:#1f2937;
    color:white;
    padding:6px 0;
    border-radius:10px;
    font-size:12px;
}

/* time */
.time {
    text-align:center;
    font-size:11px;
    font-weight:600;
}

/* states */
.free button {
    background: #dcfce7 !important;
    color: #166534 !important;
}

.mine button {
    background: #dbeafe !important;
    color: #1e40af !important;
}

.taken button {
    background: #f3f4f6 !important;
    color: #6b7280 !important;
}

/* scroll */
.scroll {
    height: 65vh;
    overflow-y: auto;
}

</style>
""", unsafe_allow_html=True)

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

# ================= NAV =================
st.sidebar.write(f"👤 {st.session_state.name}")
page = st.sidebar.radio("Menu", ["Booking","Admin"] if st.session_state.role=="admin" else ["Booking"])

if st.sidebar.button("Logout"):
    st.session_state.clear()
    st.rerun()

# ================= BOOKING =================
if page == "Booking":

    today = datetime.now().date()

    st.write("### 📅 Dates")

    # week 1
    r1 = st.columns(7)
    for i in range(7):
        d = today + timedelta(days=i)
        cls = "selected-date" if str(d)==st.session_state.sel_date else "normal-date"
        with r1[i]:
            st.markdown(f'<div class="date-btn {cls}">', unsafe_allow_html=True)
            if st.button(d.strftime("%d"), key=f"d1_{i}"):
                st.session_state.sel_date = str(d)
                st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)

    # week 2
    r2 = st.columns(7)
    for i in range(7,14):
        d = today + timedelta(days=i)
        cls = "selected-date" if str(d)==st.session_state.sel_date else "normal-date"
        with r2[i-7]:
            st.markdown(f'<div class="date-btn {cls}">', unsafe_allow_html=True)
            if st.button(d.strftime("%d"), key=f"d2_{i}"):
                st.session_state.sel_date = str(d)
                st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)

    st.divider()

    # HEADER
    h = st.columns(4)
    with h[0]: st.write("")
    with h[1]: st.markdown("<div class='header'>T1</div>", unsafe_allow_html=True)
    with h[2]: st.markdown("<div class='header'>T2</div>", unsafe_allow_html=True)
    with h[3]: st.markdown("<div class='header'>T3</div>", unsafe_allow_html=True)

    # TABLE
    st.markdown('<div class="scroll">', unsafe_allow_html=True)

    HOURS = [f"{h:02d}:{m}" for h in range(8,24) for m in ["00","30"]]

    for t in HOURS:
        row = st.columns(4)

        with row[0]:
            st.markdown(f"<div class='time'>{t}</div>", unsafe_allow_html=True)

        for i in range(3):
            t_n = f"Table {i+1}"

            match = bookings[
                (bookings["Table"]==t_n)&
                (bookings["Time"]==t)&
                (bookings["Date"]==st.session_state.sel_date)
            ]

            with row[i+1]:
                if not match.empty:
                    b_user = match.iloc[0]["User"]
                    b_name = match.iloc[0]["Name"]

                    if b_user == st.session_state.user:
                        st.markdown('<div class="mine">', unsafe_allow_html=True)
                        if st.button(f"❌ {b_name[:4]}", key=f"{t}_{i}"):
                            bookings = bookings.drop(match.index)
                            save_data(bookings, BOOKINGS_FILE)
                            st.rerun()
                        st.markdown("</div>", unsafe_allow_html=True)
                    else:
                        st.markdown('<div class="taken">', unsafe_allow_html=True)
                        st.button(b_name[:5], key=f"{t}_{i}", disabled=True)
                        st.markdown("</div>", unsafe_allow_html=True)
                else:
                    st.markdown('<div class="free">', unsafe_allow_html=True)
                    if st.button("Free", key=f"{t}_{i}"):
                        new_b = pd.DataFrame([{
                            "User": st.session_state.user,
                            "Name": st.session_state.name,
                            "Date": st.session_state.sel_date,
                            "Table": t_n,
                            "Time": t
                        }])
                        save_data(pd.concat([bookings,new_b]), BOOKINGS_FILE)
                        st.rerun()
                    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

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

    if st.button("Add"):
        new = pd.DataFrame([[email,name,pwd,role]], columns=users.columns)
        save_data(pd.concat([users,new]), USERS_FILE)
        st.success("User added")

    st.divider()

    st.subheader("Stats")
    st.write(f"Total bookings: {len(bookings)}")

    csv = bookings.to_csv(index=False).encode("utf-8")
    st.download_button("Download CSV", csv, "bookings.csv")

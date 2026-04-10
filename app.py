import os
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

# 1. SETUP
st.set_page_config(page_title="Pool", layout="wide", initial_sidebar_state="collapsed")

# 2. DATA
USERS_FILE = "users.csv"
BOOKINGS_FILE = "bookings.csv"

def load_data(file, columns):
    if os.path.exists(file):
        return pd.read_csv(file, dtype=str)
    return pd.DataFrame(columns=columns)

def save_data(df, file):
    df.to_csv(file, index=False)

users = load_data(USERS_FILE, ["Email", "Name", "Password", "Role"])
bookings = load_data(BOOKINGS_FILE, ["User", "Name", "Date", "Table", "Time"])

# 3. SESSION STATE
if "user" not in st.session_state: st.session_state.user = None
if "name" not in st.session_state: st.session_state.name = None
if "role" not in st.session_state: st.session_state.role = None
if "sel_date" not in st.session_state: st.session_state.sel_date = str(datetime.now().date())
if "confirm_delete" not in st.session_state: st.session_state.confirm_delete = None

# 4. CSS (FINAL MOBILE GRID FIX)
st.markdown("""
<style>

/* prevent stacking */
[data-testid="stHorizontalBlock"] {
    display: flex !important;
    flex-wrap: nowrap !important;
    gap: 4px !important;
    align-items: center !important;
}

/* remove spacing */
[data-testid="column"] {
    padding: 0 !important;
    margin: 0 !important;
    min-width: 0 !important;
}

/* buttons */
.stButton > button {
    width: 100% !important;
    height: 34px !important;
    padding: 0 !important;
    font-size: 12px !important;
    border-radius: 6px !important;
    font-weight: 600 !important;
}

/* free */
button[kind="secondary"] {
    background-color: #e6ffed !important;
    color: #1a7f37 !important;
    border: 1px solid #4AC26B !important;
}

/* booked */
button[kind="primary"], .table-row button:disabled {
    background-color: #ffebe9 !important;
    color: #cf222e !important;
    border: 1px solid #FF8182 !important;
    opacity: 1 !important;
}

/* time column */
.time-label {
    width: 55px !important;
    min-width: 55px !important;
    text-align: center;
    font-size: 12px;
    font-weight: bold;
}

/* headers */
.header-box {
    width: 70px;
    height: 34px;
    line-height: 34px;
    background: black;
    color: white;
    text-align: center;
    border-radius: 6px;
    font-size: 12px;
    font-weight: bold;
}

/* scroll area */
.scroll-table {
    height: 65vh;
    overflow-y: auto;
    overflow-x: hidden;
}

</style>
""", unsafe_allow_html=True)

# 5. LOGIN
if st.session_state.user is None:
    st.title("🎱 RESERVE")
    e = st.text_input("Email").lower().strip()
    p = st.text_input("Password", type="password")
    if st.button("Login"):
        match = users[(users["Email"] == e) & (users["Password"] == p)]
        if not match.empty:
            st.session_state.user = e
            st.session_state.name = match.iloc[0]["Name"]
            st.session_state.role = match.iloc[0]["Role"]
            st.rerun()
    st.stop()

# SIDEBAR
st.sidebar.title("🎱 Pool App")
st.sidebar.markdown(f"**Logged in:** {st.session_state.name} ({st.session_state.role})")

PAGES = {"Pool Booking": "user"}
if st.session_state.role == "admin":
    PAGES["Administration"] = "admin"

selected_page = st.sidebar.radio("Navigation", list(PAGES.keys()))

if st.sidebar.button("Logout"):
    st.session_state.clear()
    st.rerun()

# =========================
# MAIN PAGE
# =========================
if selected_page == "Pool Booking":

    st.write("### 📅 Dates")
    today = datetime.now().date()

    # WEEK 1
    cols1 = st.columns(7)
    for i in range(7):
        d = today + timedelta(days=i)
        d_str = str(d)
        with cols1[i]:
            if st.button(f"{d.strftime('%a')}\n{d.day}", key=f"d1_{d_str}",
                         type="primary" if st.session_state.sel_date == d_str else "secondary"):
                st.session_state.sel_date = d_str
                st.rerun()

    # WEEK 2
    cols2 = st.columns(7)
    for i in range(7, 14):
        d = today + timedelta(days=i)
        d_str = str(d)
        with cols2[i-7]:
            if st.button(f"{d.strftime('%a')}\n{d.day}", key=f"d2_{d_str}",
                         type="primary" if st.session_state.sel_date == d_str else "secondary"):
                st.session_state.sel_date = d_str
                st.rerun()

    st.divider()

    # HEADERS
    h_cols = st.columns([1,1,1,1])
    with h_cols[0]: st.write("")
    with h_cols[1]: st.markdown('<div class="header-box">T1</div>', unsafe_allow_html=True)
    with h_cols[2]: st.markdown('<div class="header-box">T2</div>', unsafe_allow_html=True)
    with h_cols[3]: st.markdown('<div class="header-box">T3</div>', unsafe_allow_html=True)

    # TABLE
    st.markdown('<div class="scroll-table">', unsafe_allow_html=True)

    HOURS = [f"{h:02d}:{m}" for h in (list(range(8, 24)) + list(range(0, 3))) for m in ["00", "30"]]

    for t in HOURS:
        r_cols = st.columns([1,1,1,1])

        with r_cols[0]:
            st.markdown(f'<div class="time-label">{t}</div>', unsafe_allow_html=True)

        for i in range(3):
            t_n = f"Table {i+1}"
            match = bookings[
                (bookings["Table"] == t_n) &
                (bookings["Time"] == t) &
                (bookings["Date"] == st.session_state.sel_date)
            ]

            with r_cols[i+1]:
                if not match.empty:
                    b_user, b_name = match.iloc[0]["User"], match.iloc[0]["Name"]

                    if st.session_state.user == b_user:
                        if st.button(f"❌ {b_name[:6]}", key=f"b_{t}_{i}", type="primary"):
                            bookings = bookings.drop(match.index)
                            save_data(bookings, BOOKINGS_FILE)
                            st.rerun()

                    elif st.session_state.role == "admin":
                        if st.button(f"🛡️ {b_name[:6]}", key=f"b_{t}_{i}", type="primary"):
                            st.session_state.confirm_delete = (match.index[0], b_name)
                            st.rerun()

                    else:
                        st.button(f"🔒 {b_name[:6]}", key=f"b_{t}_{i}", disabled=True)

                else:
                    if st.button("Free", key=f"b_{t}_{i}", type="secondary"):
                        new_b = pd.DataFrame([{
                            "User": st.session_state.user,
                            "Name": st.session_state.name,
                            "Date": st.session_state.sel_date,
                            "Table": t_n,
                            "Time": t
                        }])
                        save_data(pd.concat([bookings, new_b]), BOOKINGS_FILE)
                        st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)

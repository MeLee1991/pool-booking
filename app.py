import os
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

# =====================================
# SETUP
# =====================================
st.set_page_config(page_title="Pool", layout="centered")

USERS_FILE = "users.csv"
BOOKINGS_FILE = "bookings.csv"

def load_data(file, cols):
    if os.path.exists(file):
        return pd.read_csv(file, dtype=str)
    return pd.DataFrame(columns=cols)

def save_data(df, file):
    df.to_csv(file, index=False)

users = load_data(USERS_FILE, ["Email", "Name", "Password", "Role"])
bookings = load_data(BOOKINGS_FILE, ["User", "Name", "Date", "Table", "Time"])

# =====================================
# SESSION
# =====================================
if "user" not in st.session_state: st.session_state.user = None
if "name" not in st.session_state: st.session_state.name = None
if "role" not in st.session_state: st.session_state.role = None
if "sel_date" not in st.session_state: st.session_state.sel_date = str(datetime.now().date())

# =====================================
# CSS (LOCKED GRID)
# =====================================
st.markdown("""
<style>

/* kill horizontal scroll */
html, body, [data-testid="stAppViewContainer"] {
    overflow-x: hidden !important;
}

/* columns equal width */
[data-testid="column"] {
    flex: 1 1 0 !important;
    min-width: 0 !important;
}

/* spacing */
[data-testid="stHorizontalBlock"] {
    gap: 6px !important;
}

/* buttons */
.stButton > button {
    width: 100% !important;
    height: 40px !important;
    font-size: 11px !important;
    border-radius: 8px !important;
    padding: 0 !important;
}

/* free */
button[kind="secondary"] {
    background-color: #e6ffed !important;
    color: #1a7f37 !important;
    border: 1px solid #4AC26B !important;
}

/* booked others */
button[kind="primary"] {
    background-color: #ffebe9 !important;
    color: #cf222e !important;
    border: 1px solid #FF8182 !important;
}

/* YOUR bookings */
button.my-booking {
    background-color: #e7f3ff !important;
    color: #0969da !important;
    border: 1px solid #58a6ff !important;
}

/* time */
.time {
    text-align: center;
    font-size: 12px;
    font-weight: bold;
}

/* header */
.header {
    text-align: center;
    background: black;
    color: white;
    border-radius: 8px;
    padding: 8px 0;
    font-size: 12px;
}

/* sticky header */
.header-row {
    position: sticky;
    top: 0;
    background: white;
    z-index: 10;
}

/* scroll */
.scroll {
    height: 70vh;
    overflow-y: auto;
}

/* date nav */
.date-nav button {
    width: 100% !important;
}

</style>
""", unsafe_allow_html=True)

# =====================================
# LOGIN
# =====================================
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

# =====================================
# DATE NAV
# =====================================
d = datetime.fromisoformat(st.session_state.sel_date)

c1, c2, c3 = st.columns([1,2,1])

with c1:
    if st.button("◀"):
        st.session_state.sel_date = str(d - timedelta(days=1))
        st.rerun()

with c2:
    st.markdown(f"### {d.strftime('%A %d %B')}")

with c3:
    if st.button("▶"):
        st.session_state.sel_date = str(d + timedelta(days=1))
        st.rerun()

st.divider()

# =====================================
# HEADER
# =====================================
h = st.columns([1,1,1,1])

with h[0]: st.markdown("<div class='time'></div>", unsafe_allow_html=True)
with h[1]: st.markdown("<div class='header'>T1</div>", unsafe_allow_html=True)
with h[2]: st.markdown("<div class='header'>T2</div>", unsafe_allow_html=True)
with h[3]: st.markdown("<div class='header'>T3</div>", unsafe_allow_html=True)

# =====================================
# TABLE
# =====================================
st.markdown('<div class="scroll">', unsafe_allow_html=True)

HOURS = [f"{h:02d}:{m}" for h in (list(range(8, 24)) + list(range(0, 3))) for m in ["00", "30"]]

for t in HOURS:
    row = st.columns([1,1,1,1])

    # time
    with row[0]:
        st.markdown(f"<div class='time'>{t}</div>", unsafe_allow_html=True)

    # check if user already booked this time
    user_has_booking = not bookings[
        (bookings["User"] == st.session_state.user) &
        (bookings["Time"] == t) &
        (bookings["Date"] == st.session_state.sel_date)
    ].empty

    for i in range(3):
        t_n = f"Table {i+1}"

        match = bookings[
            (bookings["Table"] == t_n) &
            (bookings["Time"] == t) &
            (bookings["Date"] == st.session_state.sel_date)
        ]

        with row[i+1]:
            if not match.empty:
                b_user = match.iloc[0]["User"]
                b_name = match.iloc[0]["Name"]

                if b_user == st.session_state.user:
                    if st.button(f"❌ {b_name[:5]}", key=f"{t}_{i}"):
                        bookings = bookings.drop(match.index)
                        save_data(bookings, BOOKINGS_FILE)
                        st.rerun()

                elif st.session_state.role == "admin":
                    if st.button(f"🛡️ {b_name[:5]}", key=f"{t}_{i}", type="primary"):
                        bookings = bookings.drop(match.index)
                        save_data(bookings, BOOKINGS_FILE)
                        st.rerun()

                else:
                    st.button(f"🔒 {b_name[:5]}", key=f"{t}_{i}", disabled=True)

            else:
                if user_has_booking:
                    st.button("Taken", key=f"{t}_{i}", disabled=True)
                else:
                    if st.button("Free", key=f"{t}_{i}", type="secondary"):
                        new_b = pd.DataFrame([{
                            "User": st.session_state.user,
                            "Name": st.session_state.name,
                            "Date": st.session_state.sel_date,
                            "Table": t_n,
                            "Time": t
                        }])
                        save_data(pd.concat([bookings, new_b]), BOOKINGS_FILE)
                        st.rerun()

st.markdown("</div>", unsafe_allow_html=True)

import os
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

# =====================================
# 1. SETUP
# =====================================
st.set_page_config(page_title="Pool", layout="centered")

# =====================================
# 2. DATA
# =====================================
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

# =====================================
# 3. SESSION
# =====================================
if "user" not in st.session_state: st.session_state.user = None
if "name" not in st.session_state: st.session_state.name = None
if "role" not in st.session_state: st.session_state.role = None
if "sel_date" not in st.session_state: st.session_state.sel_date = str(datetime.now().date())

# =====================================
# 4. CSS (HARD LOCKED GRID)
# =====================================
st.markdown("""
<style>

/* kill horizontal scroll */
html, body, [data-testid="stAppViewContainer"] {
    overflow-x: hidden !important;
}

/* tighter app padding */
[data-testid="stAppViewBlockContainer"] {
    padding: 0.5rem !important;
}

/* row layout */
.row {
    display: flex;
    align-items: center;
    gap: 6px;
    margin-bottom: 6px;
}

/* time column */
.time {
    width: 70px;
    min-width: 70px;
    text-align: center;
    font-size: 12px;
    font-weight: bold;
}

/* slot */
.slot {
    width: 72px;
}

/* buttons */
.stButton > button {
    width: 72px !important;
    height: 38px !important;
    padding: 0 !important;
    font-size: 11px !important;
    border-radius: 8px !important;
}

/* free */
button[kind="secondary"] {
    background-color: #e6ffed !important;
    color: #1a7f37 !important;
    border: 1px solid #4AC26B !important;
}

/* booked */
button[kind="primary"], .stButton button:disabled {
    background-color: #ffebe9 !important;
    color: #cf222e !important;
    border: 1px solid #FF8182 !important;
    opacity: 1 !important;
}

/* header sticky */
.header-row {
    position: sticky;
    top: 0;
    background: white;
    z-index: 10;
    padding-bottom: 5px;
}

/* header cells */
.header {
    width: 72px;
    height: 38px;
    line-height: 38px;
    text-align: center;
    background: black;
    color: white;
    border-radius: 8px;
    font-size: 12px;
    font-weight: bold;
}

/* scroll area */
.scroll {
    height: 70vh;
    overflow-y: auto;
    overflow-x: hidden;
}

/* date nav */
.date-nav {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 10px;
}

.date-nav button {
    width: auto !important;
    padding: 6px 10px !important;
    font-size: 12px !important;
}

.date-title {
    font-weight: bold;
    font-size: 14px;
}

</style>
""", unsafe_allow_html=True)

# =====================================
# 5. LOGIN
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
# 6. DATE NAV (UX UPGRADE)
# =====================================
sel_date = datetime.fromisoformat(st.session_state.sel_date)

c1, c2, c3 = st.columns([1,2,1])

with c1:
    if st.button("◀"):
        st.session_state.sel_date = str(sel_date - timedelta(days=1))
        st.rerun()

with c2:
    st.markdown(
        f"<div class='date-title'>{sel_date.strftime('%A, %d %B')}</div>",
        unsafe_allow_html=True
    )

with c3:
    if st.button("▶"):
        st.session_state.sel_date = str(sel_date + timedelta(days=1))
        st.rerun()

st.divider()

# =====================================
# 7. HEADER
# =====================================
st.markdown("""
<div class="row header-row">
    <div class="time"></div>
    <div class="header">T1</div>
    <div class="header">T2</div>
    <div class="header">T3</div>
</div>
""", unsafe_allow_html=True)

# =====================================
# 8. TABLE
# =====================================
st.markdown('<div class="scroll">', unsafe_allow_html=True)

HOURS = [f"{h:02d}:{m}" for h in (list(range(8, 24)) + list(range(0, 3))) for m in ["00", "30"]]

for t in HOURS:
    cols = st.columns([1,1,1,1])

    # TIME
    with cols[0]:
        st.markdown(f"<div class='time'>{t}</div>", unsafe_allow_html=True)

    # TABLES
    for i in range(3):
        t_n = f"Table {i+1}"

        match = bookings[
            (bookings["Table"] == t_n) &
            (bookings["Time"] == t) &
            (bookings["Date"] == st.session_state.sel_date)
        ]

        with cols[i+1]:
            if not match.empty:
                b_user = match.iloc[0]["User"]
                b_name = match.iloc[0]["Name"]

                if st.session_state.user == b_user:
                    if st.button(f"❌ {b_name[:5]}", key=f"{t}_{i}", type="primary"):
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

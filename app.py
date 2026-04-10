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
# CSS (FINAL HARD LOCK)
# =====================================
st.markdown("""
<style>

/* ===== GLOBAL ===== */
html, body {
    overflow-x: hidden !important;
    background: #f6f7fb;
}

/* center max width (fix landscape too wide) */
.block-container {
    max-width: 420px;
    padding: 10px !important;
    margin: auto;
}

/* ===== GRID ===== */
[data-testid="stHorizontalBlock"] {
    display: flex !important;
    flex-wrap: nowrap !important;
    gap: 6px !important;
}

/* equal columns */
[data-testid="column"] {
    flex: 1 1 0 !important;
    min-width: 0 !important;
}

/* ===== BUTTONS (ALL SAME SIZE) ===== */
.stButton > button {
    width: 80px !important;
    min-width: 80px !important;
    max-width: 80px !important;
    height: 42px !important;
    border-radius: 10px !important;
    font-size: 11px !important;
    padding: 0 !important;
    border: none !important;
    box-shadow: 0 2px 6px rgba(0,0,0,0.08);
}

/* login button SAME SIZE */
button[kind="primary"] {
    background: linear-gradient(135deg, #4f8cff, #6aa8ff) !important;
    color: white !important;
}

/* free */
button[kind="secondary"] {
    background: #e9fbe9 !important;
    color: #1a7f37 !important;
}

/* disabled */
button:disabled {
    background: #f1f1f1 !important;
    color: #888 !important;
}

/* your booking */
button.my {
    background: #e7f0ff !important;
    color: #1d4ed8 !important;
}

/* ===== HEADER ===== */
.header {
    width: 80px;
    height: 42px;
    border-radius: 10px;
    text-align: center;
    line-height: 42px;
    background: linear-gradient(135deg, #2c2f36, #3a3f47);
    color: white;
    font-size: 12px;
}

/* ===== TIME ===== */
.time {
    width: 60px;
    text-align: center;
    font-size: 11px;
    font-weight: 600;
    color: #444;
}

/* ===== SCROLL ===== */
.scroll {
    height: 70vh;
    overflow-y: auto;
}

/* ===== DATE NAV ===== */
.date-nav button {
    width: 80px !important;
}

.date-title {
    text-align: center;
    font-weight: 600;
    font-size: 14px;
    padding-top: 8px;
}

</style>
""", unsafe_allow_html=True)

# =====================================
# LOGIN
# =====================================
if st.session_state.user is None:
    st.title("🎱 Pool Booking")

    e = st.text_input("Email")
    p = st.text_input("Password", type="password")

    col1, col2, col3 = st.columns([1,1,1])
    with col2:
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
    st.markdown(f"<div class='date-title'>{d.strftime('%A %d %b')}</div>", unsafe_allow_html=True)

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

    with row[0]:
        st.markdown(f"<div class='time'>{t}</div>", unsafe_allow_html=True)

    user_has = not bookings[
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
                    st.markdown('<style>div[data-testid="stButton"] button {background:#e7f0ff !important;}</style>', unsafe_allow_html=True)
                    if st.button(f"❌ {b_name[:5]}", key=f"{t}_{i}"):
                        bookings = bookings.drop(match.index)
                        save_data(bookings, BOOKINGS_FILE)
                        st.rerun()

                else:
                    st.button(f"{b_name[:5]}", key=f"{t}_{i}", disabled=True)

            else:
                if user_has:
                    st.button("—", key=f"{t}_{i}", disabled=True)
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

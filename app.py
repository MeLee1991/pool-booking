import os
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

st.set_page_config(page_title="Pool", layout="wide")

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
    st.title("🎱 Pool")

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

# ================= CSS =================
st.markdown("""
<style>

/* ===== WIDTH ===== */
.block-container {
    max-width: 320px !important;
    margin: auto !important;
}

/* ===== NO STACKING ===== */
[data-testid="stHorizontalBlock"] {
    display: flex !important;
    flex-wrap: nowrap !important;
    gap: 2px !important;
}

/* ===== FIXED COLUMN WIDTH ===== */
[data-testid="column"] {
    flex: 0 0 auto !important;
    width: 68px !important;
    min-width: 68px !important;
    max-width: 68px !important;
    padding: 0 !important;
}

/* ===== BUTTON GRID ===== */
.stButton > button {
    width: 68px !important;
    height: 36px !important;
    font-size: 10px !important;
    border-radius: 8px !important;
    padding: 0 !important;
}

/* ===== DATE BUTTONS ===== */
.date button {
    width: 44px !important;
    height: 36px !important;
    font-size: 11px !important;
}

/* selected */
.sel button {
    background:#4f46e5 !important;
    color:white !important;
}

/* ===== STATES ===== */
.free button { background:#dcfce7 !important; }
.mine button { background:#dbeafe !important; }
.taken button { background:#f3f4f6 !important; }

/* ===== TIME ===== */
.time button {
    background:#e5e7eb !important;
    font-weight:600;
}

/* ===== 4H BLOCK COLORS ===== */
.blockA button { background:#f9fafb !important; }
.blockB button { background:#eef2ff !important; }

/* ===== SCROLL ===== */
.scroll {
    height:65vh;
    overflow-y:auto;
}

</style>
""", unsafe_allow_html=True)

# ================= DATES =================
today = datetime.now().date()

r1 = st.columns(7)
for i in range(7):
    d = today + timedelta(days=i)
    cls = "sel" if str(d)==st.session_state.sel_date else ""
    with r1[i]:
        st.markdown(f'<div class="date {cls}">', unsafe_allow_html=True)
        if st.button(d.strftime("%d"), key=f"d1_{i}"):
            st.session_state.sel_date = str(d)
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

r2 = st.columns(7)
for i in range(7,14):
    d = today + timedelta(days=i)
    cls = "sel" if str(d)==st.session_state.sel_date else ""
    with r2[i-7]:
        st.markdown(f'<div class="date {cls}">', unsafe_allow_html=True)
        if st.button(d.strftime("%d"), key=f"d2_{i}"):
            st.session_state.sel_date = str(d)
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

st.divider()

# ================= TABLE =================
st.markdown('<div class="scroll">', unsafe_allow_html=True)

HOURS = [f"{h:02d}:{m}" for h in range(8,24) for m in ["00","30"]]

for idx, t in enumerate(HOURS):

    # determine 4h block
    block_class = "blockA" if (idx // 8) % 2 == 0 else "blockB"

    row = st.columns(4)

    # TIME BUTTON (same alignment)
    with row[0]:
        st.markdown(f'<div class="time {block_class}">', unsafe_allow_html=True)
        st.button(t, key=f"time_{t}")
        st.markdown("</div>", unsafe_allow_html=True)

    for i in range(3):
        t_n = f"Table {i+1}"

        match = bookings[
            (bookings["Table"]==t_n)&
            (bookings["Time"]==t)&
            (bookings["Date"]==st.session_state.sel_date)
        ]

        with row[i+1]:
            st.markdown(f'<div class="{block_class}">', unsafe_allow_html=True)

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

st.markdown("</div>", unsafe_allow_html=True)

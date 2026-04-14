import streamlit as st
from datetime import datetime, timedelta

st.set_page_config(layout="wide")

# -----------------------
# STATE
# -----------------------
if "date" not in st.session_state:
    st.session_state.date = datetime.today().date()

if "bookings" not in st.session_state:
    st.session_state.bookings = {}

if "user" not in st.session_state:
    st.session_state.user = None

# -----------------------
# CONFIG
# -----------------------
SLOTS = ["T1", "T2", "T3"]
TIMES = [f"{h:02d}:{m:02d}" for h in range(6, 12) for m in (0, 30)]
DATES = [datetime.today().date() + timedelta(days=i) for i in range(7)]

# -----------------------
# HELPERS
# -----------------------
def key(d, t, s):
    return f"{d}_{t}_{s}"

def toggle(d, t, s):
    k = key(d, t, s)
    if k in st.session_state.bookings:
        del st.session_state.bookings[k]
    else:
        st.session_state.bookings[k] = st.session_state.user or "Anon"

# -----------------------
# LOGIN
# -----------------------
if not st.session_state.user:
    st.title("Login")

    name = st.text_input("Your name")
    if st.button("Enter"):
        st.session_state.user = name if name else "Anon"
        st.rerun()

    st.stop()

# -----------------------
# HEADER
# -----------------------
st.markdown(f"### 👤 {st.session_state.user} | {st.session_state.date}")

colA, colB, colC = st.columns(3)
with colA:
    if st.button("Admin"):
        st.session_state.admin = True
with colB:
    if st.button("Logout"):
        st.session_state.user = None
        st.rerun()

# -----------------------
# DATES (GRID FIXED)
# -----------------------
st.markdown("""
<style>
div[data-testid="column"] {
    padding: 2px !important;
}
.stButton button {
    width: 100%;
    height: 44px;
    border-radius: 12px;
    font-size: 10px;
}
</style>
""", unsafe_allow_html=True)

for i in range(0, len(DATES), 4):
    row = DATES[i:i+4]
    cols = st.columns(4)

    for j, d in enumerate(row):
        label = d.strftime("%a %d")

        if cols[j].button(label, key=f"date_{d}"):
            st.session_state.date = d
            st.rerun()

# -----------------------
# TABLE HEADER
# -----------------------
cols = st.columns([1,1,1,1])
cols[0].markdown("**Time**")
cols[1].markdown("**T1**")
cols[2].markdown("**T2**")
cols[3].markdown("**T3**")

# -----------------------
# TABLE BODY
# -----------------------
for t in TIMES:
    cols = st.columns([1,1,1,1])

    cols[0].markdown(
        f"<div style='background:#e5e7eb;border-radius:12px;padding:10px;text-align:center;font-size:10px'>{t}</div>",
        unsafe_allow_html=True
    )

    for i, s in enumerate(SLOTS):
        k = key(st.session_state.date, t, s)

        if k in st.session_state.bookings:
            label = f"✖ {st.session_state.bookings[k][:6]}"
            color = "#fecaca"
        else:
            label = "+"
            color = "#bbf7d0"

        if cols[i+1].button(label, key=f"{t}_{s}"):
            toggle(st.session_state.date, t, s)
            st.rerun()

        cols[i+1].markdown(f"""
        <style>
        div[data-testid="stButton"][key="{t}_{s}"] button {{
            background: {color};
        }}
        </style>
        """, unsafe_allow_html=True)

# -----------------------
# ADMIN PANEL
# -----------------------
if st.session_state.get("admin"):
    st.markdown("---")
    st.subheader("Admin panel")

    st.write(st.session_state.bookings)

    if st.button("Clear all"):
        st.session_state.bookings = {}
        st.rerun()

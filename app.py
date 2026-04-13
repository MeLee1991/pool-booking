import streamlit as st
from datetime import datetime, timedelta

st.set_page_config(layout="wide")

# -----------------------
# CONFIG
# -----------------------
SLOTS = ["T1", "T2", "T3"]
TIMES = [f"{h:02d}:{m:02d}" for h in range(6, 22) for m in (0, 30)]
USER = "Tom"

# -----------------------
# SESSION STATE
# -----------------------
if "bookings" not in st.session_state:
    st.session_state.bookings = {}

if "selected_date" not in st.session_state:
    st.session_state.selected_date = datetime.today().date()

# -----------------------
# HELPERS
# -----------------------
def key(date, time, slot):
    return f"{date}_{time}_{slot}"

def toggle(date, time, slot):
    k = key(date, time, slot)
    if k in st.session_state.bookings:
        del st.session_state.bookings[k]
    else:
        st.session_state.bookings[k] = USER

# -----------------------
# STYLE (FIXED UI)
# -----------------------
st.markdown("""
<style>
div.stButton > button {
    width: 100%;
    height: 42px;
    border-radius: 12px;
    font-size: 10px;
    font-weight: 600;
    padding: 0;
}
</style>
""", unsafe_allow_html=True)

# -----------------------
# DATE SELECTOR (WORKING)
# -----------------------
st.markdown("### Select Date")

days = [datetime.today().date() + timedelta(days=i) for i in range(7)]
cols = st.columns(4)

for i, d in enumerate(days):
    col = cols[i % 4]
    label = d.strftime("%a %d")

    if col.button(label, use_container_width=True):
        st.session_state.selected_date = d

st.divider()

# -----------------------
# TABLE HEADER
# -----------------------
header = st.columns([1,1,1,1])
header[0].markdown("**Time**")
header[1].markdown("**T1**")
header[2].markdown("**T2**")
header[3].markdown("**T3**")

# -----------------------
# MAIN GRID (WORKING)
# -----------------------
for t in TIMES:
    row = st.columns([1,1,1,1])

    row[0].markdown(f"**{t}**")

    for i, slot in enumerate(SLOTS):
        k = key(st.session_state.selected_date, t, slot)

        if k in st.session_state.bookings:
            label = f"❌ {st.session_state.bookings[k]}"
            color = "red"
        else:
            label = "+"
            color = "green"

        if row[i+1].button(label, key=k, use_container_width=True):
            toggle(st.session_state.selected_date, t, slot)
            st.rerun()

        # COLOR FIX (after render)
        if k in st.session_state.bookings:
            row[i+1].markdown(
                f"<style>button[data-testid='baseButton'][key='{k}'] {{background-color:#f8caca;}}</style>",
                unsafe_allow_html=True
            )
        else:
            row[i+1].markdown(
                f"<style>button[data-testid='baseButton'][key='{k}'] {{background-color:#c8f7d1;}}</style>",
                unsafe_allow_html=True
        )

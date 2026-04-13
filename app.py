import streamlit as st
from datetime import datetime, timedelta

st.set_page_config(layout="wide")

# -----------------------
# DATA
# -----------------------
SLOTS = ["T1", "T2", "T3"]
TIMES = [f"{h:02d}:{m:02d}" for h in range(6, 22) for m in (0, 30)]

if "bookings" not in st.session_state:
    st.session_state.bookings = {}

if "date" not in st.session_state:
    st.session_state.date = datetime.today().date()

if "page" not in st.session_state:
    st.session_state.page = "main"

USER = "Tom"

# -----------------------
# HANDLE ACTIONS
# -----------------------
q = st.query_params

if "add" in q:
    t, s = q["add"].split("_")
    st.session_state.bookings[(str(st.session_state.date), t, s)] = USER
    st.query_params.clear()
    st.rerun()

if "remove" in q:
    t, s = q["remove"].split("_")
    st.session_state.bookings.pop((str(st.session_state.date), t, s), None)
    st.query_params.clear()
    st.rerun()

if "page" in q:
    st.session_state.page = q["page"]

# -----------------------
# STYLE (FIXED GRID)
# -----------------------
st.markdown("""
<style>
.container {
    overflow-x: auto;
}

.grid {
    display: grid;
    grid-template-columns: 70px 1fr 1fr 1fr;
    gap: 6px;
    min-width: 420px;
}

.cell {
    height: 44px;
    border-radius: 12px;
    font-size: 10px;
    display:flex;
    align-items:center;
    justify-content:center;
}

.time { background:#e5e7eb; }

.free {
    background:#bbf7d0;
}

.taken {
    background:#fecaca;
}
.date-btn {
    display:inline-block;
    padding:10px;
    margin:4px;
    border-radius:10px;
    background:#eee;
    text-align:center;
    font-size:12px;
}
.selected {
    background:#6366f1;
    color:white;
}
</style>
""", unsafe_allow_html=True)

# -----------------------
# SIDEBAR (ADMIN)
# -----------------------
with st.sidebar:
    st.title("Menu")

    if st.button("Schedule"):
        st.query_params["page"] = "main"

    if st.button("Admin"):
        st.query_params["page"] = "admin"

# -----------------------
# ADMIN PAGE
# -----------------------
if st.session_state.page == "admin":
    st.title("Admin")

    for k, v in list(st.session_state.bookings.items()):
        st.write(k, "→", v)
        if st.button("Delete", key=str(k)):
            del st.session_state.bookings[k]
            st.rerun()

    st.stop()

# -----------------------
# DATE SELECTOR
# -----------------------
st.markdown("### Dates")

for i in range(7):
    d = datetime.today().date() + timedelta(days=i)
    cls = "date-btn"
    if d == st.session_state.date:
        cls += " selected"

    st.markdown(f"""
    <a href="?date={d}" class="{cls}">
    {d.strftime('%a %d')}
    </a>
    """, unsafe_allow_html=True)

if "date" in q:
    st.session_state.date = datetime.fromisoformat(q["date"]).date()

# -----------------------
# TABLE
# -----------------------
st.markdown('<div class="container"><div class="grid">', unsafe_allow_html=True)

# header
st.markdown('<div class="cell time">Time</div>', unsafe_allow_html=True)
for s in SLOTS:
    st.markdown(f'<div class="cell time">{s}</div>', unsafe_allow_html=True)

# rows
for t in TIMES:
    st.markdown(f'<div class="cell time">{t}</div>', unsafe_allow_html=True)

    for s in SLOTS:
        key = (str(st.session_state.date), t, s)

        if key in st.session_state.bookings:
            name = st.session_state.bookings[key][:10]
            st.markdown(f"""
            <a href="?remove={t}_{s}">
                <div class="cell taken">✖ {name}</div>
            </a>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <a href="?add={t}_{s}">
                <div class="cell free">+</div>
            </a>
            """, unsafe_allow_html=True)

st.markdown('</div></div>', unsafe_allow_html=True)

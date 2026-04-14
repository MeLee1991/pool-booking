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
# STATE
# -----------------------
if "bookings" not in st.session_state:
    st.session_state.bookings = {}

if "date" not in st.session_state:
    st.session_state.date = datetime.today().date()

if "page" not in st.session_state:
    st.session_state.page = "main"

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
        st.session_state.bookings[k] = USER

# -----------------------
# SIDEBAR
# -----------------------
with st.sidebar:
    st.title("Menu")
    if st.button("Schedule"):
        st.session_state.page = "main"
    if st.button("Admin"):
        st.session_state.page = "admin"

# -----------------------
# ADMIN PAGE
# -----------------------
if st.session_state.page == "admin":
    st.title("Admin")

    if not st.session_state.bookings:
        st.info("No bookings")
    else:
        for k, v in list(st.session_state.bookings.items()):
            st.write(k, "→", v)
            if st.button("Delete", key=k):
                del st.session_state.bookings[k]
                st.rerun()

    st.stop()

# -----------------------
# STYLE (FORCE GRID)
# -----------------------
st.markdown("""
<style>
/* horizontal scroll so mobile never stacks */
.scroll {
    overflow-x: auto;
}

/* fixed width table */
.table {
    min-width: 520px;
}

/* row layout */
.row {
    display: flex;
    gap: 6px;
    margin-bottom: 6px;
}

/* cells */
.cell {
    height: 44px;
    border-radius: 12px;
    font-size: 10px;
    display:flex;
    align-items:center;
    justify-content:center;
}

/* fixed widths */
.time {
    width: 70px;
    background:#e5e7eb;
    flex-shrink:0;
}

.slot {
    width: 110px;
    flex-shrink:0;
}

/* colors */
.free { background:#bbf7d0; }
.taken { background:#fecaca; }

/* DATE ROW */
.date-row {
    display:flex;
    gap:6px;
    overflow-x:auto;
    margin-bottom:10px;
}

.date-btn button {
    height:40px;
    border-radius:10px;
    font-size:11px;
}
</style>
""", unsafe_allow_html=True)

# -----------------------
# DATE SELECTOR (FIXED)
# -----------------------
st.markdown('<div class="date-row">', unsafe_allow_html=True)

date_cols = st.columns(7)

for i in range(7):
    d = datetime.today().date() + timedelta(days=i)

    if date_cols[i].button(d.strftime("%a %d"), key=f"d{i}"):
        st.session_state.date = d
        st.rerun()

st.markdown('</div>', unsafe_allow_html=True)

# -----------------------
# TABLE (VISUAL GRID)
# -----------------------
st.markdown('<div class="scroll"><div class="table">', unsafe_allow_html=True)

# header
st.markdown("""
<div class="row">
<div class="cell time">Time</div>
<div class="cell slot">T1</div>
<div class="cell slot">T2</div>
<div class="cell slot">T3</div>
</div>
""", unsafe_allow_html=True)

# rows
for t in TIMES:
    row_html = f'<div class="row">'
    row_html += f'<div class="cell time">{t}</div>'

    for s in SLOTS:
        k = key(st.session_state.date, t, s)

        if k in st.session_state.bookings:
            name = st.session_state.bookings[k][:10]
            row_html += f'<div class="cell slot taken">✖ {name}</div>'
        else:
            row_html += f'<div class="cell slot free">+</div>'

    row_html += "</div>"
    st.markdown(row_html, unsafe_allow_html=True)

st.markdown('</div></div>', unsafe_allow_html=True)

# -----------------------
# CLICK LAYER (REAL LOGIC)
# -----------------------
st.markdown("###")  # spacing

for t in TIMES:
    cols = st.columns([0.8, 1, 1, 1])
    cols[0].write("")

    for i, s in enumerate(SLOTS):
        if cols[i+1].button(" ", key=f"btn_{t}_{s}"):
            toggle(st.session_state.date, t, s)
            st.rerun()

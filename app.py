import streamlit as st
import pandas as pd
import os
from datetime import datetime, timedelta
import streamlit.components.v1 as components

st.set_page_config(layout="centered")

# ===== DATA =====
BOOKINGS_FILE = "bookings.csv"

def load():
    if os.path.exists(BOOKINGS_FILE):
        return pd.read_csv(BOOKINGS_FILE, dtype=str)
    return pd.DataFrame(columns=["Name","Date","Table","Time"])

def save(df):
    df.to_csv(BOOKINGS_FILE, index=False)

bookings = load()

# ===== SESSION =====
if "name" not in st.session_state:
    st.session_state.name = "Tom"

if "date" not in st.session_state:
    st.session_state.date = str(datetime.now().date())

# ===== ACTION =====
params = st.query_params

if "a" in params:
    a = params["a"]
    v = params.get("v","")

    if a == "date":
        st.session_state.date = v

    elif a == "book":
        t, table = v.split("|")
        bookings = pd.concat([bookings, pd.DataFrame([{
            "Name": st.session_state.name,
            "Date": st.session_state.date,
            "Table": table,
            "Time": t
        }])])
        save(bookings)

    elif a == "del":
        t, table = v.split("|")
        bookings = bookings[~(
            (bookings["Date"]==st.session_state.date) &
            (bookings["Table"]==table) &
            (bookings["Time"]==t)
        )]
        save(bookings)

    st.query_params.clear()
    st.rerun()

# ===== HEADER =====
st.markdown(f"👤 **{st.session_state.name} | {st.session_state.date}**")

# ===== BUILD UI =====
today = datetime.now().date()

# ---- DATE GRID ----
dates_html = ""
for i in range(7):
    d = today + timedelta(days=i)
    ds = str(d)

    cls = "date"
    if ds == st.session_state.date:
        cls += " sel"

    dates_html += f"""
    <div class="{cls}" onclick="go('date','{ds}')">
        {d.strftime('%a')}<br>{d.day}
    </div>
    """

# ---- TABLE ----
HOURS = [f"{h:02d}:{m}" for h in range(6,22) for m in ["00","30"]]

rows = ""

for t in HOURS:
    rows += f'<div class="cell time">{t}</div>'

    for i in range(1,4):
        table = f"T{i}"

        match = bookings[
            (bookings["Date"]==st.session_state.date) &
            (bookings["Table"]==table) &
            (bookings["Time"]==t)
        ]

        if not match.empty:
            name = match.iloc[0]["Name"][:10]
            rows += f"""
            <div class="cell taken" onclick="go('del','{t}|{table}')">
                ✖ {name}
            </div>
            """
        else:
            rows += f"""
            <div class="cell free" onclick="go('book','{t}|{table}')">+</div>
            """

# ===== HTML =====
html = f"""
<style>
.wrap {{
    width:100%;
    max-width:360px;
    margin:auto;
    font-family:sans-serif;
}}

.dates {{
    display:grid;
    grid-template-columns:repeat(4,1fr);
    gap:4px;
}}

.date {{
    text-align:center;
    background:#e5e7eb;
    padding:6px 0;
    font-size:10px;
    border-radius:10px;
}}

.sel {{
    background:#4f46e5;
    color:white;
}}

.grid {{
    display:grid;
    grid-template-columns:60px repeat(3,1fr);
    gap:4px;
    margin-top:10px;
}}

.cell {{
    height:34px;
    display:flex;
    align-items:center;
    justify-content:center;
    font-size:10px;
    border-radius:10px;
}}

.time {{ background:#f3f4f6; }}
.free {{ background:#bbf7d0; }}
.taken {{ background:#fecaca; }}

</style>

<div class="wrap">
    <div class="dates">{dates_html}</div>

    <div class="grid">
        <div class="cell">Time</div>
        <div class="cell">T1</div>
        <div class="cell">T2</div>
        <div class="cell">T3</div>

        {rows}
    </div>
</div>

<script>
function go(a,v){{
    const url = new URL(window.parent.location);
    url.searchParams.set("a",a);
    url.searchParams.set("v",v);
    window.parent.location.href = url;
}}
</script>
"""

components.html(html, height=1200, scrolling=True)

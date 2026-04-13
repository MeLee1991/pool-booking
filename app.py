import streamlit as st
import pandas as pd
import os
from datetime import datetime, timedelta
import streamlit.components.v1 as components

st.set_page_config(layout="centered")

# ===== FILE =====
FILE = "bookings.csv"

def load():
    if os.path.exists(FILE):
        return pd.read_csv(FILE, dtype=str)
    return pd.DataFrame(columns=["Name","Date","Table","Time"])

def save(df):
    df.to_csv(FILE, index=False)

bookings = load()

# ===== SESSION =====
if "name" not in st.session_state:
    st.session_state.name = "Tom"

if "date" not in st.session_state:
    st.session_state.date = str(datetime.now().date())

# ===== UI BUILD =====
today = datetime.now().date()

# ---- DATES ----
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
            <div class="cell free" onclick="go('book','{t}|{table}')">
                +
            </div>
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
    gap:6px;
}}

.date {{
    text-align:center;
    background:#e5e7eb;
    padding:8px 0;
    font-size:10px;
    border-radius:12px;
}}

.sel {{
    background:#4f46e5;
    color:white;
}}

.grid {{
    display:grid;
    grid-template-columns:60px repeat(3,1fr);
    gap:6px;
    margin-top:12px;
}}

.cell {{
    height:38px;
    display:flex;
    align-items:center;
    justify-content:center;
    font-size:10px;
    border-radius:12px;
    font-weight:500;
}}

.time {{ background:#e5e7eb; }}
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
function go(action, value){{
    window.parent.postMessage({{
        type: "streamlit:setComponentValue",
        value: action + "|" + value
    }}, "*");
}}
</script>
"""

# ===== RENDER =====
result = components.html(html, height=1200, scrolling=True)

# ===== ACTION HANDLER =====
if result:
    action, value = result.split("|")

    if action == "date":
        st.session_state.date = value

    elif action == "book":
        t, table = value.split("|")
        bookings = pd.concat([bookings, pd.DataFrame([{
            "Name": st.session_state.name,
            "Date": st.session_state.date,
            "Table": table,
            "Time": t
        }])])
        save(bookings)

    elif action == "del":
        t, table = value.split("|")
        bookings = bookings[~(
            (bookings["Date"]==st.session_state.date) &
            (bookings["Table"]==table) &
            (bookings["Time"]==t)
        )]
        save(bookings)

    st.rerun()

import os
import json
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import streamlit.components.v1 as components

st.set_page_config(page_title="Pool", layout="centered")

# ================= DATA =================
USERS_FILE = "users.csv"
BOOKINGS_FILE = "bookings.csv"

def load_data(file, cols):
    if os.path.exists(file):
        return pd.read_csv(file, dtype=str)
    return pd.DataFrame(columns=cols)

def save_data(df, file):
    df.to_csv(file, index=False)

if "users" not in st.session_state:
    st.session_state.users = load_data(USERS_FILE, ["Email","Name","Password","Role"])
if "bookings" not in st.session_state:
    st.session_state.bookings = load_data(BOOKINGS_FILE, ["User","Name","Date","Table","Time"])

for k in ["user","name","role","sel_date","action"]:
    if k not in st.session_state:
        st.session_state[k] = None

if not st.session_state.sel_date:
    st.session_state.sel_date = str(datetime.now().date())

# ================= LOGIN =================
if st.session_state.user is None:
    st.title("Pool Login")
    e = st.text_input("Email")
    p = st.text_input("Password", type="password")

    if st.button("Login"):
        m = st.session_state.users[
            (st.session_state.users["Email"]==e)&
            (st.session_state.users["Password"]==p)
        ]
        if not m.empty:
            st.session_state.user = e
            st.session_state.name = m.iloc[0]["Name"]
            st.session_state.role = m.iloc[0]["Role"]
            st.rerun()
    st.stop()

# ================= HANDLE ACTION =================
if st.session_state.action:
    a = st.session_state.action
    st.session_state.action = None

    if a["type"] == "date":
        st.session_state.sel_date = a["value"]

    elif a["type"] in ["book","del"]:
        t, table = a["value"].split("|")

        if a["type"] == "book":
            new = pd.DataFrame([{
                "User": st.session_state.user,
                "Name": st.session_state.name,
                "Date": st.session_state.sel_date,
                "Table": table,
                "Time": t
            }])
            st.session_state.bookings = pd.concat([st.session_state.bookings,new])

        elif a["type"] == "del":
            df = st.session_state.bookings
            st.session_state.bookings = df[
                ~((df["Table"]==table)&
                  (df["Time"]==t)&
                  (df["Date"]==st.session_state.sel_date))
            ]

        save_data(st.session_state.bookings, BOOKINGS_FILE)

    st.rerun()

# ================= UI HEADER =================
st.write(f"👤 {st.session_state.name} | {st.session_state.sel_date}")

# ================= BUILD HTML =================
today = datetime.now().date()

date_html = ""
for i in range(14):
    d = today + timedelta(days=i)
    d_str = str(d)

    label = f"{d.day}.{d.strftime('%a')}"
    cls = "date"

    if i == 0:
        label = "TOD"
        cls += " tod"
    elif i == 1:
        label = "TOM"
        cls += " tom"

    if d_str == st.session_state.sel_date:
        cls += " sel"

    date_html += f"<div class='{cls}' onclick=\"send('date','{d_str}')\">{label}</div>"

HOURS = [f"{h:02d}:{m}" for h in range(6,24) for m in ["00","30"]]

grid_html = ""
for idx, t in enumerate(HOURS):
    band = ["tA","tB","tC","tD"][(idx//8)%4]
    grid_html += f"<div class='cell time {band}'>{t}</div>"

    for i in range(1,4):
        table = f"Table {i}"

        match = st.session_state.bookings[
            (st.session_state.bookings["Table"]==table)&
            (st.session_state.bookings["Time"]==t)&
            (st.session_state.bookings["Date"]==st.session_state.sel_date)
        ]

        if not match.empty:
            user = match.iloc[0]["User"]
            name = match.iloc[0]["Name"][:3]

            if user == st.session_state.user:
                grid_html += f"<div class='cell mine' onclick=\"send('del','{t}|{table}')\">✕ {name}</div>"
            else:
                grid_html += f"<div class='cell taken'>{name}</div>"
        else:
            grid_html += f"<div class='cell free' onclick=\"send('book','{t}|{table}')\">+</div>"

html = f"""
<style>
.dates {{
    display:grid;
    grid-template-columns:repeat(7,1fr);
    gap:4px;
    margin-bottom:10px;
}}
.date {{
    font-size:9px;
    padding:6px;
    text-align:center;
    border-radius:6px;
    background:#e5e7eb;
}}
.sel {{ background:#4f46e5; color:white; }}
.tod {{ background:#22c55e; color:white; }}
.tom {{ background:#3b82f6; color:white; }}

.grid {{
    display:grid;
    grid-template-columns:60px repeat(3,1fr);
    gap:4px;
}}

.cell {{
    height:32px;
    font-size:10px;
    display:flex;
    align-items:center;
    justify-content:center;
    border-radius:6px;
}}

.header {{ background:#111; color:white; }}
.time {{ background:#f3f4f6; }}
.tA {{ background:#f3f4f6; }}
.tB {{ background:#e0f2fe; }}
.tC {{ background:#fef3c7; }}
.tD {{ background:#ede9fe; }}

.free {{ background:#bbf7d0; }}
.mine {{ background:#93c5fd; }}
.taken {{ background:#e5e7eb; }}
</style>

<div class="dates">{date_html}</div>

<div class="grid">
<div class="cell header">Time</div>
<div class="cell header">T1</div>
<div class="cell header">T2</div>
<div class="cell header">T3</div>
{grid_html}
</div>

<script>
function send(type, value) {{
    window.parent.postMessage({{type:type, value:value}}, "*");
}}

window.addEventListener("message", (event) => {{
    const data = event.data;
}});
</script>
"""

# send clicks back
clicked = components.html(html, height=1500)

if clicked:
    st.session_state.action = clicked
    st.rerun()

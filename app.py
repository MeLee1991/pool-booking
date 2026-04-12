import os
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

for k in ["user","name","role","sel_date"]:
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

# ================= ACTION HANDLER =================
params = st.query_params

if "a" in params and "v" in params:
    a = params["a"]
    v = params["v"]

    if a == "date":
        st.session_state.sel_date = v

    elif a == "swipe":
        d = datetime.strptime(st.session_state.sel_date, "%Y-%m-%d").date()
        if v == "next":
            d += timedelta(days=1)
        else:
            d -= timedelta(days=1)
        st.session_state.sel_date = str(d)

    else:
        t, table = v.split("|")

        if a == "book":
            new = pd.DataFrame([{
                "User": st.session_state.user,
                "Name": st.session_state.name,
                "Date": st.session_state.sel_date,
                "Table": table,
                "Time": t
            }])
            st.session_state.bookings = pd.concat([st.session_state.bookings,new])

        elif a == "del":
            df = st.session_state.bookings
            st.session_state.bookings = df[
                ~((df["Table"]==table)&
                  (df["Time"]==t)&
                  (df["Date"]==st.session_state.sel_date))
            ]

        save_data(st.session_state.bookings, BOOKINGS_FILE)

    st.query_params.clear()
    st.rerun()

# ================= UI HEADER =================
st.write(f"👤 {st.session_state.name} | {st.session_state.sel_date}")

# ================= HTML =================
today = datetime.now().date()

# DATES (2 rows)
dates_html = ""
for i in range(14):
    d = today + timedelta(days=i)
    d_str = str(d)

    label = f"{d.day}.{d.strftime('%a')}"
    cls = "date"

    if d_str == st.session_state.sel_date:
        cls += " sel"

    dates_html += f"<div class='{cls}' onclick=\"go('date','{d_str}')\">{label}</div>"

# TABLE
HOURS = [f"{h:02d}:{m}" for h in range(6,24) for m in ["00","30"]]

grid_html = ""
for t in HOURS:
    grid_html += f"<div class='cell time'>{t}</div>"

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
                grid_html += f"<div class='cell mine' onclick=\"go('del','{t}|{table}')\">✕ {name}</div>"
            else:
                grid_html += f"<div class='cell taken'>{name}</div>"
        else:
            grid_html += f"<div class='cell free' onclick=\"go('book','{t}|{table}')\">+</div>"

html = f"""
<meta name="viewport" content="width=device-width, initial-scale=1">

<style>
body {{ margin:0; font-family:sans-serif; }}

.dates {{
    display:grid;
    grid-template-columns:repeat(7,1fr);
    gap:4px;
    margin-bottom:10px;
}}

.date {{
    padding:6px;
    font-size:10px;
    text-align:center;
    background:#e5e7eb;
    border-radius:6px;
}}

.sel {{
    background:#4f46e5;
    color:white;
    font-weight:bold;
}}

.grid {{
    display:grid;
    grid-template-columns:60px repeat(3,1fr);
    gap:4px;
}}

.cell {{
    height:30px;
    font-size:10px;
    display:flex;
    align-items:center;
    justify-content:center;
    border-radius:6px;
}}

.time {{ background:#f3f4f6; }}
.free {{ background:#bbf7d0; }}
.mine {{ background:#93c5fd; }}
.taken {{ background:#e5e7eb; }}
</style>

<div class="dates">{dates_html}</div>

<div class="grid">
<div class="cell">T</div>
<div class="cell">1</div>
<div class="cell">2</div>
<div class="cell">3</div>
{grid_html}
</div>

<script>
function go(a,v){{
    const url = new URL(window.parent.location.href);
    url.searchParams.set("a", a);
    url.searchParams.set("v", v);
    window.parent.location.href = url;
}}

// SWIPE
let startX = 0;

document.addEventListener("touchstart", e => {{
    startX = e.touches[0].clientX;
}});

document.addEventListener("touchend", e => {{
    let endX = e.changedTouches[0].clientX;
    if (endX - startX > 80) go("swipe","prev");
    if (startX - endX > 80) go("swipe","next");
}});
</script>
"""

components.html(html, height=1500, scrolling=True)

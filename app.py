import streamlit as st
import pandas as pd
import os
from datetime import datetime, timedelta
import streamlit.components.v1 as components

st.set_page_config(layout="centered")

# ================= DATA =================
USERS_FILE = "users.csv"
BOOKINGS_FILE = "bookings.csv"

def load(file, cols):
    if os.path.exists(file):
        return pd.read_csv(file, dtype=str)
    return pd.DataFrame(columns=cols)

def save(df, file):
    df.to_csv(file, index=False)

users = load(USERS_FILE, ["Email","Name","Password","Role"])
bookings = load(BOOKINGS_FILE, ["User","Name","Date","Table","Time"])

# default user
if "tom3@gmail.com" not in users["Email"].values:
    users = pd.concat([users, pd.DataFrame([{
        "Email":"tom3@gmail.com",
        "Name":"Tom",
        "Password":"1234",
        "Role":"admin"
    }])])
    save(users, USERS_FILE)

# ================= SESSION =================
for k in ["user","name","role","date"]:
    if k not in st.session_state:
        st.session_state[k] = None

if not st.session_state.date:
    st.session_state.date = str(datetime.now().date())

# ================= LOGIN =================
if st.session_state.user is None:
    e = st.text_input("Email", value="tom3@gmail.com")
    p = st.text_input("Password", type="password", value="1234")

    if st.button("Login"):
        m = users[(users["Email"]==e)&(users["Password"]==p)]
        if not m.empty:
            st.session_state.user = e
            st.session_state.name = m.iloc[0]["Name"]
            st.session_state.role = m.iloc[0]["Role"]
            st.rerun()
    st.stop()

# ================= ACTION HANDLER =================
params = st.query_params
if "a" in params:
    act = params["a"]
    val = params.get("v","")

    if act == "date":
        st.session_state.date = val

    elif act == "book":
        t, table = val.split("|")
        bookings = pd.concat([bookings, pd.DataFrame([{
            "User": st.session_state.user,
            "Name": st.session_state.name,
            "Date": st.session_state.date,
            "Table": table,
            "Time": t
        }])])
        save(bookings, BOOKINGS_FILE)

    elif act == "del":
        t, table = val.split("|")
        mask = (
            (bookings["Table"]==table) &
            (bookings["Time"]==t) &
            (bookings["Date"]==st.session_state.date)
        )
        bookings = bookings[~mask]
        save(bookings, BOOKINGS_FILE)

    st.query_params.clear()
    st.rerun()

# ================= HEADER =================
st.markdown(f"👤 **{st.session_state.name} | {st.session_state.date}**")

# ================= UI =================
today = datetime.now().date()
HOURS = [f"{h:02d}:{m}" for h in range(6,24) for m in ["00","30"]]

# -------- DATE GRID --------
dates_html = ""
for i in range(14):
    d = today + timedelta(days=i)
    ds = str(d)
    label = "TOD" if i==0 else ("TOM" if i==1 else d.strftime("%a"))

    cls = "date"
    if ds == st.session_state.date:
        cls += " sel"

    dates_html += f"""
    <div class="{cls}" onclick="go('date','{ds}')">
        {label}<br>{d.day}
    </div>
    """

# -------- TABLE --------
rows_html = ""

for t in HOURS:
    rows_html += f'<div class="cell time">{t}</div>'

    for i in range(1,4):
        table = f"Table {i}"

        match = bookings[
            (bookings["Table"]==table) &
            (bookings["Time"]==t) &
            (bookings["Date"]==st.session_state.date)
        ]

        if not match.empty:
            name = match.iloc[0]["Name"][:10]
            user = match.iloc[0]["User"]

            if user == st.session_state.user:
                rows_html += f"""
                <div class="cell mine" onclick="go('del','{t}|{table}')">
                    ✖ {name}
                </div>
                """
            else:
                rows_html += f"""
                <div class="cell taken">{name}</div>
                """
        else:
            rows_html += f"""
            <div class="cell free" onclick="go('book','{t}|{table}')">+</div>
            """

# -------- HTML --------
html = f"""
<style>
body {{ margin:0; }}

.wrap {{
    max-width:360px;
    margin:auto;
    font-family:sans-serif;
}}

.dates {{
    display:grid;
    grid-template-columns:repeat(7,1fr);
    gap:4px;
}}

.date {{
    background:#e5e7eb;
    text-align:center;
    padding:6px 2px;
    font-size:10px;
    border-radius:10px;
}}

.date.sel {{
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
.mine {{ background:#93c5fd; }}

</style>

<div class="wrap">
    <div class="dates">{dates_html}</div>
    <div class="grid">
        <div class="cell">Time</div>
        <div class="cell">T1</div>
        <div class="cell">T2</div>
        <div class="cell">T3</div>
        {rows_html}
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

components.html(html, height=1600, scrolling=True)

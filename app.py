import streamlit as st
import pandas as pd
import os
from datetime import datetime, timedelta

st.set_page_config(layout="centered")

# ================= FILES =================
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

# test user
if "tom3@gmail.com" not in users["Email"].values:
    users = pd.concat([users, pd.DataFrame([{
        "Email":"tom3@gmail.com",
        "Name":"Tom",
        "Password":"1234",
        "Role":"admin"
    }])])
    save(users, USERS_FILE)

# ================= SESSION =================
for k in ["user","name","role","date","page"]:
    if k not in st.session_state:
        st.session_state[k] = None

if not st.session_state.date:
    st.session_state.date = str(datetime.now().date())

if not st.session_state.page:
    st.session_state.page = "grid"

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

if params.get("a"):
    act = params.get("a")
    val = params.get("v")

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

# ================= ADMIN =================
if st.session_state.page == "admin":
    st.title("Admin")

    if st.button("← Back"):
        st.session_state.page = "grid"
        st.rerun()

    st.dataframe(users, use_container_width=True)

    with st.expander("Add user"):
        email = st.text_input("Email")
        name = st.text_input("Name")
        pw = st.text_input("Password")
        role = st.selectbox("Role", ["user","admin"])

        if st.button("Add"):
            users = pd.concat([users, pd.DataFrame([{
                "Email":email,
                "Name":name,
                "Password":pw,
                "Role":role
            }])])
            save(users, USERS_FILE)
            st.rerun()

    st.stop()

# ================= HEADER =================
st.markdown(f"👤 **{st.session_state.name} | {st.session_state.date}**")

if st.session_state.role == "admin":
    if st.button("⚙️ Admin Control", use_container_width=True):
        st.session_state.page = "admin"
        st.rerun()

# ================= BUILD UI =================
today = datetime.now().date()

# DATES
dates_html = ""
date_list = []

for i in range(14):
    d = today + timedelta(days=i)
    ds = str(d)
    date_list.append(ds)

    label = "TOD" if i==0 else ("TOM" if i==1 else d.strftime("%a").upper())
    num = d.day

    sel = "sel" if ds == st.session_state.date else ""

    dates_html += f"""
    <div class="date {sel}" data-date="{ds}" onclick="go('date','{ds}')">
        {label}<br>{num}
    </div>
    """

# TIMES
HOURS = [f"{h:02d}:{m}" for h in range(6,24) for m in ["00","30"]]

grid = ""

for idx, t in enumerate(HOURS):
    band = ["b1","b2","b3","b4"][(idx//8)%4]
    grid += f'<div class="cell time {band}">{t}</div>'

    for i in range(1,4):
        table = f"Table {i}"

        match = bookings[
            (bookings["Table"]==table)&
            (bookings["Time"]==t)&
            (bookings["Date"]==st.session_state.date)
        ]

        if not match.empty:
            name = match.iloc[0]["Name"][:10]
            user = match.iloc[0]["User"]

            if user == st.session_state.user:
                grid += f'<div class="cell mine" onclick="go(\'del\',\'{t}|{table}\')">X {name}</div>'
            else:
                grid += f'<div class="cell taken">X {name}</div>'
        else:
            grid += f'<div class="cell free" onclick="go(\'book\',\'{t}|{table}\')">+</div>'

# ================= HTML =================
html = f"""
<html>
<head>
<meta name="viewport" content="width=device-width, initial-scale=1">
<style>

body {{ margin:0; padding:8px; font-family:sans-serif; }}

.dates {{
    display:grid;
    grid-template-columns:repeat(7,1fr);
    gap:4px;
}}

.date {{
    font-size:10px;
    padding:6px;
    text-align:center;
    background:#e5e7eb;
    border-radius:8px;
}}

.date.sel {{
    background:#4f46e5;
    color:white;
}}

.grid {{
    display:grid;
    grid-template-columns: repeat(4,1fr);
    gap:4px;
    margin-top:10px;
}}

.cell {{
    height:36px;
    font-size:10px;
    display:flex;
    align-items:center;
    justify-content:center;
    border-radius:10px;
}}

.time {{ background:#e5e7eb; }}
.free {{ background:#bbf7d0; }}
.taken {{ background:#fecaca; }}
.mine {{ background:#93c5fd; }}

.b1 {{ background:#f3f4f6; }}
.b2 {{ background:#e0f2fe; }}
.b3 {{ background:#fef3c7; }}
.b4 {{ background:#ede9fe; }}

</style>
</head>

<body>

<div class="dates">{dates_html}</div>

<div class="grid">
<div class="cell"><b>Time</b></div>
<div class="cell"><b>T1</b></div>
<div class="cell"><b>T2</b></div>
<div class="cell"><b>T3</b></div>

{grid}

</div>

<script>

function go(a,v){{
    const url = new URL(window.parent.location.href);
    url.searchParams.set("a",a);
    url.searchParams.set("v",v);
    window.parent.location.href = url;
}}

// SWIPE
let startX=0,endX=0;

document.addEventListener('touchstart',e=>startX=e.changedTouches[0].screenX);
document.addEventListener('touchend',e=>{{
    endX=e.changedTouches[0].screenX;
    let diff=endX-startX;

    if(Math.abs(diff)<50) return;

    const dates=[...document.querySelectorAll('.date')];
    const sel=document.querySelector('.date.sel');
    let idx=dates.indexOf(sel);

    if(diff<0 && idx<dates.length-1) dates[idx+1].click();
    if(diff>0 && idx>0) dates[idx-1].click();
}});

</script>

</body>
</html>
"""

st.components.v1.html(html, height=1600, scrolling=True)

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
    if os.path.exists(file) and os.path.getsize(file) > 0:
        return pd.read_csv(file, dtype=str)
    return pd.DataFrame(columns=cols)

def save_data(df, file):
    df.to_csv(file, index=False)

if "users" not in st.session_state:
    st.session_state.users = load_data(USERS_FILE, ["Email","Name","Password","Role"])
if "bookings" not in st.session_state:
    st.session_state.bookings = load_data(BOOKINGS_FILE, ["User","Name","Date","Table","Time"])

for k in ["user","name","role","sel_date","page"]:
    if k not in st.session_state:
        st.session_state[k] = None

if not st.session_state.sel_date:
    st.session_state.sel_date = str(datetime.now().date())
if not st.session_state.page:
    st.session_state.page = "Booking"

# ================= LOGIN =================
if st.session_state.user is None:
    st.title("Pool Login")

    e = st.text_input("Email").lower().strip()
    p = st.text_input("Password", type="password")

    if st.button("Login"):
        m = st.session_state.users[
            (st.session_state.users["Email"]==e) &
            (st.session_state.users["Password"]==p)
        ]
        if not m.empty:
            st.session_state.user = e
            st.session_state.name = m.iloc[0]["Name"]
            st.session_state.role = m.iloc[0]["Role"]
            st.rerun()
    st.stop()

# ================= ADMIN =================
if st.session_state.page == "Admin":
    st.title("Admin")

    if st.button("← Back"):
        st.session_state.page = "Booking"
        st.rerun()

    st.dataframe(st.session_state.users)

    e = st.text_input("Email")
    n = st.text_input("Name")
    p = st.text_input("Password")
    r = st.selectbox("Role", ["user","admin"])

    if st.button("Add User"):
        new = pd.DataFrame([{"Email":e,"Name":n,"Password":p,"Role":r}])
        st.session_state.users = pd.concat([st.session_state.users,new], ignore_index=True)
        save_data(st.session_state.users, USERS_FILE)
        st.rerun()

    st.download_button("Download bookings", st.session_state.bookings.to_csv(index=False))
    st.stop()

# ================= ACTION HANDLER =================
params = st.query_params

if "a" in params and "v" in params:
    a = params.get("a")
    v = params.get("v")

    bookings = st.session_state.bookings

    if a == "date":
        st.session_state.sel_date = v

    elif a == "book":
        t, table = v.split("|")

        exists = bookings[
            (bookings["Table"]==table) &
            (bookings["Time"]==t) &
            (bookings["Date"]==st.session_state.sel_date)
        ]

        if exists.empty:
            new = pd.DataFrame([{
                "User": st.session_state.user,
                "Name": st.session_state.name,
                "Date": st.session_state.sel_date,
                "Table": table,
                "Time": t
            }])
            bookings = pd.concat([bookings,new], ignore_index=True)

    elif a == "del":
        t, table = v.split("|")

        bookings = bookings[
            ~(
                (bookings["Table"]==table) &
                (bookings["Time"]==t) &
                (bookings["Date"]==st.session_state.sel_date)
            )
        ]

    st.session_state.bookings = bookings
    save_data(bookings, BOOKINGS_FILE)

    st.query_params.clear()
    st.rerun()

# ================= UI =================
today = datetime.now().date()

date_cells = ""
for i in range(14):
    d = today + timedelta(days=i)
    d_str = str(d)

    label = f"{d.day}.{d.strftime('%a')}"
    cls = "date"
    if d_str == st.session_state.sel_date:
        cls += " sel"

    date_cells += f'<div class="{cls}" onclick="send(\'date\',\'{d_str}\')">{label}</div>'

HOURS = [f"{h:02d}:{m}" for h in range(6,24) for m in ["00","30"]]

grid_rows = ""
for idx, t in enumerate(HOURS):

    color = ["tA","tB","tC","tD"][(idx//8)%4]
    grid_rows += f'<div class="cell {color}">{t}</div>'

    for i in range(1,4):
        table = f"Table {i}"

        match = st.session_state.bookings[
            (st.session_state.bookings["Table"]==table) &
            (st.session_state.bookings["Time"]==t) &
            (st.session_state.bookings["Date"]==st.session_state.sel_date)
        ]

        if not match.empty:
            name = match.iloc[0]["Name"][:3]
            user = match.iloc[0]["User"]

            if user == st.session_state.user:
                grid_rows += f'<div class="cell mine" onclick="send(\'del\',\'{t}|{table}\')">✕{name}</div>'
            else:
                grid_rows += f'<div class="cell taken">{name}</div>'
        else:
            grid_rows += f'<div class="cell free" onclick="send(\'book\',\'{t}|{table}\')">+</div>'

html = f"""
<style>
body {{ margin:0; font-family:sans-serif; }}
.dates {{ display:grid; grid-template-columns:repeat(7,1fr); gap:3px; margin-bottom:10px; }}
.date {{ padding:6px; text-align:center; background:#eee; border-radius:6px; font-size:9px; }}
.sel {{ background:#4f46e5; color:white; }}

.grid {{ display:grid; grid-template-columns:44px repeat(3,1fr); gap:3px; }}
.cell {{ height:28px; display:flex; align-items:center; justify-content:center; border-radius:6px; font-size:9px; }}

.free {{ background:#bbf7d0; }}
.mine {{ background:#93c5fd; }}
.taken {{ background:#e5e7eb; }}

.tA {{ background:#f3f4f6; }}
.tB {{ background:#e0f2fe; }}
.tC {{ background:#fef3c7; }}
.tD {{ background:#ede9fe; }}
</style>

<div class="dates">{date_cells}</div>

<div class="grid">
<div class="cell">T</div>
<div class="cell">1</div>
<div class="cell">2</div>
<div class="cell">3</div>
{grid_rows}
</div>

<script>
function send(a,v){{
    const url = new URL(window.parent.location.href);
    url.searchParams.set("a", a);
    url.searchParams.set("v", v);
    window.parent.location.href = url.toString();
}}
</script>
"""

components.html(html, height=1500, scrolling=False)

# ================= HEADER =================
st.write(f"👤 {st.session_state.name} | {st.session_state.sel_date}")

if st.session_state.role == "admin":
    if st.button("Admin"):
        st.session_state.page = "Admin"
        st.rerun()

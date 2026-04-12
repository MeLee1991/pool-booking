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

for k in ["user","name","role","sel_date","page","edit_user"]:
    if k not in st.session_state:
        st.session_state[k] = None

if not st.session_state.sel_date:
    st.session_state.sel_date = str(datetime.now().date())
if not st.session_state.page:
    st.session_state.page = "Booking"

# ================= LOGIN =================
if st.session_state.user is None:
    st.title("Pool Login")

    e = st.text_input("Email").strip()
    p = st.text_input("Password", type="password")

    if st.button("Login"):
        match = st.session_state.users[
            (st.session_state.users["Email"]==e) &
            (st.session_state.users["Password"]==p)
        ]
        if not match.empty:
            st.session_state.user = e
            st.session_state.name = match.iloc[0]["Name"]
            st.session_state.role = match.iloc[0]["Role"]
            st.rerun()
    st.stop()

# ================= ADMIN =================
if st.session_state.page == "Admin":
    st.title("⚙️ Admin")

    if st.button("← Back"):
        st.session_state.page = "Booking"
        st.rerun()

    users = st.session_state.users

    st.subheader("Users")

    for idx, u in users.iterrows():
        col1, col2, col3, col4 = st.columns([3,3,1,1])
        col1.write(f"{u['Name']} ({u['Role']})")
        col2.write(u["Email"])

        if col3.button("✏️", key=f"edit_{idx}"):
            st.session_state.edit_user = idx
            st.rerun()

        if col4.button("🗑️", key=f"del_{idx}"):
            users = users.drop(idx).reset_index(drop=True)
            st.session_state.users = users
            save_data(users, USERS_FILE)
            st.rerun()

    st.divider()

    # ===== ADD / EDIT =====
    mode = "Add" if st.session_state.edit_user is None else "Edit"
    st.subheader(f"{mode} User")

    if st.session_state.edit_user is not None:
        u = users.iloc[st.session_state.edit_user]
        default_email = u["Email"]
        default_name = u["Name"]
        default_pass = u["Password"]
        default_role = u["Role"]
    else:
        default_email = default_name = default_pass = ""
        default_role = "user"

    email = st.text_input("Email", value=default_email, key="email_input")
    name = st.text_input("Name", value=default_name, key="name_input")
    password = st.text_input("Password", value=default_pass, key="password_input")
    role = st.selectbox("Role", ["user","admin"], index=0 if default_role=="user" else 1)

    if st.button("Save User"):
        if st.session_state.edit_user is None:
            new = pd.DataFrame([{"Email":email,"Name":name,"Password":password,"Role":role}])
            users = pd.concat([users,new], ignore_index=True)
        else:
            users.loc[st.session_state.edit_user] = [email,name,password,role]

        st.session_state.users = users
        save_data(users, USERS_FILE)

        # RESET FORM
        st.session_state.edit_user = None
        st.session_state.email_input = ""
        st.session_state.name_input = ""
        st.session_state.password_input = ""

        st.rerun()

    st.stop()

# ================= ACTION HANDLER =================
params = st.query_params

if "a" in params and "v" in params:
    action = params["a"]
    value = params["v"]

    if action == "date":
        st.session_state.sel_date = value

    else:
        t, table = value.split("|")

        if action == "book":
            new = pd.DataFrame([{
                "User": st.session_state.user,
                "Name": st.session_state.name,
                "Date": st.session_state.sel_date,
                "Table": table,
                "Time": t
            }])
            st.session_state.bookings = pd.concat([st.session_state.bookings,new], ignore_index=True)

        elif action == "del":
            df = st.session_state.bookings
            st.session_state.bookings = df[
                ~((df["Table"]==table)&
                  (df["Time"]==t)&
                  (df["Date"]==st.session_state.sel_date))
            ]

        save_data(st.session_state.bookings, BOOKINGS_FILE)

    st.query_params.clear()
    st.rerun()

# ================= HEADER =================
st.write(f"👤 {st.session_state.name} | {st.session_state.sel_date}")

if st.session_state.role == "admin":
    if st.button("⚙️ Admin"):
        st.session_state.page = "Admin"
        st.rerun()

# ================= GRID =================
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

    date_html += f"<div class='{cls}' onclick=\"click('date','{d_str}')\">{label}</div>"

HOURS = [f"{h:02d}:{m}" for h in range(6,24) for m in ["00","30"]]

grid_html = ""
for idx, t in enumerate(HOURS):
    band = ["tA","tB","tC","tD"][(idx//8)%4]
    grid_html += f"<div class='cell time {band}'>{t}</div>"

    for i in range(1,4):
        table = f"Table {i}"

        match = st.session_state.bookings[
            (st.session_state.bookings["Table"]==table) &
            (st.session_state.bookings["Time"]==t) &
            (st.session_state.bookings["Date"]==st.session_state.sel_date)
        ]

        if not match.empty:
            user = match.iloc[0]["User"]
            name = match.iloc[0]["Name"][:3]

            if user == st.session_state.user or st.session_state.role == "admin":
                grid_html += f"<div class='cell mine' onclick=\"click('del','{t}|{table}')\">✕ {name}</div>"
            else:
                grid_html += f"<div class='cell taken'>{name}</div>"
        else:
            grid_html += f"<div class='cell free' onclick=\"click('book','{t}|{table}')\">+</div>"

html = f"""
<style>
.dates {{ display:grid; grid-template-columns:repeat(7,1fr); gap:4px; margin-bottom:10px; }}
.date {{ font-size:9px; padding:6px; text-align:center; border-radius:6px; background:#e5e7eb; }}
.sel {{ background:#4f46e5; color:white; }}
.tod {{ background:#22c55e; color:white; }}
.tom {{ background:#3b82f6; color:white; }}

.grid {{ display:grid; grid-template-columns:60px repeat(3,1fr); gap:4px; }}
.cell {{ height:32px; font-size:10px; display:flex; align-items:center; justify-content:center; border-radius:6px; }}

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
function click(a,v){{
    const url = new URL(window.parent.location.href);
    url.searchParams.set("a", a);
    url.searchParams.set("v", v);
    window.parent.location.href = url.toString();
}}
</script>
"""

components.html(html, height=1500, scrolling=True)

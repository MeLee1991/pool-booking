import os
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import streamlit.components.v1 as components

# 1. SETUP & PERSISTENCE
st.set_page_config(page_title="Pool", layout="centered")

# Custom CSS to keep the layout tight
st.markdown("<style>.block-container { max-width:330px !important; padding-top:1rem; }</style>", unsafe_allow_html=True)

USERS_FILE = "users.csv"
BOOKINGS_FILE = "bookings.csv"

def load_data(file, cols):
    if os.path.exists(file) and os.path.getsize(file) > 0:
        return pd.read_csv(file, dtype=str)
    return pd.DataFrame(columns=cols)

def save_data(df, file):
    df.to_csv(file, index=False)

# Load into session state to ensure "memory" between clicks
if "users" not in st.session_state:
    st.session_state.users = load_data(USERS_FILE, ["Email","Name","Password","Role"])
if "bookings" not in st.session_state:
    st.session_state.bookings = load_data(BOOKINGS_FILE, ["User","Name","Date","Table","Time"])

# Init session variables
for k in ["user","name","role","sel_date","page"]:
    if k not in st.session_state: st.session_state[k] = None

if not st.session_state.sel_date: st.session_state.sel_date = str(datetime.now().date())
if not st.session_state.page: st.session_state.page = "Booking"

# 2. THE BUTTON ENGINE (Query Params)
# This section listens to the HTML clicks
p = st.query_params

if "date" in p:
    st.session_state.sel_date = p["date"]
    st.query_params.clear()
    st.rerun()

if "book" in p:
    t, table = p["book"].split("|", 1)
    # Check if still free
    df = st.session_state.bookings
    exists = df[(df["Table"]==table) & (df["Time"]==t) & (df["Date"]==st.session_state.sel_date)]
    if exists.empty:
        new_row = pd.DataFrame([{"User": st.session_state.user, "Name": st.session_state.name, 
                                 "Date": st.session_state.sel_date, "Table": table, "Time": t}])
        st.session_state.bookings = pd.concat([st.session_state.bookings, new_row], ignore_index=True)
        save_data(st.session_state.bookings, BOOKINGS_FILE)
    st.query_params.clear()
    st.rerun()

if "del" in p:
    t, table = p["del"].split("|", 1)
    df = st.session_state.bookings
    # LOGIC: Admin deletes anything, User only deletes their own
    mask = (df["Table"]==table) & (df["Time"]==t) & (df["Date"]==st.session_state.sel_date)
    if st.session_state.role != "admin":
        mask = mask & (df["User"] == st.session_state.user)
    
    st.session_state.bookings = df[~mask]
    save_data(st.session_state.bookings, BOOKINGS_FILE)
    st.query_params.clear()
    st.rerun()

# 3. LOGIN PAGE
if st.session_state.user is None:
    st.title("🏊 Pool")
    e = st.text_input("Email").strip()
    p_in = st.text_input("Password", type="password").strip()
    if st.button("Login", use_container_width=True):
        u = st.session_state.users
        m = u[(u["Email"]==e) & (u["Password"]==p_in)]
        if not m.empty:
            st.session_state.user, st.session_state.name, st.session_state.role = e, m.iloc[0]["Name"], m.iloc[0]["Role"]
            st.rerun()
        else: st.error("Wrong credentials")
    st.stop()

# 4. SIDEBAR
with st.sidebar:
    st.write(f"**👤 {st.session_state.name}** ({st.session_state.role})")
    if st.session_state.role == "admin":
        if st.button("📅 Booking Grid"): st.session_state.page = "Booking"; st.rerun()
        if st.button("⚙️ Admin Panel"): st.session_state.page = "Admin"; st.rerun()
    if st.button("🚪 Logout"):
        for k in list(st.session_state.keys()): del st.session_state[k]
        st.rerun()

# 5. ADMIN PAGE
if st.session_state.page == "Admin":
    st.title("⚙️ Admin")
    # Add User
    with st.expander("Add User"):
        ae, an, ap = st.text_input("Email"), st.text_input("Name"), st.text_input("Pass")
        ar = st.selectbox("Role", ["user", "admin"])
        if st.button("Create"):
            new_u = pd.DataFrame([{"Email":ae,"Name":an,"Password":ap,"Role":ar}])
            st.session_state.users = pd.concat([st.session_state.users, new_u], ignore_index=True)
            save_data(st.session_state.users, USERS_FILE)
            st.rerun()
    st.dataframe(st.session_state.users, use_container_width=True)
    st.stop()

# 6. BOOKING GRID (THE LOOKOUT)
today = datetime.now().date()
HOURS = [f"{h:02d}:{m}" for h in range(6,24) for m in ["00","30"]]

date_cells = ""
for i in range(14):
    d = today + timedelta(days=i)
    d_str = str(d)
    label = f"TOD<br>{d.day}" if i==0 else (f"TOM<br>{d.day}" if i==1 else f"{d.strftime('%a')}<br>{d.day}")
    cls = "date"
    if i==0: cls += " d-today"
    if d_str == st.session_state.sel_date: cls += " sel"
    date_cells += f'<div class="{cls}" onclick="go(\'date\',\'{d_str}\')">{label}</div>'

grid_rows = ""
for idx, t in enumerate(HOURS):
    band = ["tA","tB","tC","tD"][(idx // 8) % 4]
    grid_rows += f'<div class="cell {band}">{t}</div>'
    for i in range(1, 4):
        table = f"Table {i}"
        match = st.session_state.bookings[
            (st.session_state.bookings["Table"]==table) & 
            (st.session_state.bookings["Time"]==t) & 
            (st.session_state.bookings["Date"]==st.session_state.sel_date)
        ]
        if not match.empty:
            b_user = match.iloc[0]["User"]
            b_name = match.iloc[0]["Name"][:3]
            # Admin can delete anything (mine class), User only their own
            if b_user == st.session_state.user or st.session_state.role == "admin":
                grid_rows += f'<div class="cell mine" onclick="go(\'del\',\'{t}|{table}\')">✕ {b_name}</div>'
            else:
                grid_rows += f'<div class="cell taken">{b_name}</div>'
        else:
            grid_rows += f'<div class="cell free" onclick="go(\'book\',\'{t}|{table}\')">+</div>'

html_code = f"""
<!DOCTYPE html><html><head><meta name="viewport" content="width=device-width, initial-scale=1">
<style>
    * {{ box-sizing:border-box; margin:0; padding:0; font-family:sans-serif; }}
    .dates {{ display:grid; grid-template-columns:repeat(7,1fr); gap:4px; margin-bottom:10px; }}
    .date {{ font-size:9px; padding:6px 2px; text-align:center; border-radius:6px; background:#e5e7eb; cursor:pointer; }}
    .date.sel {{ background:#4f46e5; color:#fff; }}
    .date.d-today {{ border:1px solid #22c55e; }}
    .grid {{ display:grid; grid-template-columns:44px repeat(3,1fr); gap:3px; }}
    .cell {{ height:28px; font-size:9px; display:flex; align-items:center; justify-content:center; border-radius:6px; cursor:pointer; }}
    .header {{ background:#111; color:#fff; font-weight:bold; cursor:default; }}
    .free {{ background:#bbf7d0; color:#166534; }}
    .mine {{ background:#93c5fd; color:#1e3a5f; }}
    .taken {{ background:#e5e7eb; color:#9ca3af; cursor:default; }}
    .tA {{ background:#f3f4f6; }} .tB {{ background:#e0f2fe; }} .tC {{ background:#fef3c7; }} .tD {{ background:#ede9fe; }}
</style></head><body>
    <div class="dates">{date_cells}</div>
    <div class="grid">
        <div class="cell header">Time</div><div class="cell header">T 1</div><div class="cell header">T 2</div><div class="cell header">T 3</div>
        {grid_rows}
    </div>
    <script>
        function go(key, val) {{
            const url = new URL(window.parent.location.href);
            url.searchParams.set(key, val);
            window.parent.location.href = url.href;
        }}
    </script>
</body></html>
"""
components.html(html_code, height=1100, scrolling=True)

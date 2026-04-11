import os
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import streamlit.components.v1 as components

# ================= CONFIG & PERSISTENCE =================
st.set_page_config(page_title="Pool", layout="centered")

USERS_FILE    = "users.csv"
BOOKINGS_FILE = "bookings.csv"

def load_data(file, cols):
    if os.path.exists(file) and os.path.getsize(file) > 0:
        return pd.read_csv(file, dtype=str)
    return pd.DataFrame(columns=cols)

def save_data(df, file):
    df.to_csv(file, index=False)

# Load data into session state so it survives the "rerun" after a button click
if "users_df" not in st.session_state:
    st.session_state.users_df = load_data(USERS_FILE, ["Email","Name","Password","Role"])
if "bookings_df" not in st.session_state:
    st.session_state.bookings_df = load_data(BOOKINGS_FILE, ["User","Name","Date","Table","Time"])

# ================= SESSION STATE =================
for k in ["user","name","role","sel_date","page"]:
    if k not in st.session_state:
        st.session_state[k] = None

if st.session_state.sel_date is None:
    st.session_state.sel_date = str(datetime.now().date())
if st.session_state.page is None:
    st.session_state.page = "Booking"

# ================= URL / QUERY PARAM LOGIC =================
# This is the "Engine" that makes the HTML buttons work
params = st.query_params

if "date" in params:
    st.session_state.sel_date = params["date"]
    st.query_params.clear()
    st.rerun()

if "book" in params:
    t, table = params["book"].split("|", 1)
    new_row = pd.DataFrame([{
        "User": st.session_state.user,
        "Name": st.session_state.name,
        "Date": st.session_state.sel_date,
        "Table": table,
        "Time": t
    }])
    st.session_state.bookings_df = pd.concat([st.session_state.bookings_df, new_row], ignore_index=True)
    save_data(st.session_state.bookings_df, BOOKINGS_FILE)
    st.query_params.clear()
    st.rerun()

if "del" in params:
    t, table = params["del"].split("|", 1)
    df = st.session_state.bookings_df
    st.session_state.bookings_df = df[~((df["Table"]==table) & (df["Time"]==t) & (df["Date"]==st.session_state.sel_date))]
    save_data(st.session_state.bookings_df, BOOKINGS_FILE)
    st.query_params.clear()
    st.rerun()

# ================= LOGIN PAGE =================
if st.session_state.user is None:
    st.title("🏊 Pool Login")
    e = st.text_input("Email").strip()
    p = st.text_input("Password", type="password").strip()
    if st.button("Login", use_container_width=True):
        u_df = st.session_state.users_df
        m = u_df[(u_df["Email"]==e) & (u_df["Password"]==p)]
        if not m.empty:
            st.session_state.user = e
            st.session_state.name = m.iloc[0]["Name"]
            st.session_state.role = m.iloc[0]["Role"]
            st.rerun()
        else:
            st.error("Invalid credentials")
    st.stop()

# ================= SIDEBAR =================
with st.sidebar:
    st.subheader(f"👋 {st.session_state.name}")
    if st.session_state.role == "admin":
        if st.button("📅 Booking Grid"): st.session_state.page = "Booking"; st.rerun()
        if st.button("⚙️ Admin Panel"): st.session_state.page = "Admin"; st.rerun()
    if st.button("🚪 Logout"):
        for k in list(st.session_state.keys()): del st.session_state[k]
        st.rerun()

# ================= ADMIN PANEL =================
if st.session_state.page == "Admin":
    st.title("⚙️ Admin")
    
    # Add User Section
    with st.expander("➕ Add New User", expanded=True):
        new_email = st.text_input("Email")
        new_name = st.text_input("Name")
        new_pass = st.text_input("Password")
        new_role = st.selectbox("Role", ["user", "admin"])
        if st.button("Save User"):
            if new_email and new_name:
                user_add = pd.DataFrame([{"Email":new_email, "Name":new_name, "Password":new_pass, "Role":new_role}])
                st.session_state.users_df = pd.concat([st.session_state.users_df, user_add], ignore_index=True)
                save_data(st.session_state.users_df, USERS_FILE)
                st.success("User added!")
                st.rerun()

    st.write("### Current Users")
    st.dataframe(st.session_state.users_df, use_container_width=True)
    st.stop()

# ================= BOOKING GRID (THE LOOKOUT) =================
today = datetime.now().date()
HOURS = [f"{h:02d}:{m}" for h in range(6,24) for m in ["00","30"]]

# Build Dates
date_cells = ""
for i in range(14):
    d = today + timedelta(days=i)
    d_str = str(d)
    label = f"{d.strftime('%a')}<br>{d.day}"
    if i == 0: label = f"TOD<br>{d.day}"
    
    cls = "date"
    if d_str == st.session_state.sel_date: cls += " sel"
    date_cells += f'<div class="{cls}" onclick="go(\'date\',\'{d_str}\')">{label}</div>'

# Build Rows
grid_rows = ""
for idx, t in enumerate(HOURS):
    band = ["tA","tB","tC","tD"][(idx // 8) % 4]
    grid_rows += f'<div class="cell {band}">{t}</div>'
    for i in range(1, 4):
        table = f"Table {i}"
        match = st.session_state.bookings_df[
            (st.session_state.bookings_df["Table"]==table) & 
            (st.session_state.bookings_df["Time"]==t) & 
            (st.session_state.bookings_df["Date"]==st.session_state.sel_date)
        ]
        if not match.empty:
            is_me = match.iloc[0]["User"] == st.session_state.user
            name_tag = match.iloc[0]["Name"][:3]
            if is_me:
                grid_rows += f'<div class="cell mine" onclick="go(\'del\',\'{t}|{table}\')">✕ {name_tag}</div>'
            else:
                grid_rows += f'<div class="cell taken">{name_tag}</div>'
        else:
            grid_rows += f'<div class="cell free" onclick="go(\'book\',\'{t}|{table}\')">+</div>'

# HTML Layout
html_code = f"""
<!DOCTYPE html>
<html>
<head>
<style>
    body {{ font-family: sans-serif; margin: 0; padding-top: 10px; }}
    .dates {{
        display: grid;
        grid-template-columns: repeat(7, 1fr);
        gap: 4px;
        position: sticky; top: 0; background: white; padding-bottom: 10px; z-index: 10;
    }}
    .date {{
        font-size: 10px; padding: 8px 2px; text-align: center; 
        background: #f0f0f0; border-radius: 6px; cursor: pointer;
    }}
    .date.sel {{ background: #4f46e5; color: white; font-weight: bold; }}
    
    .grid {{ display: grid; grid-template-columns: 50px repeat(3, 1fr); gap: 4px; }}
    .cell {{
        height: 32px; font-size: 10px; display: flex; align-items: center; 
        justify-content: center; border-radius: 4px; cursor: pointer;
    }}
    .header {{ background: #111; color: #fff; font-weight: bold; cursor: default; }}
    .free {{ background: #dcfce7; color: #166534; }}
    .taken {{ background: #f3f4f6; color: #9ca3af; cursor: default; }}
    .mine {{ background: #dbeafe; color: #1e40af; border: 1px solid #3b82f6; }}
    .tA {{ background: #fafafa; }} .tB {{ background: #f0f9ff; }}
</style>
</head>
<body>
    <div class="dates">{date_cells}</div>
    <div class="grid">
        <div class="cell header">Time</div>
        <div class="cell header">T1</div><div class="cell header">T2</div><div class="cell header">T3</div>
        {grid_rows}
    </div>
    <script>
        function go(key, val) {{
            const url = new URL(window.parent.location.href);
            url.searchParams.set(key, val);
            window.parent.location.href = url.href;
        }}
    </script>
</body>
</html>
"""

st.markdown(f"### 🗓️ {st.session_state.sel_date}")
components.html(html_code, height=800, scrolling=True)

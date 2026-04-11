import os
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import streamlit.components.v1 as components

# ================= 1. SETUP & DATA PERSISTENCE =================
st.set_page_config(page_title="Pool", layout="centered")

# CSS to ensure the Streamlit container doesn't hide the top
st.markdown("""
<style>
    .block-container { max-width:340px !important; padding-top:0rem !important; }
    iframe { margin-top: 5px; }
</style>
""", unsafe_allow_html=True)

USERS_FILE = "users.csv"
BOOKINGS_FILE = "bookings.csv"

def load_data(file, cols):
    if os.path.exists(file) and os.path.getsize(file) > 0:
        return pd.read_csv(file, dtype=str)
    return pd.DataFrame(columns=cols)

def save_data(df, file):
    df.to_csv(file, index=False)

# Crucial: Load data into session state so it's globally available
if "users" not in st.session_state:
    st.session_state.users = load_data(USERS_FILE, ["Email","Name","Password","Role"])
if "bookings" not in st.session_state:
    st.session_state.bookings = load_data(BOOKINGS_FILE, ["User","Name","Date","Table","Time"])

# Init State
for k in ["user","name","role","sel_date","page"]:
    if k not in st.session_state: st.session_state[k] = None

if not st.session_state.sel_date: st.session_state.sel_date = str(datetime.now().date())
if not st.session_state.page: st.session_state.page = "Booking"

# ================= 2. THE ENGINE (BUTTON CLICKS) =================
# This handles the clicks sent from the HTML
p = st.query_params

if "date" in p:
    st.session_state.sel_date = p["date"]
    st.query_params.clear()
    st.rerun()

if "book" in p:
    t, table = p["book"].split("|", 1)
    df = st.session_state.bookings
    # Check if slot is empty
    if df[(df["Table"]==table) & (df["Time"]==t) & (df["Date"]==st.session_state.sel_date)].empty:
        new_row = pd.DataFrame([{
            "User": st.session_state.user, 
            "Name": st.session_state.name, 
            "Date": st.session_state.sel_date, 
            "Table": table, 
            "Time": t
        }])
        st.session_state.bookings = pd.concat([df, new_row], ignore_index=True)
        save_data(st.session_state.bookings, BOOKINGS_FILE)
    st.query_params.clear()
    st.rerun()

if "del" in p:
    t, table = p["del"].split("|", 1)
    df = st.session_state.bookings
    # Logic: Admin can delete anything. User only their own.
    mask = (df["Table"]==table) & (df["Time"]==t) & (df["Date"]==st.session_state.sel_date)
    if st.session_state.role != "admin":
        mask = mask & (df["User"] == st.session_state.user)
    
    st.session_state.bookings = df[~mask]
    save_data(st.session_state.bookings, BOOKINGS_FILE)
    st.query_params.clear()
    st.rerun()

# ================= 3. LOGIN & SIDEBAR =================
if st.session_state.user is None:
    st.title("🏊 Pool Login")
    e = st.text_input("Email").strip().lower()
    p_in = st.text_input("Password", type="password").strip()
    if st.button("Login", use_container_width=True):
        u_db = st.session_state.users
        match = u_db[(u_db["Email"]==e) & (u_db["Password"]==p_in)]
        if not match.empty:
            st.session_state.user = e
            st.session_state.name = match.iloc[0]["Name"]
            st.session_state.role = match.iloc[0]["Role"]
            st.rerun()
        else: st.error("Wrong Email/Pass")
    st.stop()

with st.sidebar:
    st.markdown(f"### 👤 {st.session_state.name}")
    if st.session_state.role == "admin":
        if st.button("📅 Booking Grid"): st.session_state.page = "Booking"; st.rerun()
        if st.button("⚙️ Admin Panel"): st.session_state.page = "Admin"; st.rerun()
    if st.button("🚪 Logout"):
        for k in list(st.session_state.keys()): del st.session_state[k]
        st.rerun()

# ================= 4. ADMIN PANEL & STATS =================
if st.session_state.page == "Admin":
    st.title("⚙️ Admin")
    t1, t2 = st.tabs(["Users", "Stats"])
    
    with t1:
        with st.form("Add User"):
            ae, an, ap = st.text_input("Email"), st.text_input("Name"), st.text_input("Pass")
            ar = st.selectbox("Role", ["user", "admin"])
            if st.form_submit_button("Save User"):
                new_u = pd.DataFrame([{"Email":ae.lower(),"Name":an,"Password":ap,"Role":ar}])
                st.session_state.users = pd.concat([st.session_state.users, new_u], ignore_index=True)
                save_data(st.session_state.users, USERS_FILE)
                st.success("Saved!")
                st.rerun()
        st.dataframe(st.session_state.users, use_container_width=True)

    with t2:
        df_b = st.session_state.bookings
        if not df_b.empty:
            st.metric("Total Bookings", len(df_b))
            st.bar_chart(df_b["Name"].value_counts())
        else: st.write("No stats yet.")
    st.stop()

# ================= 5. BOOKING GRID (OUTLOOK) =================
today = datetime.now().date()
HOURS = [f"{h:02d}:{m}" for h in range(6,24) for m in ["00","30"]]

date_cells = ""
for i in range(14):
    d = today + timedelta(days=i)
    d_str = str(d)
    day_name = "TOD" if i==0 else ("TOM" if i==1 else d.strftime('%a').upper())
    cls = "date"
    if i == 0: cls += " d-today"
    if d_str == st.session_state.sel_date: cls += " sel"
    date_cells += f'<div class="{cls}" onclick="go(\'date\',\'{d_str}\')">{day_name}<br>{d.day}</div>'

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
            # Admin can delete anything. User sees 'mine' only for their own.
            is_owner = b_user == st.session_state.user
            if is_owner or st.session_state.role == "admin":
                grid_rows += f'<div class="cell mine" onclick="go(\'del\',\'{t}|{table}\')">✕ {b_name}</div>'
            else:
                grid_rows += f'<div class="cell taken">{b_name}</div>'
        else:
            grid_rows += f'<div class="cell free" onclick="go(\'book\',\'{t}|{table}\')">+</div>'

html_code = f"""
<!DOCTYPE html><html><head>
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
<style>
    * {{ box-sizing:border-box; margin:0; padding:0; font-family:sans-serif; }}
    body {{ background: white; padding: 15px 5px 5px 5px; }} /* Padding for top visibility */
    .dates {{ display:grid; grid-template-columns:repeat(7,1fr); gap:4px; margin-bottom:15px; }}
    .date {{ font-size:9px; padding:8px 2px; text-align:center; border-radius:6px; background:#f3f4f6; cursor:pointer; line-height:1.2; }}
    .date.sel {{ background:#4f46e5 !important; color:#fff !important; font-weight:bold; }}
    .date.d-today {{ border:1.5px solid #22c55e; color:#111; }}
    .grid {{ display:grid; grid-template-columns:46px repeat(3,1fr); gap:4px; }}
    .cell {{ height:32px; font-size:10px; display:flex; align-items:center; justify-content:center; border-radius:6px; cursor:pointer; transition: 0.1s; }}
    .header {{ background:#111; color:#fff; font-weight:bold; cursor:default; }}
    .free {{ background:#dcfce7; color:#166534; border:1px solid #bbf7d0; }}
    .mine {{ background:#dbeafe; color:#1e3a5f; border:1.5px solid #3b82f6; font-weight:bold; }}
    .taken {{ background:#f3f4f6; color:#9ca3af; cursor:default; }}
    .tA {{ background:#fafafa; }} .tB {{ background:#f0f9ff; }} .tC {{ background:#fffbeb; }} .tD {{ background:#f5f3ff; }}
</style></head><body>
    <div class="dates">{date_cells}</div>
    <div class="grid">
        <div class="cell header">Time</div><div class="cell header">T1</div><div class="cell header">T2</div><div class="cell header">T3</div>
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

st.write(f"### 🗓️ {st.session_state.sel_date}")
components.html(html_code, height=1100, scrolling=True)

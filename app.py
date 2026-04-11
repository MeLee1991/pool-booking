import os
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import streamlit.components.v1 as components

# ================= 1. SETUP & PERSISTENCE =================
st.set_page_config(page_title="Pool", layout="centered")

# Visual tweaks to ensure the grid fits mobile screens
st.markdown("""
<style>
    .block-container { max-width:340px !important; padding-top:1rem; }
    [data-testid="stMetricValue"] { font-size: 1.5rem !important; }
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

# Initialize data in session state
if "users" not in st.session_state:
    st.session_state.users = load_data(USERS_FILE, ["Email","Name","Password","Role"])
if "bookings" not in st.session_state:
    st.session_state.bookings = load_data(BOOKINGS_FILE, ["User","Name","Date","Table","Time"])

for k in ["user","name","role","sel_date","page"]:
    if k not in st.session_state: st.session_state[k] = None

if not st.session_state.sel_date: st.session_state.sel_date = str(datetime.now().date())
if not st.session_state.page: st.session_state.page = "Booking"

# ================= 2. THE COMMAND ENGINE =================
# Since query params can be finicky, we check them and immediately update state
p = st.query_params
if "date" in p:
    st.session_state.sel_date = p["date"]
    st.query_params.clear()
    st.rerun()

if "book" in p:
    t, table = p["book"].split("|", 1)
    df = st.session_state.bookings
    if df[(df["Table"]==table) & (df["Time"]==t) & (df["Date"]==st.session_state.sel_date)].empty:
        new_row = pd.DataFrame([{"User": st.session_state.user, "Name": st.session_state.name, 
                                 "Date": st.session_state.sel_date, "Table": table, "Time": t}])
        st.session_state.bookings = pd.concat([df, new_row], ignore_index=True)
        save_data(st.session_state.bookings, BOOKINGS_FILE)
    st.query_params.clear()
    st.rerun()

if "del" in p:
    t, table = p["del"].split("|", 1)
    df = st.session_state.bookings
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
    p_in = st.text_input("Password", type="password")
    if st.button("Login", use_container_width=True):
        u = st.session_state.users
        m = u[(u["Email"]==e) & (u["Password"]==p_in)]
        if not m.empty:
            st.session_state.user, st.session_state.name, st.session_state.role = e, m.iloc[0]["Name"], m.iloc[0]["Role"]
            st.rerun()
        else: st.error("Wrong credentials")
    st.stop()

with st.sidebar:
    st.write(f"**👤 {st.session_state.name}**")
    if st.session_state.role == "admin":
        if st.button("📅 Booking Grid", use_container_width=True): st.session_state.page = "Booking"; st.rerun()
        if st.button("⚙️ Admin Panel", use_container_width=True): st.session_state.page = "Admin"; st.rerun()
    if st.button("🚪 Logout", use_container_width=True):
        for k in list(st.session_state.keys()): del st.session_state[k]
        st.rerun()

# ================= 4. ADMIN PAGE (WITH STATS) =================
if st.session_state.page == "Admin":
    st.title("⚙️ Admin Panel")
    t1, t2 = st.tabs(["👥 User Management", "📊 Booking Stats"])
    
    with t1:
        with st.expander("➕ Add New User", expanded=False):
            ae = st.text_input("New Email").strip().lower()
            an = st.text_input("New Name")
            ap = st.text_input("New Password")
            ar = st.selectbox("Role", ["user", "admin"])
            if st.button("Create User", use_container_width=True):
                if ae and an:
                    new_u = pd.DataFrame([{"Email":ae,"Name":an,"Password":ap,"Role":ar}])
                    st.session_state.users = pd.concat([st.session_state.users, new_u], ignore_index=True)
                    save_data(st.session_state.users, USERS_FILE)
                    st.success(f"User {an} created!")
                    st.rerun()
        st.dataframe(st.session_state.users, use_container_width=True)

    with t2:
        df_b = st.session_state.bookings
        if not df_b.empty:
            col1, col2 = st.columns(2)
            col1.metric("Total Bookings", len(df_b))
            col2.metric("Active Users", df_b["User"].nunique())
            
            st.write("### Bookings by Table")
            st.bar_chart(df_b["Table"].value_counts())
            
            st.write("### Most Active Players")
            st.bar_chart(df_b["Name"].value_counts().head(5))
        else:
            st.info("No bookings recorded yet.")
    st.stop()

# ================= 5. BOOKING GRID (THE LOOKOUT) =================
today = datetime.now().date()
HOURS = [f"{h:02d}:{m}" for h in range(6,24) for m in ["00","30"]]

# Build 14-day grid (2 rows of 7)
date_cells = ""
for i in range(14):
    d = today + timedelta(days=i)
    d_str = str(d)
    day_name = "TOD" if i==0 else ("TOM" if i==1 else d.strftime('%a').upper())
    label = f"{day_name}<br>{d.day}"
    cls = "date"
    if i==0: cls += " d-today"
    if d_str == st.session_state.sel_date: cls += " sel"
    date_cells += f'<div class="{cls}" onclick="go(\'date\',\'{d_str}\')">{label}</div>'

# Build Slots
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
            # Admin delete access or user's own booking
            if b_user == st.session_state.user or st.session_state.role == "admin":
                grid_rows += f'<div class="cell mine" onclick="go(\'del\',\'{t}|{table}\')">✕ {b_name}</div>'
            else:
                grid_rows += f'<div class="cell taken">{b_name}</div>'
        else:
            grid_rows += f'<div class="cell free" onclick="go(\'book\',\'{t}|{table}\')">+</div>'

html_code = f"""
<!DOCTYPE html><html><head>
<meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=no">
<style>
    * {{ box-sizing:border-box; margin:0; padding:0; font-family:sans-serif; }}
    body {{ background: white; padding-top: 5px; }}
    .dates {{ display:grid; grid-template-columns:repeat(7,1fr); gap:4px; margin-bottom:12px; }}
    .date {{ font-size:9px; padding:6px 2px; text-align:center; border-radius:6px; background:#f3f4f6; cursor:pointer; color:#374151; }}
    .date.sel {{ background:#4f46e5; color:#fff; font-weight:bold; }}
    .date.d-today {{ border:1.5px solid #22c55e; }}
    .grid {{ display:grid; grid-template-columns:46px repeat(3,1fr); gap:4px; }}
    .cell {{ height:30px; font-size:10px; display:flex; align-items:center; justify-content:center; border-radius:6px; cursor:pointer; }}
    .header {{ background:#111; color:#fff; font-weight:bold; cursor:default; }}
    .free {{ background:#dcfce7; color:#166534; border:1px solid #bbf7d0; }}
    .mine {{ background:#dbeafe; color:#1e3a5f; border:1px solid #3b82f6; font-weight:bold; }}
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

st.write(f"### 📅 {st.session_state.sel_date}")
components.html(html_code, height=1000, scrolling=True)

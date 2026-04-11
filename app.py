import os
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import streamlit.components.v1 as components

# ================= PERSISTENCE =================
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

# ================= STATE MANAGEMENT =================
for k in ["user","name","role","sel_date","page"]:
    if k not in st.session_state: st.session_state[k] = None

if not st.session_state.sel_date: st.session_state.sel_date = str(datetime.now().date())
if not st.session_state.page: st.session_state.page = "Booking"

# ================= THE CURE FOR BUTTONS =================
# We read the query params, execute the logic, THEN CLEAR them 
# and rerun to ensure the app state is fresh.
query = st.query_params

if "act" in query:
    action = query["act"]
    val = query["val"]
    
    if action == "date":
        st.session_state.sel_date = val
    
    elif action == "book":
        t, table = val.split("|", 1)
        df = st.session_state.bookings
        if df[(df["Table"]==table) & (df["Time"]==t) & (df["Date"]==st.session_state.sel_date)].empty:
            new_row = pd.DataFrame([{"User": st.session_state.user, "Name": st.session_state.name, 
                                     "Date": st.session_state.sel_date, "Table": table, "Time": t}])
            st.session_state.bookings = pd.concat([st.session_state.bookings, new_row], ignore_index=True)
            save_data(st.session_state.bookings, BOOKINGS_FILE)
            
    elif action == "del":
        t, table = val.split("|", 1)
        df = st.session_state.bookings
        mask = (df["Table"]==table) & (df["Time"]==t) & (df["Date"]==st.session_state.sel_date)
        if st.session_state.role != "admin":
            mask = mask & (df["User"] == st.session_state.user)
        st.session_state.bookings = df[~mask]
        save_data(st.session_state.bookings, BOOKINGS_FILE)

    st.query_params.clear()
    st.rerun()

# ================= UI / LOGIN =================
if st.session_state.user is None:
    st.title("🏊 Pool Login")
    e = st.text_input("Email").lower().strip()
    p = st.text_input("Password", type="password")
    if st.button("Login"):
        u_db = st.session_state.users
        m = u_db[(u_db["Email"]==e) & (u_db["Password"]==p)]
        if not m.empty:
            st.session_state.user, st.session_state.name, st.session_state.role = e, m.iloc[0]["Name"], m.iloc[0]["Role"]
            st.rerun()
    st.stop()

# ================= ADMIN PAGE =================
if st.session_state.page == "Admin":
    st.title("⚙️ Admin")
    tab1, tab2 = st.tabs(["Users", "Stats"])
    with tab1:
        with st.form("add_u"):
            ne, nn, np, nr = st.text_input("Email"), st.text_input("Name"), st.text_input("Pass"), st.selectbox("Role", ["user","admin"])
            if st.form_submit_button("Add"):
                new_user = pd.DataFrame([{"Email":ne.lower(),"Name":nn,"Password":np,"Role":nr}])
                st.session_state.users = pd.concat([st.session_state.users, new_user], ignore_index=True)
                save_data(st.session_state.users, USERS_FILE)
                st.rerun()
        st.dataframe(st.session_state.users)
    with tab2:
        st.metric("Total Bookings", len(st.session_state.bookings))
        st.bar_chart(st.session_state.bookings["Name"].value_counts())
    if st.button("Back"): 
        st.session_state.page = "Booking"
        st.rerun()
    st.stop()

# ================= BOOKING GRID =================
today = datetime.now().date()
HOURS = [f"{h:02d}:{m}" for h in range(6,24) for m in ["00","30"]]

date_cells = ""
for i in range(14):
    d = today + timedelta(days=i)
    d_str = str(d)
    cls = "date" + (" sel" if d_str == st.session_state.sel_date else "") + (" d-today" if i==0 else "")
    label = f"{'TOD' if i==0 else ('TOM' if i==1 else d.strftime('%a').upper())}<br>{d.day}"
    date_cells += f'<div class="{cls}" onclick="send(\'date\',\'{d_str}\')">{label}</div>'

grid_rows = ""
for idx, t in enumerate(HOURS):
    band = ["tA","tB","tC","tD"][(idx // 8) % 4]
    grid_rows += f'<div class="cell {band}">{t}</div>'
    for i in range(1, 4):
        tbl = f"Table {i}"
        match = st.session_state.bookings[(st.session_state.bookings["Table"]==tbl) & 
                                          (st.session_state.bookings["Time"]==t) & 
                                          (st.session_state.bookings["Date"]==st.session_state.sel_date)]
        if not match.empty:
            is_me = match.iloc[0]["User"] == st.session_state.user or st.session_state.role == "admin"
            grid_rows += f'<div class="cell {"mine" if is_me else "taken"}" {"onclick=\"send(\'del\',\''+t+'|'+tbl+'\')\"" if is_me else ""}>{match.iloc[0]["Name"][:3]}</div>'
        else:
            grid_rows += f'<div class="cell free" onclick="send(\'book\',\'{t}|{tbl}\')">+</div>'

html_code = f"""
<!DOCTYPE html><html><head><style>
    * {{ box-sizing:border-box; font-family:sans-serif; }}
    body {{ padding: 20px 5px; }}
    .dates {{ display:grid; grid-template-columns:repeat(7,1fr); gap:4px; margin-bottom:15px; }}
    .date {{ font-size:9px; padding:8px 2px; text-align:center; border-radius:6px; background:#eee; cursor:pointer; }}
    .date.sel {{ background:#4f46e5; color:#fff; }}
    .grid {{ display:grid; grid-template-columns:46px repeat(3,1fr); gap:4px; }}
    .cell {{ height:32px; font-size:10px; display:flex; align-items:center; justify-content:center; border-radius:6px; cursor:pointer; }}
    .header {{ background:#111; color:#fff; font-weight:bold; }}
    .free {{ background:#dcfce7; color:#166534; }}
    .mine {{ background:#93c5fd; color:#1e3a5f; font-weight:bold; }}
    .taken {{ background:#f3f4f6; color:#9ca3af; cursor:default; }}
    .tA {{ background:#fafafa; }} .tB {{ background:#f0f9ff; }}
</style></head><body>
    <div class="dates">{date_cells}</div>
    <div class="grid">
        <div class="cell header">Time</div><div class="cell header">T1</div><div class="cell header">T2</div><div class="cell header">T3</div>
        {grid_rows}
    </div>
    <script>
        function send(act, val) {{
            const url = new URL(window.parent.location.href);
            url.searchParams.set("act", act);
            url.searchParams.set("val", val);
            window.parent.location.href = url.href;
        }}
    </script>
</body></html>
"""

st.sidebar.button("⚙️ Admin", on_click=lambda: st.session_state.update({"page":"Admin"}))
st.sidebar.button("🚪 Logout", on_click=lambda: st.session_state.clear())

components.html(html_code, height=1200)

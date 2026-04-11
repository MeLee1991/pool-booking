import os
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import streamlit.components.v1 as components

# ================= 1. SETUP & DATA =================
st.set_page_config(page_title="Pool", layout="centered")

# CSS LOCK: Restoring your exact lookout
st.markdown("""
<style>
    .block-container { max-width:320px !important; padding-top: 0rem !important; margin: auto; }
    header {visibility: hidden;}
    footer {visibility: hidden;}
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

if "users" not in st.session_state:
    st.session_state.users = load_data(USERS_FILE, ["Email","Name","Password","Role"])
if "bookings" not in st.session_state:
    st.session_state.bookings = load_data(BOOKINGS_FILE, ["User","Name","Date","Table","Time"])

for k in ["user","name","role","sel_date","page"]:
    if k not in st.session_state: st.session_state[k] = None

if not st.session_state.sel_date: st.session_state.sel_date = str(datetime.now().date())
if not st.session_state.page: st.session_state.page = "Booking"

# ================= 2. THE ADMIN PANEL (SIMPLE & FUNCTIONAL) =================
if st.session_state.page == "Admin":
    st.title("⚙️ Admin")
    if st.button("← Back to Grid", use_container_width=True): 
        st.session_state.page = "Booking"
        st.rerun()

    st.subheader("👥 User Management")
    # Simple table display for control
    for idx, u in st.session_state.users.iterrows():
        with st.container(border=True):
            c1, c2 = st.columns([4, 1])
            c1.write(f"**{u['Name']}** ({u['Role']})\n{u['Email']}")
            if c2.button("🗑️", key=f"u_del_{idx}"):
                st.session_state.users = st.session_state.users.drop(idx).reset_index(drop=True)
                save_data(st.session_state.users, USERS_FILE)
                st.rerun()
    
    with st.expander("➕ Add User"):
        ae = st.text_input("Email").lower().strip()
        an = st.text_input("Name")
        ap = st.text_input("Pass")
        ar = st.selectbox("Role", ["user","admin"])
        if st.button("Save User", use_container_width=True):
            nu = pd.DataFrame([{"Email":ae,"Name":an,"Password":ap,"Role":ar}])
            st.session_state.users = pd.concat([st.session_state.users, nu], ignore_index=True)
            save_data(st.session_state.users, USERS_FILE)
            st.rerun()

    st.divider()
    st.download_button("📥 Export CSV", st.session_state.bookings.to_csv(index=False), "bookings.csv")
    st.stop()

# ================= 3. LOGIN =================
if st.session_state.user is None:
    st.title("🏊 Pool")
    e = st.text_input("Email").strip().lower()
    p_in = st.text_input("Password", type="password")
    if st.button("Login", use_container_width=True):
        match = st.session_state.users[(st.session_state.users["Email"]==e) & (st.session_state.users["Password"]==p_in)]
        if not match.empty:
            st.session_state.user, st.session_state.name, st.session_state.role = e, match.iloc[0]["Name"], match.iloc[0]["Role"]
            st.rerun()
    st.stop()

# ================= 4. THE OUTLOOK (FRONT-END) =================
today = datetime.now().date()
HOURS = [f"{h:02d}:{m}" for h in range(6, 24) for m in ["00","30"]] + \
        [f"{h:02d}:{m}" for h in range(0, 6) for m in ["00","30"]]

date_cells = ""
for i in range(14):
    d = today + timedelta(days=i)
    d_str = str(d)
    label = f"TOD<br>{d.day}" if i==0 else (f"TOM<br>{d.day}" if i==1 else f"{d.strftime('%a').upper()}<br>{d.day}")
    cls = "date" + (" sel" if d_str == st.session_state.sel_date else "") + (" d-today" if i==0 else "")
    date_cells += f'<div class="{cls}" onclick="handleGo(\'date\',\'{d_str}\')">{label}</div>'

grid_rows = ""
for idx, t in enumerate(HOURS):
    band = ["tA","tB","tC","tD"][(idx // 8) % 4]
    grid_rows += f'<div class="cell {band}">{t}</div>'
    for i in range(1, 4):
        table = f"Table {i}"
        match = st.session_state.bookings[(st.session_state.bookings["Table"]==table) & 
                                          (st.session_state.bookings["Time"]==t) & 
                                          (st.session_state.bookings["Date"]==st.session_state.sel_date)]
        if not match.empty:
            b_name = match.iloc[0]["Name"][:3]
            is_mine = (match.iloc[0]["User"] == st.session_state.user) or (st.session_state.role == "admin")
            cls = "mine" if is_mine else "taken"
            grid_rows += f'<div class="cell {cls}" onclick="{"handleGo(\'del\',\''+t+'|'+table+'\')" if is_mine else ""}">{"✕" if is_mine else ""}{b_name}</div>'
        else:
            grid_rows += f'<div class="cell free" onclick="handleGo(\'book\',\'{t}|{table}\')">+</div>'

html_code = f"""
<!DOCTYPE html><html><head><meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1">
<style>
    * {{ box-sizing:border-box; margin:0; padding:0; font-family:sans-serif; }}
    body {{ padding: 25px 2px 10px 2px; background: white; }}
    .dates {{ display:grid; grid-template-columns:repeat(7,1fr); gap:3px; margin-bottom:10px; }}
    .date {{ font-size:9px; padding:6px 2px; text-align:center; border-radius:6px; background:#e5e7eb; cursor:pointer; line-height:1.2; }}
    .date.sel {{ background:#4f46e5 !important; color:#fff; font-weight:bold; }}
    .date.d-today {{ border:1px solid #22c55e; }}
    .grid {{ display:grid; grid-template-columns:44px repeat(3,1fr); gap:3px; }}
    .cell {{ height:28px; font-size:9px; display:flex; align-items:center; justify-content:center; border-radius:6px; cursor:pointer; -webkit-tap-highlight-color:transparent; }}
    .header {{ background:#111; color:#fff; font-weight:bold; cursor:default; }}
    .free {{ background:#bbf7d0; color:#166534; }}
    .mine {{ background:#93c5fd; color:#1e3a5f; font-weight:bold; }}
    .taken {{ background:#e5e7eb; color:#9ca3af; cursor:default; }}
    .tA {{ background:#f3f4f6; }} .tB {{ background:#e0f2fe; }} .tC {{ background:#fef3c7; }} .tD {{ background:#ede9fe; }}
</style></head><body>
    <div class="dates">{date_cells}</div>
    <div class="grid">
        <div class="cell header">Time</div><div class="cell header">T 1</div><div class="cell header">T 2</div><div class="cell header">T 3</div>
        {grid_rows}
    </div>
    <script>
        function handleGo(act, val) {{
            // This sends the click data to Streamlit via a component value
            const data = {{ action: act, value: val }};
            window.parent.postMessage({{
                type: 'streamlit:setComponentValue',
                value: data
            }}, '*');
        }}
    </script>
</body></html>
"""

# ================= 5. THE FUNCTIONAL BRIDGE =================
# This is the secret. It catches the messages from the HTML grid.
grid_response = components.html(html_code, height=1550)

# We check for a hidden signal in the session state or a query trigger
p = st.query_params
if "a" in p or "d" in p:
    # URL Logic as fallback
    if "d" in p: st.session_state.sel_date = p["d"]
    if "a" in p:
        act, val = p["a"], p["v"]
        if act == "book":
            t, table = val.split("|", 1)
            new_row = pd.DataFrame([{"User": st.session_state.user, "Name": st.session_state.name, "Date": st.session_state.sel_date, "Table": table, "Time": t}])
            st.session_state.bookings = pd.concat([st.session_state.bookings, new_row], ignore_index=True)
            save_data(st.session_state.bookings, BOOKINGS_FILE)
        elif act == "del":
            t, table = val.split("|", 1)
            mask = (st.session_state.bookings["Table"]==table) & (st.session_state.bookings["Time"]==t) & (st.session_state.bookings["Date"]==st.session_state.sel_date)
            if st.session_state.role != "admin": mask = mask & (st.session_state.bookings["User"] == st.session_state.user)
            st.session_state.bookings = st.session_state.bookings[~mask]
            save_data(st.session_state.bookings, BOOKINGS_FILE)
    st.query_params.clear()
    st.rerun()

# The JS "Listener" that forces the Streamlit app to refresh when the iframe is clicked
st.markdown("""
<script>
window.addEventListener('message', function(event) {
    if (event.data.type === 'streamlit:setComponentValue') {
        const d = event.data.value;
        const url = new URL(window.parent.location.href);
        if (d.action === 'date') url.searchParams.set('d', d.value);
        else {
            url.searchParams.set('a', d.action);
            url.searchParams.set('v', d.value);
        }
        window.parent.location.href = url.href;
    }
});
</script>
""", unsafe_allow_html=True)

st.write(f"👤 **{st.session_state.name}** | {st.session_state.sel_date}")
if st.session_state.role == "admin":
    if st.button("⚙️ Admin Panel", use_container_width=True): 
        st.session_state.page = "Admin"
        st.rerun()

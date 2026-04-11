import os
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import streamlit.components.v1 as components

st.set_page_config(page_title="Pool", layout="centered")

# ================= DATA =================
USERS_FILE    = "users.csv"
BOOKINGS_FILE = "bookings.csv"

def load_data(file, cols):
    if os.path.exists(file):
        return pd.read_csv(file, dtype=str)
    return pd.DataFrame(columns=cols)

def save_data(df, file):
    df.to_csv(file, index=False)

users    = load_data(USERS_FILE,    ["Email","Name","Password","Role"])
bookings = load_data(BOOKINGS_FILE, ["User","Name","Date","Table","Time"])

# ================= SESSION =================
for k in ["user","name","role","sel_date","page"]:
    if k not in st.session_state:
        st.session_state[k] = None

if st.session_state.sel_date is None:
    st.session_state.sel_date = str(datetime.now().date())
if st.session_state.page is None:
    st.session_state.page = "Booking"

# ================= LOGIN =================
if st.session_state.user is None:
    st.title("🏊 Pool")
    e = st.text_input("Email")
    p = st.text_input("Password", type="password")
    if st.button("Login", use_container_width=True):
        m = users[(users["Email"]==e) & (users["Password"]==p)]
        if not m.empty:
            st.session_state.user     = e
            st.session_state.name     = m.iloc[0]["Name"]
            st.session_state.role     = m.iloc[0]["Role"]
            st.session_state.page     = "Booking"
            st.rerun()
        else:
            st.error("Wrong email or password")
    st.stop()

# ================= QUERY PARAM ACTIONS =================
# These are set by JS via parent.window.location.href
p = st.query_params

if "date" in p:
    st.session_state.sel_date = p["date"]
    st.query_params.clear()
    st.rerun()

if "book" in p:
    t, table = p["book"].split("|", 1)
    exists = bookings[
        (bookings["Table"]==table) &
        (bookings["Time"]==t) &
        (bookings["Date"]==st.session_state.sel_date)
    ]
    if exists.empty:
        row = pd.DataFrame([{
            "User":  st.session_state.user,
            "Name":  st.session_state.name,
            "Date":  st.session_state.sel_date,
            "Table": table,
            "Time":  t
        }])
        bookings = pd.concat([bookings, row], ignore_index=True)
        save_data(bookings, BOOKINGS_FILE)
    st.query_params.clear()
    st.rerun()

if "del" in p:
    t, table = p["del"].split("|", 1)
    bookings = bookings[
        ~((bookings["Table"]==table) &
          (bookings["Time"]==t) &
          (bookings["Date"]==st.session_state.sel_date))
    ]
    save_data(bookings, BOOKINGS_FILE)
    st.query_params.clear()
    st.rerun()

if "nav" in p:
    st.session_state.page = p["nav"]
    st.query_params.clear()
    st.rerun()

# ================= SIDEBAR =================
with st.sidebar:
    st.markdown(f"**👤 {st.session_state.name}**")
    st.caption(f"Role: {st.session_state.role}")
    st.divider()
    if st.session_state.role == "admin":
        if st.button("📅 Booking", use_container_width=True):
            st.session_state.page = "Booking"
            st.rerun()
        if st.button("⚙️ Admin Panel", use_container_width=True):
            st.session_state.page = "Admin"
            st.rerun()
        st.divider()
    if st.button("🚪 Logout", use_container_width=True):
        for k in list(st.session_state.keys()):
            del st.session_state[k]
        st.rerun()

# ================= GLOBAL CSS =================
st.markdown("""
<style>
.block-container { max-width:310px !important; margin:auto; padding-top:0.5rem; }
</style>
""", unsafe_allow_html=True)

# ================= ADMIN PAGE =================
if st.session_state.page == "Admin":
    st.title("⚙️ Admin Panel")
    tab1, tab2 = st.tabs(["👥 Users", "📋 Stats"])

    with tab1:
        if not users.empty:
            st.dataframe(users[["Email","Name","Role"]], use_container_width=True)
        st.markdown("**➕ Add user**")
        em = st.text_input("Email",    key="a_em")
        nm = st.text_input("Name",     key="a_nm")
        pw = st.text_input("Password", key="a_pw")
        rl = st.selectbox("Role", ["user","admin"], key="a_rl")
        if st.button("Add User", use_container_width=True):
            if em and nm and pw:
                new = pd.DataFrame([{"Email":em,"Name":nm,"Password":pw,"Role":rl}])
                users = pd.concat([users, new], ignore_index=True)
                save_data(users, USERS_FILE)
                st.success(f"✅ Added {nm}")
                st.rerun()
            else:
                st.warning("Fill all fields")
        if not users.empty:
            st.markdown("**🗑️ Delete user**")
            del_user = st.selectbox("Select", users["Email"], key="a_del")
            if st.button("Delete User", use_container_width=True):
                users = users[users["Email"] != del_user]
                save_data(users, USERS_FILE)
                st.success("Deleted")
                st.rerun()

    with tab2:
        if bookings.empty:
            st.info("No bookings yet.")
        else:
            st.dataframe(bookings, use_container_width=True)
            st.markdown("**Bookings per user**")
            top = bookings["Name"].value_counts().reset_index()
            top.columns = ["Name","Count"]
            st.bar_chart(top.set_index("Name"))
            st.markdown("**Bookings per table**")
            tbl = bookings["Table"].value_counts().reset_index()
            tbl.columns = ["Table","Count"]
            st.bar_chart(tbl.set_index("Table"))
        st.download_button("⬇️ Download CSV", bookings.to_csv(index=False),
                           "bookings.csv", use_container_width=True)
    st.stop()

# ================= BOOKING PAGE =================
today = datetime.now().date()
HOURS = [f"{h:02d}:{m}" for h in range(6,24) for m in ["00","30"]]

# Build date cells
date_cells = ""
for i in range(14):
    d     = today + timedelta(days=i)
    d_str = str(d)
    if i == 0:
        label = f"TOD<br>{d.day}"
        cls   = "date d-today"
    elif i == 1:
        label = f"TOM<br>{d.day}"
        cls   = "date d-tomorrow"
    else:
        label = f"{d.strftime('%a')}<br>{d.day}"
        cls   = "date"
    if d_str == st.session_state.sel_date:
        cls += " sel"
    date_cells += f'<div class="{cls}" onclick="go(\'date\',\'{d_str}\')">{label}</div>\n'

# Build booking grid rows
grid_rows = ""
for idx, t in enumerate(HOURS):
    band = ["tA","tB","tC","tD"][(idx // 8) % 4]
    grid_rows += f'<div class="cell {band}">{t}</div>\n'
    for i in range(3):
        table = f"Table {i+1}"
        match = bookings[
            (bookings["Table"]==table) &
            (bookings["Time"]==t) &
            (bookings["Date"]==st.session_state.sel_date)
        ]
        if not match.empty:
            booker = match.iloc[0]["User"]
            bname  = match.iloc[0]["Name"][:3]
            if booker == st.session_state.user:
                grid_rows += f'<div class="cell mine" onclick="go(\'del\',\'{t}|{table}\')">✕{bname}</div>\n'
            else:
                grid_rows += f'<div class="cell taken">{bname}</div>\n'
        else:
            grid_rows += f'<div class="cell free" onclick="go(\'book\',\'{t}|{table}\')">+</div>\n'

# Height: 2 date rows (≈50px) + header (30px) + 36 time rows * 31px
total_h = 50 + 30 + len(HOURS) * 31 + 20

html = f"""<!DOCTYPE html>
<html>
<head><meta name="viewport" content="width=device-width, initial-scale=1">
<style>
* {{ box-sizing:border-box; margin:0; padding:0; }}
body {{ font-family:sans-serif; }}

.dates {{
    display:grid;
    grid-template-columns:repeat(7,1fr);
    gap:3px;
    margin-bottom:5px;
}}
.date {{
    font-size:9px;
    padding:4px 2px;
    text-align:center;
    border-radius:6px;
    background:#e5e7eb;
    color:#111;
    line-height:1.3;
    cursor:pointer;
    -webkit-tap-highlight-color:transparent;
}}
.date.sel        {{ background:#4f46e5; color:#fff; }}
.date.d-today    {{ background:#22c55e; color:#fff; }}
.date.d-tomorrow {{ background:#3b82f6; color:#fff; }}

.grid {{
    display:grid;
    grid-template-columns:44px repeat(3,1fr);
    gap:3px;
}}
.cell {{
    height:28px;
    font-size:9px;
    display:flex;
    align-items:center;
    justify-content:center;
    border-radius:6px;
    cursor:pointer;
    -webkit-tap-highlight-color:transparent;
}}
.cell:active {{ opacity:0.6; }}
.header {{ background:#111;    color:#fff;    font-weight:bold; cursor:default; }}
.free   {{ background:#bbf7d0; color:#166534; }}
.mine   {{ background:#93c5fd; color:#1e3a5f; }}
.taken  {{ background:#e5e7eb; color:#9ca3af; cursor:default; }}
.tA     {{ background:#f3f4f6; color:#666; cursor:default; }}
.tB     {{ background:#e0f2fe; color:#666; cursor:default; }}
.tC     {{ background:#fef3c7; color:#666; cursor:default; }}
.tD     {{ background:#ede9fe; color:#666; cursor:default; }}
</style>
</head>
<body>

<script>
function go(param, value) {{
    // Walk up to the real Streamlit page and change its URL
    var base = (window.location !== window.parent.location)
               ? window.parent.location : window.location;
    var url  = base.protocol + '//' + base.host + base.pathname
               + '?' + param + '=' + encodeURIComponent(value);
    if (window.location !== window.parent.location) {{
        window.parent.location.href = url;
    }} else {{
        window.location.href = url;
    }}
}}
</script>

<div class="dates">
{date_cells}
</div>

<div class="grid">
  <div class="cell header">Time</div>
  <div class="cell header">T 1</div>
  <div class="cell header">T 2</div>
  <div class="cell header">T 3</div>
{grid_rows}
</div>

</body>
</html>"""

components.html(html, height=total_h, scrolling=True)

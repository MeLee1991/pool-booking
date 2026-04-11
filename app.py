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
# Fixed logic for processing clicks
p = st.query_params

if "date" in p:
    st.session_state.sel_date = p["date"]
    st.query_params.clear()
    st.rerun()

if "book" in p:
    t, table = p["book"].split("|", 1)
    # Check if slot is still free
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
          (bookings["Date"]==st.session_state.sel_date) &
          (bookings["User"]==st.session_state.user))
    ]
    save_data(bookings, BOOKINGS_FILE)
    st.query_params.clear()
    st.rerun()

# ================= SIDEBAR =================
with st.sidebar:
    st.markdown(f"**👤 {st.session_state.name}**")
    st.divider()
    if st.session_state.role == "admin":
        if st.button("📅 Booking", use_container_width=True):
            st.session_state.page = "Booking"
            st.rerun()
        if st.button("⚙️ Admin Panel", use_container_width=True):
            st.session_state.page = "Admin"
            st.rerun()
    if st.button("🚪 Logout", use_container_width=True):
        for k in list(st.session_state.keys()):
            del st.session_state[k]
        st.rerun()

# ================= GLOBAL CSS =================
st.markdown("""
<style>
.block-container { max-width:330px !important; padding-top:1rem; }
[data-testid="stSidebar"] { width: 200px !important; }
</style>
""", unsafe_allow_html=True)

# ================= ADMIN PAGE =================
if st.session_state.page == "Admin":
    st.title("⚙️ Admin Panel")
    # ... (Admin code remains the same as your original)
    st.stop()

# ================= BOOKING PAGE =================
today = datetime.now().date()
HOURS = [f"{h:02d}:{m}" for h in range(6,24) for m in ["00","30"]]

# 1. Build date cells (Ensuring we have 14 days)
date_cells = ""
for i in range(14):
    d     = today + timedelta(days=i)
    d_str = str(d)
    
    # Custom Labels
    if i == 0: label = f"TOD<br>{d.day}"
    elif i == 1: label = f"TOM<br>{d.day}"
    else: label = f"{d.strftime('%a')}<br>{d.day}"
    
    # Selection logic
    cls = "date"
    if i == 0: cls += " d-today"
    elif i == 1: cls += " d-tomorrow"
    
    if d_str == st.session_state.sel_date:
        cls += " sel"
        
    date_cells += f'<div class="{cls}" onclick="go(\'date\',\'{d_str}\')">{label}</div>\n'

# 2. Build booking grid rows
grid_rows = ""
for idx, t in enumerate(HOURS):
    band = ["tA","tB","tC","tD"][(idx // 8) % 4]
    grid_rows += f'<div class="cell {band}">{t}</div>\n'
    for i in range(1, 4):
        table = f"Table {i}"
        match = bookings[
            (bookings["Table"]==table) &
            (bookings["Time"]==t) &
            (bookings["Date"]==st.session_state.sel_date)
        ]
        if not match.empty:
            booker = match.iloc[0]["User"]
            bname  = match.iloc[0]["Name"][:4]
            if booker == st.session_state.user:
                grid_rows += f'<div class="cell mine" onclick="go(\'del\',\'{t}|{table}\')">✕ {bname}</div>\n'
            else:
                grid_rows += f'<div class="cell taken">{bname}</div>\n'
        else:
            grid_rows += f'<div class="cell free" onclick="go(\'book\',\'{t}|{table}\')">+</div>\n'

# Height calculation to avoid double scrollbars
total_h = 850 

html_code = f"""
<!DOCTYPE html>
<html>
<head>
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
<style>
    * {{ box-sizing:border-box; margin:0; padding:0; font-family: sans-serif; }}
    body {{ padding: 5px; background: white; }}
    
    .dates {{
        display: grid;
        grid-template-columns: repeat(7, 1fr); /* Force 7 columns */
        gap: 4px;
        margin-bottom: 12px;
    }}
    
    .date {{
        font-size: 10px;
        padding: 6px 2px;
        text-align: center;
        border-radius: 8px;
        background: #f3f4f6;
        cursor: pointer;
        line-height: 1.2;
    }}
    
    .date.sel {{ background: #4f46e5 !important; color: white !important; font-weight: bold; }}
    .date.d-today {{ border: 1.5px solid #22c55e; }}
    .date.d-tomorrow {{ border: 1.5px solid #3b82f6; }}

    .grid {{
        display: grid;
        grid-template-columns: 50px repeat(3, 1fr);
        gap: 4px;
    }}
    
    .cell {{
        height: 32px;
        font-size: 10px;
        display: flex;
        align-items: center;
        justify-content: center;
        border-radius: 6px;
        cursor: pointer;
        transition: 0.1s;
    }}

    .header {{ background: #1f2937; color: white; font-weight: bold; cursor: default; }}
    .free   {{ background: #dcfce7; color: #166534; border: 1px solid #bbf7d0; }}
    .mine   {{ background: #dbeafe; color: #1e40af; border: 1.5px solid #3b82f6; font-weight: bold; }}
    .taken  {{ background: #f3f4f6; color: #9ca3af; cursor: not-allowed; }}
    
    .tA {{ background: #fafafa; color: #666; }}
    .tB {{ background: #f0f9ff; color: #666; }}
    .tC {{ background: #fffbeb; color: #666; }}
    .tD {{ background: #f5f3ff; color: #666; }}
</style>
</head>
<body>

<div class="dates">
    {date_cells}
</div>

<div class="grid">
    <div class="cell header">Time</div>
    <div class="cell header">T1</div>
    <div class="cell header">T2</div>
    <div class="cell header">T3</div>
    {grid_rows}
</div>

<script>
function go(param, value) {{
    const url = new URL(window.parent.location.href);
    url.searchParams.set(param, value);
    window.parent.location.href = url.href;
}}
</script>

</body>
</html>
"""

components.html(html_code, height=total_h, scrolling=True)

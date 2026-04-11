import os
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

st.set_page_config(page_title="Pool", layout="centered")

# ================= DATA =================
USERS_FILE = "users.csv"
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
for k in ["user","name","role"]:
    if k not in st.session_state:
        st.session_state[k] = None

if "sel_date" not in st.session_state:
    st.session_state.sel_date = str(datetime.now().date())

# ================= LOGIN =================
if st.session_state.user is None:
    st.title("Pool")
    e = st.text_input("Email")
    p = st.text_input("Password", type="password")

    if st.button("Login"):
        m = users[(users["Email"]==e)&(users["Password"]==p)]
        if not m.empty:
            st.session_state.user = e
            st.session_state.name = m.iloc[0]["Name"]
            st.session_state.role = m.iloc[0]["Role"]
            st.rerun()
    st.stop()

# ================= ACTION HANDLER (query-param bookings) =================
params = st.query_params

if "date" in params:
    st.session_state.sel_date = params["date"]
    st.query_params.clear()
    st.rerun()

if "book" in params:
    t, table = params["book"].split("|")
    new = pd.DataFrame([{
        "User":  st.session_state.user,
        "Name":  st.session_state.name,
        "Date":  st.session_state.sel_date,
        "Table": table,
        "Time":  t
    }])
    bookings = pd.concat([bookings, new])
    save_data(bookings, BOOKINGS_FILE)
    st.query_params.clear()
    st.rerun()

if "del" in params:
    t, table = params["del"].split("|")
    bookings = bookings[
        ~((bookings["Table"]==table) &
          (bookings["Time"]==t) &
          (bookings["Date"]==st.session_state.sel_date))
    ]
    save_data(bookings, BOOKINGS_FILE)
    st.query_params.clear()
    st.rerun()

# ================= SIDEBAR =================
page = "Booking"
with st.sidebar:
    st.write(f"👤 {st.session_state.name}")

    if st.session_state.role == "admin":
        page = st.radio("Page", ["Booking","Admin"])

    if st.button("Logout"):
        st.session_state.clear()
        st.rerun()

# ================= CSS =================
st.markdown("""
<style>

.block-container { max-width: 300px; margin:auto; padding-top:1rem; }

/* DATE GRID */
.dates {
    display:grid;
    grid-template-columns: repeat(7, 1fr);
    gap:3px;
    margin-bottom:6px;
}
.date {
    font-size:9px;
    padding:5px 2px;
    text-align:center;
    border-radius:6px;
    background:#eee;
    text-decoration:none;
    color:black;
}
.date.sel          { background:#4f46e5; color:white; }
.date.date-today   { background:#22c55e; color:white; }
.date.date-tomorrow{ background:#3b82f6; color:white; }

/* BOOKING GRID */
.grid {
    display:grid;
    grid-template-columns: 44px repeat(3, 1fr);
    gap:3px;
}
.cell {
    height:28px;
    font-size:9px;
    display:flex;
    align-items:center;
    justify-content:center;
    border-radius:6px;
    text-decoration:none;
}

/* header */
.header { background:#111; color:white; font-weight:bold; }

/* states */
.free  { background:#bbf7d0; color:#166534; }
.mine  { background:#93c5fd; color:#1e3a5f; }
.taken { background:#e5e7eb; color:#6b7280; }

/* time bands */
.tA { background:#f3f4f6; }
.tB { background:#e0f2fe; }
.tC { background:#fef3c7; }
.tD { background:#ede9fe; }

hr { margin:6px 0; }

</style>
""", unsafe_allow_html=True)

# ================= ADMIN =================
if page == "Admin":
    st.title("Admin")

    st.subheader("Users")
    st.dataframe(users)

    em = st.text_input("Email")
    nm = st.text_input("Name")
    pw = st.text_input("Password")
    rl = st.selectbox("Role", ["user","admin"])

    if st.button("Add User"):
        new = pd.DataFrame([{"Email":em,"Name":nm,"Password":pw,"Role":rl}])
        users = pd.concat([users, new])
        save_data(users, USERS_FILE)
        st.rerun()

    del_user = st.selectbox("Delete user", users["Email"])
    if st.button("Delete User"):
        users = users[users["Email"] != del_user]
        save_data(users, USERS_FILE)
        st.rerun()

    st.subheader("Bookings")
    st.download_button("Download CSV", bookings.to_csv(index=False), "bookings.csv")
    st.stop()

# ================= DATE PICKER (HTML grid) =================
today = datetime.now().date()

html = '<div class="dates">'
for i in range(14):
    d     = today + timedelta(days=i)
    d_str = str(d)

    cls   = "date"
    label = f"{d.day}.{d.strftime('%a')}"

    if i == 0:
        cls  += " date-today"
        label = "TOD"
    elif i == 1:
        cls  += " date-tomorrow"
        label = "TOM"

    if d_str == st.session_state.sel_date:
        cls += " sel"

    html += f'<a href="?date={d_str}" class="{cls}">{label}</a>'
html += '</div>'

# ================= BOOKING GRID (HTML grid) =================
HOURS = [f"{h:02d}:{m}" for h in range(6,24) for m in ["00","30"]]

html += '<div class="grid">'
html += '<div class="cell header">T</div>'
html += '<div class="cell header">1</div>'
html += '<div class="cell header">2</div>'
html += '<div class="cell header">3</div>'

for idx, t in enumerate(HOURS):
    color = ["tA","tB","tC","tD"][(idx // 8) % 4]
    html += f'<div class="cell {color}">{t}</div>'

    for i in range(3):
        table = f"Table {i+1}"
        match = bookings[
            (bookings["Table"]==table) &
            (bookings["Time"]==t) &
            (bookings["Date"]==st.session_state.sel_date)
        ]

        if not match.empty:
            user = match.iloc[0]["User"]
            name = match.iloc[0]["Name"][:3]
            if user == st.session_state.user:
                html += f'<a href="?del={t}|{table}" class="cell mine">✕{name}</a>'
            else:
                html += f'<div class="cell taken">{name}</div>'
        else:
            html += f'<a href="?book={t}|{table}" class="cell free">+</a>'

html += '</div>'

st.markdown(html, unsafe_allow_html=True)

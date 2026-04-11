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

if "page" not in st.session_state:
    st.session_state.page = "Booking"

# ================= LOGIN =================
if st.session_state.user is None:
    st.title("🏊 Pool")
    e = st.text_input("Email")
    p = st.text_input("Password", type="password")
    if st.button("Login", use_container_width=True):
        m = users[(users["Email"]==e) & (users["Password"]==p)]
        if not m.empty:
            st.session_state.user = e
            st.session_state.name = m.iloc[0]["Name"]
            st.session_state.role = m.iloc[0]["Role"]
            st.session_state.page = "Booking"
            st.rerun()
        else:
            st.error("Wrong email or password")
    st.stop()

# ================= ACTION HANDLER =================
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
    bookings = pd.concat([bookings, new], ignore_index=True)
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

if "page" in params:
    st.session_state.page = params["page"]
    st.query_params.clear()
    st.rerun()

# ================= SIDEBAR =================
with st.sidebar:
    st.markdown(f"### 👤 {st.session_state.name}")
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
        st.session_state.clear()
        st.rerun()

# ================= CSS =================
st.markdown("""
<style>

.block-container { max-width:310px !important; margin:auto; padding-top:0.5rem; }

/* ── DATE GRID: 2 rows × 7 cols ── */
.dates {
    display: grid;
    grid-template-columns: repeat(7, 1fr);
    gap: 3px;
    margin-bottom: 6px;
}
.date {
    font-size: 9px;
    padding: 4px 2px;
    text-align: center;
    border-radius: 6px;
    background: #e5e7eb;
    text-decoration: none;
    color: #111;
    line-height: 1.3;
}
.date.sel       { background:#4f46e5; color:white; }
.date.d-today   { background:#22c55e; color:white; }
.date.d-tomorrow{ background:#3b82f6; color:white; }

/* ── BOOKING GRID ── */
.grid {
    display: grid;
    grid-template-columns: 44px repeat(3, 1fr);
    gap: 3px;
}
.cell {
    height: 28px;
    font-size: 9px;
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: 6px;
    text-decoration: none;
}
.header { background:#111;     color:white;   font-weight:bold; }
.free   { background:#bbf7d0;  color:#166534; }
.mine   { background:#93c5fd;  color:#1e3a5f; }
.taken  { background:#e5e7eb;  color:#9ca3af; }
.tA     { background:#f3f4f6;  color:#555; }
.tB     { background:#e0f2fe;  color:#555; }
.tC     { background:#fef3c7;  color:#555; }
.tD     { background:#ede9fe;  color:#555; }

</style>
""", unsafe_allow_html=True)

# ================= ADMIN PAGE =================
if st.session_state.page == "Admin":
    st.title("⚙️ Admin Panel")

    tab1, tab2 = st.tabs(["👥 Users", "📋 Bookings & Stats"])

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
        st.download_button("⬇️ Download CSV", bookings.to_csv(index=False), "bookings.csv", use_container_width=True)

    st.stop()

# ================= BOOKING PAGE =================
today = datetime.now().date()

# DATE GRID — 14 cells in a 7-column CSS grid = exactly 2 rows
html = '<div class="dates">'
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

    html += f'<a href="?date={d_str}" class="{cls}">{label}</a>'
html += '</div>'

# BOOKING GRID
HOURS = [f"{h:02d}:{m}" for h in range(6,24) for m in ["00","30"]]

html += '<div class="grid">'
html += '<div class="cell header">Time</div>'
html += '<div class="cell header">T 1</div>'
html += '<div class="cell header">T 2</div>'
html += '<div class="cell header">T 3</div>'

for idx, t in enumerate(HOURS):
    band = ["tA","tB","tC","tD"][(idx // 8) % 4]
    html += f'<div class="cell {band}">{t}</div>'

    for i in range(3):
        table = f"Table {i+1}"
        match = bookings[
            (bookings["Table"]==table) &
            (bookings["Time"]==t) &
            (bookings["Date"]==st.session_state.sel_date)
        ]

        if not match.empty:
            booker      = match.iloc[0]["User"]
            booker_name = match.iloc[0]["Name"][:3]
            if booker == st.session_state.user:
                html += f'<a href="?del={t}|{table}" class="cell mine">✕{booker_name}</a>'
            else:
                html += f'<div class="cell taken">{booker_name}</div>'
        else:
            html += f'<a href="?book={t}|{table}" class="cell free">+</a>'

html += '</div>'

st.markdown(html, unsafe_allow_html=True)

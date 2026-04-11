import os
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

# ================= 1. SETUP & DATA =================
st.set_page_config(page_title="Pool", layout="centered")

# CSS to make native Streamlit buttons look like your grid cells
st.markdown("""
<style>
    .block-container { max-width:380px !important; padding-top: 1rem !important; }
    div.stButton > button {
        width: 100%;
        height: 32px;
        padding: 0px;
        font-size: 10px !important;
        border-radius: 6px;
    }
    /* Simple color coding for the buttons */
    button[kind="secondary"] { background-color: #f3f4f6; } /* Empty/Standard */
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

if not st.session_state.sel_date:
    st.session_state.sel_date = str(datetime.now().date())
if not st.session_state.page:
    st.session_state.page = "Booking"

# ================= 2. LOGIN =================
if st.session_state.user is None:
    st.title("🏊 Pool Login")
    e = st.text_input("Email").strip().lower()
    p = st.text_input("Password", type="password")
    if st.button("Login", use_container_width=True):
        u_db = st.session_state.users
        m = u_db[(u_db["Email"]==e) & (u_db["Password"]==p)]
        if not m.empty:
            st.session_state.user = e
            st.session_state.name = m.iloc[0]["Name"]
            st.session_state.role = m.iloc[0]["Role"]
            st.rerun()
        else: st.error("Wrong credentials")
    st.stop()

# ================= 3. SIDEBAR & ADMIN =================
with st.sidebar:
    st.write(f"**👤 {st.session_state.name}**")
    if st.session_state.role == "admin":
        if st.button("📅 Booking Grid"): st.session_state.page = "Booking"; st.rerun()
        if st.button("📊 Admin & Stats"): st.session_state.page = "Admin"; st.rerun()
    if st.button("🚪 Logout"):
        st.session_state.clear()
        st.rerun()

if st.session_state.page == "Admin":
    st.title("⚙️ Admin & Stats")
    t1, t2 = st.tabs(["Users", "Stats"])
    with t1:
        with st.form("new_user"):
            ae, an, ap, ar = st.text_input("Email"), st.text_input("Name"), st.text_input("Pass"), st.selectbox("Role", ["user","admin"])
            if st.form_submit_button("Add User"):
                new_u = pd.DataFrame([{"Email":ae.lower(),"Name":an,"Password":ap,"Role":ar}])
                st.session_state.users = pd.concat([st.session_state.users, new_u], ignore_index=True)
                save_data(st.session_state.users, USERS_FILE)
                st.rerun()
        st.dataframe(st.session_state.users, use_container_width=True)
    with t2:
        dfb = st.session_state.bookings
        if not dfb.empty:
            st.metric("Total Bookings", len(dfb))
            st.bar_chart(dfb["Name"].value_counts())
        else: st.info("No bookings yet.")
    st.stop()

# ================= 4. BOOKING GRID (THE LOOKOUT) =================
st.write(f"### 🗓️ Selected: {st.session_state.sel_date}")

# --- DATE SELECTOR (2 rows of 7) ---
today = datetime.now().date()
cols = st.columns(7)
for i in range(14):
    d = today + timedelta(days=i)
    d_str = str(d)
    label = f"{'TOD' if i==0 else ('TOM' if i==1 else d.strftime('%a').upper())}\n{d.day}"
    
    # Place in first or second row of columns
    with cols[i % 7]:
        # Highlighting the selected date
        btn_type = "primary" if d_str == st.session_state.sel_date else "secondary"
        if st.button(label, key=f"date_{i}", type=btn_type):
            st.session_state.sel_date = d_str
            st.rerun()

st.divider()

# --- TIME SLOTS ---
HOURS = [f"{h:02d}:{m}" for h in range(6,24) for m in ["00","30"]]
head = st.columns([1.2, 1, 1, 1])
head[0].write("**Time**")
head[1].write("**T1**")
head[2].write("**T2**")
head[3].write("**T3**")

for t in HOURS:
    row = st.columns([1.2, 1, 1, 1])
    row[0].caption(f"**{t}**")
    
    for i in range(1, 4):
        table = f"Table {i}"
        match = st.session_state.bookings[
            (st.session_state.bookings["Table"]==table) & 
            (st.session_state.bookings["Time"]==t) & 
            (st.session_state.bookings["Date"]==st.session_state.sel_date)
        ]
        
        with row[i]:
            if not match.empty:
                b_user = match.iloc[0]["User"]
                b_name = match.iloc[0]["Name"][:3]
                is_mine = (b_user == st.session_state.user) or (st.session_state.role == "admin")
                
                if is_mine:
                    if st.button(f"✕ {b_name}", key=f"del_{t}_{i}", type="primary"):
                        df = st.session_state.bookings
                        mask = (df["Table"]==table) & (df["Time"]==t) & (df["Date"]==st.session_state.sel_date)
                        st.session_state.bookings = df[~mask]
                        save_data(st.session_state.bookings, BOOKINGS_FILE)
                        st.rerun()
                else:
                    st.button(b_name, key=f"taken_{t}_{i}", disabled=True)
            else:
                if st.button("+", key=f"free_{t}_{i}"):
                    new_b = pd.DataFrame([{
                        "User": st.session_state.user, "Name": st.session_state.name,
                        "Date": st.session_state.sel_date, "Table": table, "Time": t
                    }])
                    st.session_state.bookings = pd.concat([st.session_state.bookings, new_b], ignore_index=True)
                    save_data(st.session_state.bookings, BOOKINGS_FILE)
                    st.rerun()

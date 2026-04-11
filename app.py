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

/* narrow centred layout */
.block-container { max-width:310px !important; margin:auto; padding-top:0.5rem; }

/* ---- all buttons baseline ---- */
.stButton > button {
    height:28px !important;
    min-height:28px !important;
    padding:0 2px !important;
    font-size:9px !important;
    border-radius:6px !important;
    width:100% !important;
    line-height:1 !important;
    white-space:pre-wrap !important;
}

/* ---- date button colours via wrapper class ---- */
.d-default > div > button { background:#e5e7eb !important; color:#111 !important; border:none !important; }
.d-today   > div > button { background:#22c55e !important; color:white !important; border:none !important; }
.d-tomorrow> div > button { background:#3b82f6 !important; color:white !important; border:none !important; }
.d-sel     > div > button { background:#4f46e5 !important; color:white !important; border:2px solid #312e81 !important; }

/* ---- booking cell colours via wrapper class ---- */
.btn-free  > div > button { background:#bbf7d0 !important; color:#166534 !important; border:none !important; }
.btn-mine  > div > button { background:#93c5fd !important; color:#1e3a5f !important; border:none !important; }
.btn-taken > div > button { background:#e5e7eb !important; color:#9ca3af !important; border:none !important; }

/* ---- time label cell ---- */
.cell {
    height:28px;
    font-size:9px;
    display:flex;
    align-items:center;
    justify-content:center;
    border-radius:6px;
}
.header { background:#111 !important; color:white !important; font-weight:bold; }
.tA { background:#f3f4f6; color:#555; }
.tB { background:#e0f2fe; color:#555; }
.tC { background:#fef3c7; color:#555; }
.tD { background:#ede9fe; color:#555; }

</style>
""", unsafe_allow_html=True)

# ================= ADMIN PAGE =================
if st.session_state.page == "Admin":
    st.title("⚙️ Admin Panel")

    tab1, tab2 = st.tabs(["👥 Users", "📋 Bookings & Stats"])

    with tab1:
        if users.empty:
            st.info("No users yet.")
        else:
            st.dataframe(users[["Email","Name","Role"]], use_container_width=True)

        st.markdown("---")
        st.markdown("**➕ Add user**")
        em = st.text_input("Email",    key="a_em")
        nm = st.text_input("Name",     key="a_nm")
        pw = st.text_input("Password", key="a_pw")
        rl = st.selectbox("Role", ["user","admin"], key="a_rl")
        if st.button("Add User", use_container_width=True, key="add_user_btn"):
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
            if st.button("Delete User", use_container_width=True, key="del_user_btn"):
                users = users[users["Email"] != del_user]
                save_data(users, USERS_FILE)
                st.success("Deleted")
                st.rerun()

    with tab2:
        if bookings.empty:
            st.info("No bookings yet.")
        else:
            st.dataframe(bookings, use_container_width=True)
            st.markdown("---")
            st.markdown("**📊 Bookings per user**")
            top = bookings["Name"].value_counts().reset_index()
            top.columns = ["Name","Count"]
            st.bar_chart(top.set_index("Name"))

            st.markdown("**📊 Bookings per table**")
            tbl = bookings["Table"].value_counts().reset_index()
            tbl.columns = ["Table","Count"]
            st.bar_chart(tbl.set_index("Table"))

        st.download_button(
            "⬇️ Download bookings CSV",
            bookings.to_csv(index=False),
            "bookings.csv",
            use_container_width=True
        )
    st.stop()

# ================= BOOKING PAGE =================
today = datetime.now().date()

st.markdown("##### Select date")

# TWO rows of 7 days
for row_start in [0, 7]:
    cols = st.columns(7)
    for j in range(7):
        i     = row_start + j
        d     = today + timedelta(days=i)
        d_str = str(d)
        is_sel = (d_str == st.session_state.sel_date)

        # label: TOD/TOM for first two, else "Mon\n12"
        if i == 0:
            label = f"TOD\n{d.day}"
        elif i == 1:
            label = f"TOM\n{d.day}"
        else:
            label = f"{d.strftime('%a')}\n{d.day}"

        # wrapper div picks the colour
        if is_sel:
            css_cls = "d-sel"
        elif i == 0:
            css_cls = "d-today"
        elif i == 1:
            css_cls = "d-tomorrow"
        else:
            css_cls = "d-default"

        with cols[j]:
            st.markdown(f'<div class="{css_cls}">', unsafe_allow_html=True)
            if st.button(label, key=f"date_{d_str}"):
                st.session_state.sel_date = d_str
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

st.divider()

# ================= GRID HEADER =================
HOURS = [f"{h:02d}:{m}" for h in range(6,24) for m in ["00","30"]]

hcols = st.columns([1.2, 1, 1, 1])
hcols[0].markdown('<div class="cell header">Time</div>', unsafe_allow_html=True)
hcols[1].markdown('<div class="cell header">T 1</div>',  unsafe_allow_html=True)
hcols[2].markdown('<div class="cell header">T 2</div>',  unsafe_allow_html=True)
hcols[3].markdown('<div class="cell header">T 3</div>',  unsafe_allow_html=True)

# ================= GRID ROWS =================
for idx, t in enumerate(HOURS):
    band  = ["tA","tB","tC","tD"][(idx // 8) % 4]
    gcols = st.columns([1.2, 1, 1, 1])

    # Time label
    gcols[0].markdown(f'<div class="cell {band}">{t}</div>', unsafe_allow_html=True)

    for i in range(3):
        table = f"Table {i+1}"
        match = bookings[
            (bookings["Table"]==table) &
            (bookings["Time"]==t) &
            (bookings["Date"]==st.session_state.sel_date)
        ]

        with gcols[i+1]:
            if not match.empty:
                booker      = match.iloc[0]["User"]
                booker_name = match.iloc[0]["Name"][:3]

                if booker == st.session_state.user:
                    # My booking → click cancels
                    st.markdown('<div class="btn-mine">', unsafe_allow_html=True)
                    if st.button(f"✕{booker_name}", key=f"del_{t}_{i}"):
                        bookings = bookings.drop(match.index)
                        save_data(bookings, BOOKINGS_FILE)
                        st.rerun()
                    st.markdown('</div>', unsafe_allow_html=True)
                else:
                    # Taken by someone else → disabled
                    st.markdown('<div class="btn-taken">', unsafe_allow_html=True)
                    st.button(booker_name, key=f"tak_{t}_{i}", disabled=True)
                    st.markdown('</div>', unsafe_allow_html=True)
            else:
                # Free → click to book
                st.markdown('<div class="btn-free">', unsafe_allow_html=True)
                if st.button("+", key=f"book_{t}_{i}"):
                    new = pd.DataFrame([{
                        "User":  st.session_state.user,
                        "Name":  st.session_state.name,
                        "Date":  st.session_state.sel_date,
                        "Table": table,
                        "Time":  t
                    }])
                    bookings = pd.concat([bookings, new], ignore_index=True)
                    save_data(bookings, BOOKINGS_FILE)
                    st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)

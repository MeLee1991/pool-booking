import os
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

st.set_page_config(layout="centered", page_title="Osmica")

# ================= DATA =================
USERS_FILE = "users.csv"
BOOKINGS_FILE = "bookings.csv"

def load(file, cols):
    if os.path.exists(file) and os.path.getsize(file) > 0:
        return pd.read_csv(file, dtype=str)
    return pd.DataFrame(columns=cols)

def save(df, file):
    df.to_csv(file, index=False)

users    = load(USERS_FILE,    ["Email","Name","Password","Role"])
bookings = load(BOOKINGS_FILE, ["User","Name","Date","Table","Time"])

if "tom3@gmail.com" not in users["Email"].values:
    users = pd.concat([users, pd.DataFrame([{
        "Email":"tom3@gmail.com","Name":"Tom","Password":"1234","Role":"admin"
    }])])
    save(users, USERS_FILE)

# ================= SESSION =================
for k,v in [("user",None),("name",None),("role",None),("page","booking"),
            ("date", str(datetime.now().date()))]:
    if k not in st.session_state:
        st.session_state[k] = v

today = str(datetime.now().date())
cur   = datetime.strptime(st.session_state.date, "%Y-%m-%d")

# ================= LOGIN =================
if st.session_state.user is None:
    st.markdown("## 🍷 Osmica Booking")
    e = st.text_input("Email", value="tom3@gmail.com")
    p = st.text_input("Password", type="password", value="1234")
    if st.button("Login", use_container_width=True):
        m = users[(users["Email"]==e)&(users["Password"]==p)]
        if not m.empty:
            st.session_state.user = e
            st.session_state.name = m.iloc[0]["Name"]
            st.session_state.role = m.iloc[0]["Role"]
            st.rerun()
        else:
            st.error("Wrong email or password")
    st.stop()

# ================= GLOBAL CSS =================
st.markdown("""
<style>
.block-container {
    max-width: 430px !important;
    padding: 0.5rem 0.5rem 3rem !important;
    margin: auto !important;
}
/* kill ALL streamlit vertical gaps between elements */
div[data-testid="stVerticalBlockBorderWrapper"],
div[data-testid="stVerticalBlock"] > div[data-testid="stVerticalBlock"] {
    gap: 0 !important;
}
.element-container { margin-bottom: 0 !important; padding-bottom: 0 !important; }
.stButton { margin: 0 !important; padding: 0 !important; }
.stButton > button {
    margin: 0 !important; padding: 0 2px !important;
    height: 34px !important; width: 100% !important;
    font-size: 11px !important; font-weight: 700 !important;
    border-radius: 7px !important; border: none !important;
    cursor: pointer !important; transition: filter 0.12s !important;
}
.stButton > button:hover { filter: brightness(0.93) !important; }
/* horizontal block gap = 5px */
div[data-testid="stHorizontalBlock"] {
    gap: 5px !important;
    margin-bottom: 5px !important;
    align-items: stretch !important;
}
div[data-testid="column"] { padding: 0 !important; }
</style>
""", unsafe_allow_html=True)

# ================= HELPERS =================
HOURS  = [f"{h:02d}:{m}" for h in range(6,24) for m in ["00","30"]]
TABLES = ["Table 1","Table 2","Table 3"]

def time_bg(t):
    h = int(t[:2])
    if   h < 10: return "#fde68a","#78350f"
    elif h < 14: return "#bae6fd","#0c4a6e"
    elif h < 18: return "#ddd6fe","#3b0764"
    elif h < 22: return "#fed7aa","#7c2d12"
    else:        return "#bbf7d0","#14532d"

# ============================================================
#  ADMIN PAGE
# ============================================================
if st.session_state.page == "admin":
    st.markdown("### ⚙️ Admin panel")
    tab1, tab2 = st.tabs(["👥 Users", "📋 All bookings"])

    with tab1:
        st.dataframe(users[["Email","Name","Role"]], use_container_width=True)
        st.divider()
        st.markdown("**Add new user**")
        ne = st.text_input("Email",    key="nu_e")
        nn = st.text_input("Name",     key="nu_n")
        np_ = st.text_input("Password",key="nu_p")
        nr = st.selectbox("Role", ["user","admin"], key="nu_r")
        if st.button("Add user", use_container_width=True):
            if ne and nn and np_:
                users = pd.concat([users, pd.DataFrame([{
                    "Email":ne,"Name":nn,"Password":np_,"Role":nr
                }])], ignore_index=True)
                save(users, USERS_FILE)
                st.success("User added!")
                st.rerun()
    with tab2:
        if bookings.empty:
            st.info("No bookings yet.")
        else:
            st.dataframe(bookings.sort_values(["Date","Time"]), use_container_width=True)
            if st.button("🗑️ Clear ALL bookings", type="primary", use_container_width=True):
                bookings = pd.DataFrame(columns=["User","Name","Date","Table","Time"])
                save(bookings, BOOKINGS_FILE)
                st.rerun()

    st.markdown("---")
    if st.button("← Back to booking", use_container_width=True):
        st.session_state.page = "booking"
        st.rerun()
    st.stop()

# ============================================================
#  BOOKING PAGE
# ============================================================

# ── Top bar ──────────────────────────────────────────────────
c1, c2 = st.columns([3,1])
c1.markdown(f"<p style='margin:0;font-size:13px;color:#6b7280'>👤 {st.session_state.name}</p>",
            unsafe_allow_html=True)
with c2:
    if st.session_state.role == "admin":
        if st.button("⚙️ Admin"):
            st.session_state.page = "admin"
            st.rerun()

# ── Date nav ─────────────────────────────────────────────────
is_today  = st.session_state.date == today
day_label = cur.strftime("%a, %d %b %Y")
color     = "#dc2626" if is_today else "#111827"
badge     = " 🔴" if is_today else ""

n1, n2, n3 = st.columns([1,5,1])
with n1:
    if st.button("◀", key="prev"):
        st.session_state.date = str((cur - timedelta(days=1)).date())
        st.rerun()
with n2:
    st.markdown(
        f"<div style='text-align:center;font-weight:800;font-size:14px;"
        f"color:{color};padding:4px 0'>{day_label}{badge}</div>",
        unsafe_allow_html=True)
with n3:
    if st.button("▶", key="next"):
        st.session_state.date = str((cur + timedelta(days=1)).date())
        st.rerun()

# ── Swipe JS ─────────────────────────────────────────────────
st.markdown("""
<script>
(function(){
  var sx=0;
  document.addEventListener('touchstart',function(e){sx=e.touches[0].clientX;},{passive:true});
  document.addEventListener('touchend',function(e){
    var dx=e.changedTouches[0].clientX-sx;
    if(Math.abs(dx)<55)return;
    var btns=Array.from(document.querySelectorAll('button'));
    if(dx<0){var b=btns.find(function(b){return b.innerText.trim()==='▶';});if(b)b.click();}
    else{var b=btns.find(function(b){return b.innerText.trim()==='◀';});if(b)b.click();}
  },{passive:true});
})();
</script>
""", unsafe_allow_html=True)

st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)

# ── Column header row ────────────────────────────────────────
CELL = ("display:flex;align-items:center;justify-content:center;"
        "height:34px;border-radius:7px;font-weight:800;font-size:12px;")

hrow = st.columns([1.2,1,1,1])
hrow[0].markdown(f'<div style="{CELL}background:#e5e7eb;color:#374151">Time</div>',
                 unsafe_allow_html=True)
for i,lbl in enumerate(["T1","T2","T3"]):
    hrow[i+1].markdown(f'<div style="{CELL}background:#e5e7eb;color:#374151">{lbl}</div>',
                       unsafe_allow_html=True)

st.markdown("<div style='height:5px'></div>", unsafe_allow_html=True)

# ── Data rows ─────────────────────────────────────────────────
day_bk = bookings[bookings["Date"] == st.session_state.date]

for t in HOURS:
    bg, fg = time_bg(t)
    row = st.columns([1.2,1,1,1])

    # TIME – pure HTML label, no button
    row[0].markdown(
        f'<div style="{CELL}background:{bg};color:{fg}">{t}</div>',
        unsafe_allow_html=True)

    for i, table in enumerate(TABLES):
        match = day_bk[(day_bk["Table"]==table)&(day_bk["Time"]==t)]

        with row[i+1]:
            if not match.empty:
                bu   = match.iloc[0]["User"]
                bn   = match.iloc[0]["Name"][:7]
                lbl  = f"✕ {bn}"

                if bu == st.session_state.user:
                    # MY slot → blue button, click cancels
                    st.markdown(f"""
<style>
div[data-testid="stButton"]:has(button[kind="secondary"][key="b_{t}_{i}"]) button {{
    background:#dbeafe !important;color:#1e3a5f !important;
    border:1.5px solid #93c5fd !important;
}}
</style>""", unsafe_allow_html=True)
                    if st.button(lbl, key=f"b_{t}_{i}"):
                        bookings = bookings.drop(match.index)
                        save(bookings, BOOKINGS_FILE)
                        st.rerun()
                else:
                    # TAKEN → red HTML div (no button)
                    st.markdown(
                        f'<div style="{CELL}background:#fee2e2;color:#991b1b;'
                        f'border:1.5px solid #fca5a5;font-size:11px;font-weight:700;'
                        f'overflow:hidden;white-space:nowrap">{lbl}</div>',
                        unsafe_allow_html=True)
            else:
                # FREE → green button, click books
                st.markdown(f"""
<style>
div[data-testid="stButton"]:has(button[key="b_{t}_{i}"]) button {{
    background:#d1fae5 !important;color:#065f46 !important;
    border:1.5px solid #6ee7b7 !important;
}}
</style>""", unsafe_allow_html=True)
                if st.button("", key=f"b_{t}_{i}"):
                    bookings = pd.concat([bookings, pd.DataFrame([{
                        "User": st.session_state.user,
                        "Name": st.session_state.name,
                        "Date": st.session_state.date,
                        "Table": table,
                        "Time": t,
                    }])], ignore_index=True)
                    save(bookings, BOOKINGS_FILE)
                    st.rerun()

    st.markdown("<div style='height:5px'></div>", unsafe_allow_html=True)

# ── Logout ───────────────────────────────────────────────────
st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)
if st.button("Logout", use_container_width=True):
    for k in ["user","name","role","page"]:
        st.session_state[k] = None
    st.session_state.date = str(datetime.now().date())
    st.session_state.page = "booking"
    st.rerun()

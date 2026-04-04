import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime, timedelta
import hashlib

# ==========================================
# CONFIG
# ==========================================
st.set_page_config(page_title="Poolhall", layout="wide")

DB = "db.sqlite"
OWNER_EMAIL = "admin@pool.com"

# ==========================================
# 🍏 APPLE UI
# ==========================================
st.markdown("""
<style>
body, .stApp {
    background:#0b0b0c;
    color:#f5f5f7;
    font-family:-apple-system,BlinkMacSystemFont;
}

/* HEADER */
.header {
    position:sticky;
    top:0;
    z-index:999;
    background:#0b0b0c;
    padding:8px;
    font-weight:600;
    text-align:center;
}

/* SLOT */
.slot {
    height:26px;
    border-radius:10px;
    margin-bottom:4px;
    display:flex;
    align-items:center;
    justify-content:center;
    font-size:11px;
}

/* NON PRIME */
.normal {
    background:#1c1c1e;
    color:#aaa;
}

/* PRIME */
.prime {
    background:#2c2c2e;
    border:1px solid #ff9f0a;
    box-shadow:0 0 12px rgba(255,159,10,0.35);
    color:#fff;
}

/* STATES */
.locked { opacity:0.4; }
.mine { background:#ff453a !important; color:white; }

.topbar {
    background:#1c1c1e;
    padding:10px;
    border-radius:12px;
    text-align:center;
    margin-bottom:15px;
}
</style>
""", unsafe_allow_html=True)

# ==========================================
# DATABASE
# ==========================================
def db():
    return sqlite3.connect(DB, check_same_thread=False)

def init():
    d = db()
    d.execute("CREATE TABLE IF NOT EXISTS users(email TEXT, name TEXT, pw TEXT, role TEXT, max_hours REAL)")
    d.execute("CREATE TABLE IF NOT EXISTS bookings(user TEXT, date TEXT, table_name TEXT, time TEXT)")
    d.commit()

init()

# ==========================================
# EMAIL PREVIEW (TEMP)
# ==========================================
def send_email(to, subject, body):
    st.markdown("### 📧 Email Preview")
    st.markdown(f"**To:** {to}  \n**Subject:** {subject}\n\n---\n{body}\n---")

# ==========================================
# AUTH
# ==========================================
def hash_pw(p): return hashlib.sha256(p.encode()).hexdigest()

def login(email,pw):
    return db().execute("SELECT * FROM users WHERE email=? AND pw=?", (email,hash_pw(pw))).fetchone()

def register(e,n,p):
    try:
        role="admin" if e==OWNER_EMAIL else "user"
        db().execute("INSERT INTO users VALUES (?,?,?,?,?)",(e,n,hash_pw(p),role,3.0))
        db().commit()
        return True
    except:
        return False

# ==========================================
# SESSION
# ==========================================
if "user" not in st.session_state:
    st.session_state.user=None
    st.session_state.role=None

# ==========================================
# LOGIN (FIXED ✅)
# ==========================================
st.sidebar.title("Account")

mode = st.sidebar.radio("Mode", ["Login", "Register"])

email = st.sidebar.text_input("Email").strip().lower()
name = st.sidebar.text_input("Name") if mode=="Register" else ""
pw = st.sidebar.text_input("Password", type="password")

if st.sidebar.button("Go", use_container_width=True):

    if "@" not in email or "." not in email:
        st.sidebar.error("Enter valid email")

    elif len(pw) < 3:
        st.sidebar.error("Password too short")

    else:
        if mode == "Register":
            success = register(email, name, pw)

            if success:
                st.sidebar.success("Account created ✅")
            else:
                st.sidebar.error("User already exists")

        else:
            user = login(email, pw)

            if user:
                st.session_state.user = email
                st.session_state.role = user[3]
                st.sidebar.success("Logged in ✅")
                st.rerun()
            else:
                st.sidebar.error("Wrong email or password")

if not st.session_state.user:
    st.title("🎱 Poolhall Reservations")
    st.info("Login or register from sidebar")
    st.stop()

if st.sidebar.button("Logout"):
    st.session_state.clear()
    st.rerun()

# ==========================================
# NAV
# ==========================================
view="Schedule"
if st.session_state.role=="admin":
    view=st.sidebar.radio("View",["Schedule","Admin"])

# ==========================================
# ADMIN
# ==========================================
if view=="Admin":
    st.title("⚙️ Admin Panel")

    st.subheader("Users")
    st.dataframe(pd.read_sql_query("SELECT * FROM users",db()))

    st.subheader("Bookings")
    st.dataframe(pd.read_sql_query("SELECT * FROM bookings",db()))

    st.stop()

# ==========================================
# SCHEDULE
# ==========================================
st.title("🎱 Reservations")

today=datetime.now().date()
date=st.selectbox("Date",[today+timedelta(days=i) for i in range(7)])

times=[f"{h:02d}:{m}" for h in range(8,24) for m in ("00","30")]
tables=["Table 1","Table 2","Table 3"]

df=pd.read_sql_query("SELECT * FROM bookings WHERE date=?", db(), params=(str(date),))

# USER LIMIT
user_df=pd.read_sql_query("SELECT * FROM users WHERE email=?",db(),params=(st.session_state.user,))
max_hours=float(user_df.iloc[0]["max_hours"])
used=df[df["user"]==st.session_state.user].shape[0]*0.5

st.markdown(f"<div class='topbar'>Your time: {used} / {max_hours}h</div>",unsafe_allow_html=True)

cols=st.columns(3)

for i,tbl in enumerate(tables):
    with cols[i]:
        st.markdown(f"<div class='header'>{tbl}</div>",unsafe_allow_html=True)

        for t in times:
            hour=int(t[:2])
            prime=17<=hour<=22

            slot=df[(df["table_name"]==tbl)&(df["time"]==t)]
            cls="slot prime" if prime else "slot normal"

            # BOOKED
            if not slot.empty:
                u=slot.iloc[0]["user"]

                if u==st.session_state.user:
                    if st.button(f"{t}",key=f"{tbl}{t}"):
                        db().execute("DELETE FROM bookings WHERE user=? AND date=? AND table_name=? AND time=?",
                                     (u,str(date),tbl,t))
                        db().commit()

                        send_email(OWNER_EMAIL,"❌ Cancelled",
                                   f"{u} cancelled {tbl} at {t}")

                        st.rerun()
                else:
                    st.markdown(f"<div class='{cls} locked'>{t}</div>",unsafe_allow_html=True)

            # FREE
            else:
                if used>=max_hours and st.session_state.role!="admin":
                    st.markdown(f"<div class='{cls} locked'>{t}</div>",unsafe_allow_html=True)
                else:
                    if st.button(f"{t}",key=f"{tbl}{t}"):
                        db().execute("INSERT INTO bookings VALUES (?,?,?,?)",
                                     (st.session_state.user,str(date),tbl,t))
                        db().commit()

                        send_email(OWNER_EMAIL,"🎱 New Booking",
                                   f"{email} booked {tbl} at {t}")

                        send_email(email,"⏰ Reminder",
                                   f"You have {tbl} at {t}")

                        st.rerun()

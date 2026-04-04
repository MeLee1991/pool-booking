import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime, timedelta
import hashlib
import os

# ==========================================
# CONFIG
# ==========================================
st.set_page_config(page_title="Poolhall", layout="wide")

DB = "db.sqlite"
OWNER_EMAIL = "admin@pool.com"

# ==========================================
# 🍏 UI
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
    text-align:center;
    font-weight:600;
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

/* NORMAL */
.normal { background:#1c1c1e; color:#aaa; }

/* PRIME */
.prime {
    background:#2c2c2e;
    border:1px solid #ff9f0a;
    box-shadow:0 0 10px rgba(255,159,10,0.4);
    color:#fff;
}

/* LOCK */
.locked { opacity:0.4; }

/* OWN */
.mine { background:#ff453a !important; color:white; }

/* TOP BAR */
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
# EMAIL PREVIEW
# ==========================================
def send_email(to, subject, body):
    st.markdown(f"📧 **Email → {to}**")
    st.write(subject)
    st.write(body)

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
# LOGIN SCREEN (FIXED)
# ==========================================
if not st.session_state.user:

    st.title("🎱 Poolhall Reservations")

    mode = st.radio("Select", ["Login", "Register"])

    email = st.text_input("Email").strip().lower()
    name = st.text_input("Name") if mode=="Register" else ""
    pw = st.text_input("Password", type="password")

    if st.button("Continue", use_container_width=True):

        if "@" not in email or "." not in email:
            st.error("Enter valid email")

        elif len(pw) < 3:
            st.error("Password too short")

        else:
            if mode == "Register":
                if register(email, name, pw):
                    st.success("Account created ✅")
                else:
                    st.error("User exists")

            else:
                user = login(email, pw)

                if user:
                    st.session_state.user = email
                    st.session_state.role = user[3]
                    st.success("Logged in ✅")
                    st.rerun()
                else:
                    st.error("Wrong login")

    st.stop()

# ==========================================
# LOGOUT
# ==========================================
if st.button("Logout"):
    st.session_state.clear()
    st.rerun()

# ==========================================
# BANNER IMAGE
# ==========================================
if os.path.exists("banner.jpg"):
    st.image("banner.jpg", use_container_width=True)

# ==========================================
# SCHEDULE
# ==========================================
st.title("Reservations")

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

        # TABLE IMAGE
        img_path=f"table{i+1}.jpg"
        if os.path.exists(img_path):
            st.image(img_path, use_container_width=True)

        for t in times:
            hour=int(t[:2])
            prime=17<=hour<=22

            slot=df[(df["table_name"]==tbl)&(df["time"]==t)]
            cls="slot prime" if prime else "slot normal"

            if not slot.empty:
                u=slot.iloc[0]["user"]

                if u==st.session_state.user:
                    if st.button(f"{t}",key=f"{tbl}{t}"):
                        db().execute("DELETE FROM bookings WHERE user=? AND date=? AND table_name=? AND time=?",
                                     (u,str(date),tbl,t))
                        db().commit()

                        send_email(OWNER_EMAIL,"Cancel",f"{u} cancelled {t}")
                        st.rerun()
                else:
                    st.markdown(f"<div class='{cls} locked'>{t}</div>",unsafe_allow_html=True)

            else:
                if used>=max_hours:
                    st.markdown(f"<div class='{cls} locked'>{t}</div>",unsafe_allow_html=True)
                else:
                    if st.button(f"{t}",key=f"{tbl}{t}"):
                        db().execute("INSERT INTO bookings VALUES (?,?,?,?)",
                                     (st.session_state.user,str(date),tbl,t))
                        db().commit()

                        send_email(OWNER_EMAIL,"Booking",f"{email} booked {t}")
                        st.rerun()

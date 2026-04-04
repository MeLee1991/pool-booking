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
OWNER_EMAIL = "tomaz@gmail.com"  # YOUR EMAIL = ADMIN

# ==========================================
# 🍏 LIGHT UI
# ==========================================
st.markdown("""
<style>
body, .stApp {
    background:#f5f5f7;
    color:#1d1d1f;
    font-family:-apple-system,BlinkMacSystemFont;
}

.header {
    background:white;
    padding:8px;
    text-align:center;
    font-weight:600;
    border-radius:10px;
    margin-bottom:5px;
}

.slot {
    height:32px;
    border-radius:10px;
    margin-bottom:4px;
    display:flex;
    align-items:center;
    justify-content:center;
    font-size:13px;
}

/* NORMAL */
.normal { background:#e5e5ea; }

/* PRIME */
.prime {
    background:#fff3cd;
    border:1px solid #ff9500;
}

/* LOCK */
.locked { opacity:0.4; }

/* OWN */
.mine {
    background:#ff3b30 !important;
    color:white;
}

/* TOP BAR */
.topbar {
    background:white;
    padding:10px;
    border-radius:12px;
    text-align:center;
    margin-bottom:15px;
    border:1px solid #ddd;
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

    # USERS TABLE
    d.execute("""
    CREATE TABLE IF NOT EXISTS users(
        email TEXT PRIMARY KEY,
        name TEXT,
        pw TEXT,
        role TEXT,
        max_hours REAL DEFAULT 3.0
    )
    """)

    # ADD COLUMN IF MISSING (important fix)
    try:
        d.execute("ALTER TABLE users ADD COLUMN max_hours REAL DEFAULT 3.0")
    except:
        pass  # column already exists

    # BOOKINGS TABLE
    d.execute("""
    CREATE TABLE IF NOT EXISTS bookings(
        user TEXT,
        date TEXT,
        table_name TEXT,
        time TEXT
    )
    """)

    d.commit()



init()

# ==========================================
# AUTH (AUTO LOGIN)
# ==========================================
def hash_pw(p): return hashlib.sha256(p.encode()).hexdigest()

def login_or_register(email, name, pw):
    d = db()
    user = d.execute("SELECT * FROM users WHERE email=?", (email,)).fetchone()

    if user:
        # LOGIN
        if user[2] == hash_pw(pw):
            return user
        else:
            return "wrong_password"
    else:
        # REGISTER
        role = "admin" if email == OWNER_EMAIL else "user"
        d.execute("INSERT INTO users VALUES (?,?,?,?,?)",
                  (email, name, hash_pw(pw), role, 3.0))
        d.commit()
        return d.execute("SELECT * FROM users WHERE email=?", (email,)).fetchone()

# ==========================================
# SESSION
# ==========================================
if "user" not in st.session_state:
    st.session_state.user = None
    st.session_state.role = None

# ==========================================
# LOGIN SCREEN (SUPER SIMPLE)
# ==========================================
if not st.session_state.user:

    st.title("🎱 Poolhall Reservations")

    email = st.text_input("Email").strip().lower()
    name = st.text_input("Name (first time only)")
    pw = st.text_input("Password", type="password")

    if st.button("Continue", use_container_width=True):

        if "@" not in email:
            st.error("Enter valid email")

        elif len(pw) < 3:
            st.error("Password too short")

        else:
            result = login_or_register(email, name, pw)

            if result == "wrong_password":
                st.error("Wrong password")
            else:
                st.session_state.user = result[0]
                st.session_state.role = result[3]
                st.success("Welcome ✅")
                st.rerun()

    st.stop()

# ==========================================
# LOGOUT
# ==========================================
if st.button("Logout"):
    st.session_state.clear()
    st.rerun()

# ==========================================
# BANNER
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

        img=f"table{i+1}.jpg"
        if os.path.exists(img):
            st.image(img, use_container_width=True)

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
                        st.rerun()

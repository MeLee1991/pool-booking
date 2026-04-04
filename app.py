import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime, timedelta
import hashlib
import smtplib
from email.mime.text import MIMEText

# ==========================================
# CONFIG
# ==========================================
st.set_page_config(page_title="Poolhall", layout="wide")

DB = "db.sqlite"
OWNER_EMAIL = "your@email.com"

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

/* HEADER STICKY */
.header {
    position:sticky;
    top:0;
    z-index:999;
    background:#0b0b0c;
    padding:8px;
    font-weight:600;
    text-align:center;
}

/* SLOT BASE */
.slot {
    height:26px;
    border-radius:10px;
    margin-bottom:4px;
    display:flex;
    align-items:center;
    justify-content:center;
    font-size:11px;
    transition:all .12s ease;
}

/* NON PRIME */
.normal {
    background:#1c1c1e;
    color:#aaa;
}

/* 🔥 PRIME */
.prime {
    background:#2c2c2e;
    border:1px solid #ff9f0a;
    box-shadow:0 0 12px rgba(255,159,10,0.35);
    color:#fff;
}

/* STATES */
.free { cursor:pointer; }
.free:hover { transform:scale(1.05); }

.locked { opacity:0.4; }

.mine {
    background:#ff453a !important;
    color:white;
}
</style>
""", unsafe_allow_html=True)

# ==========================================
# DB
# ==========================================
def db():
    return sqlite3.connect(DB, check_same_thread=False)

def init():
    d = db()
    d.execute("CREATE TABLE IF NOT EXISTS users(email TEXT, name TEXT, pw TEXT, role TEXT)")
    d.execute("CREATE TABLE IF NOT EXISTS bookings(user TEXT, date TEXT, table_name TEXT, time TEXT)")
    d.commit()

init()

# ==========================================
# AUTH
# ==========================================
def hash_pw(p): return hashlib.sha256(p.encode()).hexdigest()

def login(email,pw):
    return db().execute("SELECT * FROM users WHERE email=? AND pw=?", (email,hash_pw(pw))).fetchone()

def register(e,n,p):
    try:
        role="admin" if e==OWNER_EMAIL else "user"
        db().execute("INSERT INTO users VALUES (?,?,?,?)",(e,n,hash_pw(p),role))
        db().commit()
        return True
    except: return False

# ==========================================
# EMAIL
# ==========================================
def send_email(to, subject, body):
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = st.secrets["EMAIL"]
    msg['To'] = to

    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as s:
        s.login(st.secrets["EMAIL"], st.secrets["EMAIL_PASS"])
        s.send_message(msg)

# ==========================================
# SESSION
# ==========================================
if "user" not in st.session_state:
    st.session_state.user=None
    st.session_state.role=None

# ==========================================
# LOGIN UI
# ==========================================
st.sidebar.title("Account")

mode=st.sidebar.radio("Mode",["Login","Register"])
email=st.sidebar.text_input("Email")
name=st.sidebar.text_input("Name") if mode=="Register" else ""
pw=st.sidebar.text_input("Password",type="password")

if st.sidebar.button("Go"):
    if mode=="Register":
        if register(email,name,pw):
            st.success("Created")
    else:
        u=login(email,pw)
        if u:
            st.session_state.user=email
            st.session_state.role=u[3]
            st.rerun()

if not st.session_state.user:
    st.stop()

# ==========================================
# SCHEDULE
# ==========================================
st.title("Reservations")

today=datetime.now().date()
date=st.selectbox("Date",[today+timedelta(days=i) for i in range(7)])

times=[f"{h:02d}:{m}" for h in range(8,24) for m in ("00","30")]
tables=["Table 1","Table 2","Table 3"]

df=pd.read_sql_query("SELECT * FROM bookings WHERE date=?", db(), params=(str(date),))

cols=st.columns(3)

for i,tbl in enumerate(tables):
    with cols[i]:
        st.markdown(f"<div class='header'>{tbl}</div>",unsafe_allow_html=True)

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
                        send_email(OWNER_EMAIL,"Booking Cancelled",f"{u} cancelled {t}")
                        st.rerun()
                else:
                    st.markdown(f"<div class='{cls} locked'>{t}</div>",unsafe_allow_html=True)

            else:
                if st.button(f"{t}",key=f"{tbl}{t}"):
                    db().execute("INSERT INTO bookings VALUES (?,?,?,?)",
                                 (st.session_state.user,str(date),tbl,t))
                    db().commit()

                    send_email(OWNER_EMAIL,"New Booking",f"{email} booked {t}")

                    st.rerun()

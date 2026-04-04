import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime, timedelta
import hashlib
import os

st.set_page_config(page_title="Poolhall", layout="wide")

DB = "db.sqlite"
OWNER_EMAIL = "tomaz@gmail.com"

# ==========================================
# 🎨 UI
# ==========================================
st.markdown("""
<style>
body, .stApp {
    background:#f5f5f7;
    color:#1d1d1f;
}

.header {
    text-align:center;
    font-weight:600;
}

.slot {
    height:32px;
    border-radius:10px;
    margin-bottom:4px;
}

.normal { background:#e5e5ea; }

.prime {
    background:#fff3cd;
    border:1px solid #ff9500;
}

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
# DB
# ==========================================
def db():
    return sqlite3.connect(DB, check_same_thread=False)

def init():
    d = db()
    d.execute("""
    CREATE TABLE IF NOT EXISTS users(
        email TEXT PRIMARY KEY,
        name TEXT,
        pw TEXT,
        role TEXT,
        max_hours REAL DEFAULT 3.0
    )
    """)
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
# AUTH
# ==========================================
def hash_pw(p): return hashlib.sha256(p.encode()).hexdigest()

def login_or_register(email, name, pw):
    d = db()
    user = d.execute("SELECT * FROM users WHERE email=?", (email,)).fetchone()

    if user:
        if user[2] == hash_pw(pw):
            return user
        else:
            return "wrong"
    else:
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
# LOGIN
# ==========================================
if not st.session_state.user:

    st.title("🎱 Poolhall Reservations")

    email = st.text_input("Email")
    name = st.text_input("Name (first time only)")
    pw = st.text_input("Password", type="password")

    if st.button("Continue", use_container_width=True):

        result = login_or_register(email, name, pw)

        if result == "wrong":
            st.error("Wrong password")
        else:
            st.session_state.user = result[0]
            st.session_state.role = result[3]
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

st.title("Reservations")

# ==========================================
# DATE PICKER
# ==========================================
today = datetime.now().date()
dates = [today + timedelta(days=i) for i in range(14)]

labels = [
    "Today" if d == today else
    "Tomorrow" if d == today + timedelta(days=1)
    else d.strftime("%a %d")
    for d in dates
]

selected = st.radio("Select day", labels, horizontal=True)
date = dates[labels.index(selected)]

# ==========================================
# DATA
# ==========================================
times = [f"{h:02d}:{m}" for h in range(8,24) for m in ("00","30")]
tables = ["Table 1","Table 2","Table 3"]

df = pd.read_sql_query(
    "SELECT * FROM bookings WHERE date=?",
    db(), params=(str(date),)
)

# USER LIMIT
user_df=pd.read_sql_query("SELECT * FROM users WHERE email=?",db(),params=(st.session_state.user,))
max_hours=float(user_df.iloc[0]["max_hours"])
used=df[df["user"]==st.session_state.user].shape[0]*0.5

st.markdown(f"<div class='topbar'>Your time: {used} / {max_hours}h</div>",unsafe_allow_html=True)

# ==========================================
# GRID
# ==========================================
col_time, col1, col2, col3 = st.columns([1,2,2,2])

col_time.markdown("**Time**")
col1.markdown("**Table 1**")
col2.markdown("**Table 2**")
col3.markdown("**Table 3**")

for t in times:

    hour = int(t[:2])
    prime = 17 <= hour <= 22

    cols = st.columns([1,2,2,2])
    cols[0].markdown(f"🔥 {t}" if prime else t)

    for i, tbl in enumerate(tables):

        slot = df[
            (df["table_name"] == tbl) &
            (df["time"] == t)
        ]

        key = f"{tbl}_{t}"

        if not slot.empty:
            u = slot.iloc[0]["user"]

            if u == st.session_state.user:
                if cols[i+1].button("❌", key=key):
                    db().execute(
                        "DELETE FROM bookings WHERE user=? AND date=? AND table_name=? AND time=?",
                        (u, str(date), tbl, t)
                    )
                    db().commit()
                    st.rerun()
            else:
                cols[i+1].button("🔒", disabled=True, key=key)

        else:
            if cols[i+1].button("🟢", key=key):
                db().execute(
                    "INSERT INTO bookings VALUES (?,?,?,?)",
                    (st.session_state.user, str(date), tbl, t)
                )
                db().commit()
                st.rerun()

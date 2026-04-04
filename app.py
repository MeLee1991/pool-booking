import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime, timedelta
import hashlib

st.set_page_config(page_title="Poolhall", layout="wide")

DB = "db.sqlite"

# ==========================================
# 🎨 CLEAN UI
# ==========================================
st.markdown("""
<style>
body, .stApp {
    background:#f5f5f7;
    color:#1d1d1f;
    font-family:-apple-system;
}

/* SCROLL GRID */
.grid-wrap {
    overflow-x:auto;
}

/* GRID LAYOUT */
.grid {
    display:grid;
    grid-template-columns: 70px repeat(3, 90px);
    gap:6px;
    min-width:360px;
}

/* CELLS */
.cell {
    text-align:center;
    font-size:12px;
}

/* HEADERS */
.header {
    font-weight:600;
    background:white;
    position:sticky;
    top:0;
    z-index:10;
    padding:4px;
}

/* TIME */
.time {
    text-align:right;
    padding-right:6px;
    color:#666;
}

/* BUTTON */
button {
    width:100%;
    height:34px;
    border-radius:10px !important;
}

/* PRIME TIME */
.prime button {
    background:#ff9500 !important;
    color:white !important;
    font-weight:700;
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
        pw TEXT
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
        d.execute("INSERT INTO users VALUES (?,?,?)",
                  (email, name, hash_pw(pw)))
        d.commit()
        return d.execute("SELECT * FROM users WHERE email=?", (email,)).fetchone()

# ==========================================
# SESSION
# ==========================================
if "user" not in st.session_state:
    st.session_state.user = None

# ==========================================
# LOGIN
# ==========================================
if not st.session_state.user:

    st.title("🎱 Poolhall")

    email = st.text_input("Email")
    name = st.text_input("Name (first time only)")
    pw = st.text_input("Password", type="password")

    if st.button("Continue", use_container_width=True):

        if "@" not in email:
            st.error("Enter valid email")

        elif len(pw) < 2:
            st.error("Password too short")

        else:
            result = login_or_register(email, name, pw)

            if result == "wrong":
                st.error("Wrong password")
            else:
                st.session_state.user = result[0]
                st.rerun()

    st.stop()

# ==========================================
# LOGOUT
# ==========================================
if st.button("Logout"):
    st.session_state.clear()
    st.rerun()

# ==========================================
# DATE
# ==========================================
today = datetime.now().date()
dates = [today + timedelta(days=i) for i in range(14)]

labels = [
    "Today" if d == today else
    "Tomorrow" if d == today + timedelta(days=1)
    else d.strftime("%a %d")
    for d in dates
]

selected = st.radio("", labels, horizontal=True)
date = dates[labels.index(selected)]

# ==========================================
# DATA
# ==========================================
TABLES = ["Table 1", "Table 2", "Table 3"]

times = [
    f"{h:02d}:{m:02d}"
    for h in range(8, 24)
    for m in (0, 30)
]

df = pd.read_sql_query(
    "SELECT * FROM bookings WHERE date=?",
    db(), params=(str(date),)
)

# ==========================================
# GRID
# ==========================================
st.markdown('<div class="grid-wrap"><div class="grid">', unsafe_allow_html=True)

# HEADER
st.markdown('<div class="cell header">Time</div>', unsafe_allow_html=True)
for t in TABLES:
    st.markdown(f'<div class="cell header">{t}</div>', unsafe_allow_html=True)

# ROWS
for t in times:

    hour = int(t[:2])
    prime = 17 <= hour <= 22

    st.markdown(f'<div class="cell time">{t}</div>', unsafe_allow_html=True)

    for tbl in TABLES:

        slot = df[
            (df["table_name"] == tbl) &
            (df["time"] == t)
        ]

        key = f"{tbl}_{t}"
        cls = "cell prime" if prime else "cell"

        st.markdown(f'<div class="{cls}">', unsafe_allow_html=True)

        if not slot.empty:
            u = slot.iloc[0]["user"]

            if u == st.session_state.user:
                if st.button("❌", key=key):
                    db().execute(
                        "DELETE FROM bookings WHERE user=? AND date=? AND table_name=? AND time=?",
                        (u, str(date), tbl, t)
                    )
                    db().commit()
                    st.rerun()
            else:
                st.button("🔒", key=key, disabled=True)

        else:
            if st.button("🟢", key=key):
                db().execute(
                    "INSERT INTO bookings VALUES (?,?,?,?)",
                    (st.session_state.user, str(date), tbl, t)
                )
                db().commit()
                st.rerun()

        st.markdown('</div>', unsafe_allow_html=True)

st.markdown('</div></div>', unsafe_allow_html=True)

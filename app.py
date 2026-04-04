import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime, timedelta
import hashlib

st.set_page_config(page_title="Poolhall", layout="wide")

DB = "db.sqlite"

# ==========================================
# 🎨 MODERN UI (APPLE-STYLE)
# ==========================================
st.markdown("""
<style>

/* BACKGROUND */
body, .stApp {
    background:#f5f5f7;
    color:#1d1d1f;
    font-family:-apple-system,BlinkMacSystemFont;
}

/* FORCE 3 COLUMNS + SCROLL */
[data-testid="stHorizontalBlock"] {
    display:flex !important;
    flex-wrap:nowrap !important;
    overflow-x:auto !important;
    gap:6px;
}

/* EACH COLUMN */
[data-testid="column"] {
    min-width:110px !important;
    flex:0 0 auto !important;
}

/* TIME COLUMN */
[data-testid="column"]:first-child {
    min-width:70px !important;
}

/* BUTTON STYLE (MODERN) */
button {
    width:100%;
    height:42px;
    border-radius:14px !important;
    border:none !important;
    font-size:14px;
    font-weight:600;
    background:#e5e5ea;
    color:#111;
    transition:all 0.15s ease;
}

/* HOVER */
button:hover {
    transform:scale(1.03);
}

/* ACTIVE CLICK */
button:active {
    transform:scale(0.95);
}

/* FREE SLOT */
button[kind="secondary"] {
    background:#34c759 !important;
    color:white !important;
}

/* YOUR BOOKING */
button[kind="primary"] {
    background:#ff3b30 !important;
    color:white !important;
}

/* LOCKED */
button[disabled] {
    background:#d1d1d6 !important;
    color:#666 !important;
}

/* PRIME TIME */
.prime button {
    background:#ff9500 !important;
    color:white !important;
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
    name = st.text_input("Name")
    pw = st.text_input("Password", type="password")

    if st.button("Continue", use_container_width=True):

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
TABLES = ["Table 1","Table 2","Table 3"]

times = [
    f"{h:02d}:{m:02d}"
    for h in range(8,24)
    for m in (0,30)
]

df = pd.read_sql_query(
    "SELECT * FROM bookings WHERE date=?",
    db(), params=(str(date),)
)

# ==========================================
# GRID (WORKING VERSION)
# ==========================================
# HEADER
cols = st.columns([1,2,2,2])
cols[0].markdown("**Time**")
cols[1].markdown("**Table 1**")
cols[2].markdown("**Table 2**")
cols[3].markdown("**Table 3**")

# ROWS
for t in times:

    hour = int(t[:2])
    prime = 17 <= hour <= 22

    cols = st.columns([1,2,2,2])

    cols[0].markdown(f"🔥 {t}" if prime else t)

    for i, tbl in enumerate(TABLES):

        slot = df[
            (df["table_name"] == tbl) &
            (df["time"] == t)
        ]

        key = f"{tbl}_{t}"

        if not slot.empty:
            u = slot.iloc[0]["user"]

            if u == st.session_state.user:
                cols[i+1].button("Booked", key=key, type="primary")
                if cols[i+1].button("Cancel", key=key+"c"):
                    db().execute(
                        "DELETE FROM bookings WHERE user=? AND date=? AND table_name=? AND time=?",
                        (u, str(date), tbl, t)
                    )
                    db().commit()
                    st.rerun()
            else:
                cols[i+1].button("Taken", disabled=True, key=key)

        else:
            if cols[i+1].button("Book", key=key, type="secondary"):
                db().execute(
                    "INSERT INTO bookings VALUES (?,?,?,?)",
                    (st.session_state.user, str(date), tbl, t)
                )
                db().commit()
                st.rerun()

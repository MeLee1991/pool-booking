import streamlit as st
import pandas as pd
import os
from datetime import datetime, timedelta

st.set_page_config(page_title="Poolhall", layout="wide")

# ===============================
# FILES
# ===============================
USERS_FILE = "users.csv"
BOOKINGS_FILE = "bookings.csv"
OWNER = "admin@gmail.com"

# ===============================
# INIT FILES
# ===============================
if not os.path.exists(USERS_FILE):
    pd.DataFrame(columns=["email","name","pw","role"]).to_csv(USERS_FILE,index=False)

if not os.path.exists(BOOKINGS_FILE):
    pd.DataFrame(columns=["user","date","table","time"]).to_csv(BOOKINGS_FILE,index=False)

# ===============================
# LOAD/SAVE
# ===============================
def load_users():
    return pd.read_csv(USERS_FILE)

def save_users(df):
    df.to_csv(USERS_FILE,index=False)

def load_bookings():
    return pd.read_csv(BOOKINGS_FILE)

def save_bookings(df):
    df.to_csv(BOOKINGS_FILE,index=False)

# ===============================
# STYLE (CLEAN + SAFE)
# ===============================
st.markdown("""
<style>

/* GENERAL */
body, .stApp {
    background:#f5f5f7;
    font-family:-apple-system,BlinkMacSystemFont;
}

/* HEADER */
.title {
    text-align:center;
    font-size:32px;
    font-weight:700;
    margin-bottom:10px;
}

/* DATE BAR */
.date-row {
    display:flex;
    overflow-x:auto;
    gap:8px;
    padding-bottom:10px;
}

/* TABLE GRID */
.grid {
    display:flex;
    overflow-x:auto;
    gap:10px;
}

/* COLUMN */
.col {
    min-width:140px;
    flex:1;
}

/* HEADER */
.col-header {
    background:#111;
    color:white;
    text-align:center;
    padding:6px;
    border-radius:10px;
    margin-bottom:6px;
    font-weight:600;
}

/* SLOT */
.slot {
    border-radius:10px;
    margin-bottom:4px;
    text-align:center;
    padding:6px;
    cursor:pointer;
    transition:0.15s;
    font-size:12px;
}

/* FREE */
.free {
    background:white;
    border:1px solid #ddd;
}

/* YOUR */
.mine {
    background:#ff3b30;
    color:white;
}

/* LOCKED */
.locked {
    background:#eee;
    color:#888;
}

/* PRIME */
.prime {
    height:42px;
    font-size:15px;
    font-weight:700;
    background:#ffe8cc;
    border:2px solid #ff9500;
}

/* NORMAL */
.normal {
    height:28px;
}

/* HOVER */
.slot:hover {
    transform:scale(0.97);
}

/* MOBILE */
@media (max-width:900px){
    .col {
        min-width:120px;
    }
}

</style>
""", unsafe_allow_html=True)

# ===============================
# SESSION
# ===============================
if "user" not in st.session_state:
    st.session_state.user = None
    st.session_state.name = None
    st.session_state.role = None

# ===============================
# LOGIN
# ===============================
if not st.session_state.user:

    st.markdown("<div class='title'>🎱 Poolhall</div>", unsafe_allow_html=True)

    email = st.text_input("Email").lower()
    name = st.text_input("Name")
    pw = st.text_input("Password", type="password")

    if st.button("Continue"):

        users = load_users()

        user = users[users["email"] == email]

        if not user.empty:
            if user.iloc[0]["pw"] == pw:
                st.session_state.user = email
                st.session_state.name = user.iloc[0]["name"]
                st.session_state.role = user.iloc[0]["role"]
                st.rerun()
            else:
                st.error("Wrong password")
        else:
            role = "admin" if email == OWNER else "user"
            new = pd.DataFrame([[email,name,pw,role]],
                               columns=["email","name","pw","role"])
            save_users(pd.concat([users,new]))
            st.success("Registered, press again")
    st.stop()

# ===============================
# LOGOUT
# ===============================
if st.button("Logout"):
    st.session_state.clear()
    st.rerun()

# ===============================
# TITLE
# ===============================
st.markdown("<div class='title'>Reserve Table</div>", unsafe_allow_html=True)

# ===============================
# DATE SELECT
# ===============================
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

# ===============================
# DATA
# ===============================
times = [f"{h:02d}:{m}" for h in range(8,24) for m in ("00","30")]
tables = ["Table 1","Table 2","Table 3"]

df = load_bookings()
df = df[df["date"] == str(date)]

# ===============================
# GRID (REAL FIX)
# ===============================
cols = st.columns(3)

for i, col in enumerate(cols):

    table = tables[i]

    with col:

        st.markdown(f"<div class='col-header'>{table}</div>", unsafe_allow_html=True)

        for t in times:

            hour = int(t[:2])
            prime = 17 <= hour <= 23

            slot = df[(df["table"] == table) & (df["time"] == t)]

            cls = "slot "
            cls += "prime " if prime else "normal "

            if not slot.empty:

                u = slot.iloc[0]["user"]

                if u == st.session_state.user:
                    cls += "mine"
                    if st.button(f"{t} ❌", key=f"{table}{t}"):
                        data = load_bookings()
                        data = data[~((data["table"]==table)&(data["time"]==t)&(data["date"]==str(date)))]
                        save_bookings(data)
                        st.rerun()

                else:
                    cls += "locked"
                    st.markdown(f"<div class='{cls}'>{t} 🔒</div>", unsafe_allow_html=True)

            else:
                cls += "free"
                if st.button(f"{t} 🟢", key=f"{table}{t}"):
                    data = load_bookings()
                    new = pd.DataFrame([[st.session_state.user,str(date),table,t]],
                                       columns=["user","date","table","time"])
                    save_bookings(pd.concat([data,new]))
                    st.rerun()

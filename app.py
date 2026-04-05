import os
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

st.set_page_config(page_title="Pool Booking", layout="wide")

# ==========================================
# FILES
# ==========================================
USERS_FILE = "users.csv"
BOOKINGS_FILE = "bookings.csv"

# ==========================================
# SAFE LOAD
# ==========================================
def load_users():
    if os.path.exists(USERS_FILE):
        df = pd.read_csv(USERS_FILE)
        for col in ["Email","Name","Password","Role"]:
            if col not in df.columns:
                df[col] = ""
        df["Email"] = df["Email"].astype(str).str.strip().str.lower()
        df["Password"] = df["Password"].astype(str).str.strip()
        return df
    return pd.DataFrame(columns=["Email","Name","Password","Role"])

def save_users(df):
    df.to_csv(USERS_FILE, index=False)

def load_bookings():
    if os.path.exists(BOOKINGS_FILE):
        df = pd.read_csv(BOOKINGS_FILE)
        if "Name" not in df.columns:
            df["Name"] = df["User"].astype(str).str.split("@").str[0]
        return df
    return pd.DataFrame(columns=["User","Name","Date","Table","Time"])

def save_bookings(df):
    df.to_csv(BOOKINGS_FILE, index=False)

# ==========================================
# SESSION
# ==========================================
if "user" not in st.session_state:
    st.session_state.user = None

# ==========================================
# SIDEBAR LOGIN
# ==========================================
st.sidebar.title("🔐 Access")

mode = st.sidebar.radio("Mode", ["Login","Register"])

email = st.sidebar.text_input("Email")
password = st.sidebar.text_input("Password", type="password")

name = st.sidebar.text_input("Name") if mode == "Register" else ""

users = load_users()

if st.sidebar.button("Go"):
    email = email.strip().lower()
    password = password.strip()

    if mode == "Register":
        if email in users["Email"].values:
            st.sidebar.error("User exists")
        else:
            role = "admin" if users.empty else "pending"
            new = pd.DataFrame([[email,name,password,role]],
                               columns=["Email","Name","Password","Role"])
            save_users(pd.concat([users,new], ignore_index=True))
            st.sidebar.success("Registered")

    else:
        u = users[(users["Email"]==email)&(users["Password"]==password)]
        if not u.empty:
            st.session_state.user = email
            st.session_state.name = u.iloc[0]["Name"]
            st.session_state.role = u.iloc[0]["Role"]
            st.rerun()
        else:
            st.sidebar.error("Invalid login")

if st.session_state.user is None:
    st.title("POOL BOOKING")
    st.stop()

# ==========================================
# CSS (CLEAN + MOBILE FIX)
# ==========================================
st.markdown("""
<style>

/* DATE BAR */
[data-testid="stRadio"]{
position:sticky;
top:0;
background:#f8f9fa;
z-index:100;
padding:4px;
}

/* 2 ROWS */
[data-testid="stRadio"] > div{
display:grid!important;
grid-template-columns:repeat(7,1fr)!important;
grid-template-rows:auto auto!important;
gap:4px;
}

/* HEADER */
.table-header{
position:sticky;
top:60px;
background:#1e1e1e;
color:white;
text-align:center;
padding:6px;
border-radius:8px;
margin-bottom:4px;
}

/* BUTTON */
button{
border-radius:999px!important;
height:26px!important;
font-size:11px!important;
white-space:nowrap!important;
overflow:hidden!important;
text-overflow:ellipsis!important;
}

/* MOBILE: FORCE 3 COL */
@media (max-width: 900px){
[data-testid="stHorizontalBlock"]{
display:flex!important;
flex-wrap:nowrap!important;
gap:4px!important;
}
[data-testid="column"]{
width:33%!important;
flex:1 1 33%!important;
}
button{
font-size:9px!important;
height:24px!important;
}
}

</style>
""", unsafe_allow_html=True)

# ==========================================
# DATE PICKER
# ==========================================
today = datetime.now().date()
dates = [today + timedelta(days=i) for i in range(14)]

labels = ["Today","Tomorrow"] + [d.strftime("%a %d") for d in dates[2:]]

selected = st.radio("", labels, horizontal=True)
selected_date = dates[labels.index(selected)]

# ==========================================
# TIME RANGE
# ==========================================
HOURS = []
for h in list(range(8,24)) + list(range(0,3)):
    for m in ["00","30"]:
        HOURS.append(f"{h:02d}:{m}")

# ==========================================
# GRID
# ==========================================
st.title("RESERVE TABLE")

df = load_bookings()

BLOCKS = ["#f8f9fa","#eef7ff"]

cols = st.columns(3)

for i, col in enumerate(cols):
    col.markdown(f"<div class='table-header'>Table {i+1}</div>", unsafe_allow_html=True)

    for t in HOURS:
        idx = HOURS.index(t)
        bg = BLOCKS[(idx//4)%2]

        booked = df[
            (df["Table"]==f"Table {i+1}") &
            (df["Time"]==t) &
            (df["Date"]==str(selected_date))
        ]

        key = f"{i}_{t}"

        col.markdown(
            f"<div style='background:{bg};padding:2px;border-radius:8px;'>",
            unsafe_allow_html=True
        )

        if not booked.empty:
            name_display = booked.iloc[0]["Name"]

            if booked.iloc[0]["User"] == st.session_state.user:
                if col.button(f"{t} ❌ {name_display}", key=key):
                    df = df.drop(booked.index)
                    save_bookings(df)
                    st.rerun()
            else:
                col.button(f"{t} 🔒 {name_display}", key=key, disabled=True)

        else:
            if col.button(f"{t} 🟢", key=key):
                new = pd.DataFrame([[
                    st.session_state.user,
                    st.session_state.name,
                    str(selected_date),
                    f"Table {i+1}",
                    t
                ]], columns=["User","Name","Date","Table","Time"])

                save_bookings(pd.concat([df,new], ignore_index=True))
                st.rerun()

        col.markdown("</div>", unsafe_allow_html=True)

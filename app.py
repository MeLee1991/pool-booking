import os
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

st.set_page_config(page_title="Poolhall Reservations", layout="wide")

# ==========================================
# FILES
# ==========================================
USERS_FILE = "users.csv"
BOOKINGS_FILE = "bookings.csv"

if not os.path.exists(USERS_FILE):
    pd.DataFrame(columns=["Email","Name","Password","Role"]).to_csv(USERS_FILE,index=False)

if not os.path.exists(BOOKINGS_FILE):
    pd.DataFrame(columns=["User","Name","Date","Table","Time"]).to_csv(BOOKINGS_FILE,index=False)

def load_users():
    return pd.read_csv(USERS_FILE)

def save_users(df):
    df.to_csv(USERS_FILE,index=False)

def load_bookings():
    return pd.read_csv(BOOKINGS_FILE)

def save_bookings(df):
    df.to_csv(BOOKINGS_FILE,index=False)

# ==========================================
# SESSION
# ==========================================
if "user" not in st.session_state:
    st.session_state.user = None

# ==========================================
# SIDEBAR (FIXED COLUMN)
# ==========================================
st.sidebar.title("🔐 Access")

mode = st.sidebar.radio("Choose option", ["Login","Register"])

email = st.sidebar.text_input("Email")
password = st.sidebar.text_input("Password", type="password")
name = st.sidebar.text_input("Name") if mode=="Register" else ""

users = load_users()

if st.sidebar.button("Go"):
    email=email.strip().lower()

    if mode=="Register":
        role = "admin" if users.empty else "pending"
        new = pd.DataFrame([[email,name,password,role]],
                           columns=["Email","Name","Password","Role"])
        save_users(pd.concat([users,new],ignore_index=True))
        st.sidebar.success("Registered")

    else:
        u = users[(users.Email==email)&(users.Password==password)]
        if not u.empty and u.iloc[0]["Role"]!="pending":
            st.session_state.user=email
            st.session_state.name=u.iloc[0]["Name"]
            st.session_state.role=u.iloc[0]["Role"]
            st.rerun()
        else:
            st.sidebar.error("Login failed")

# STOP if not logged
if st.session_state.user is None:
    st.title("POOL TABLE BOOKING")
    st.stop()

# ==========================================
# CSS (FIXED)
# ==========================================
st.markdown("""
<style>

/* DATE BAR STICKY */
[data-testid="stRadio"]{
position:sticky;
top:0;
z-index:100;
background:#f8f9fa;
padding:8px;
}

/* FORCE 2 ROWS */
[data-testid="stRadio"] > div{
display:grid!important;
grid-template-columns:repeat(7,1fr)!important;
grid-template-rows:auto auto!important;
gap:6px;
}

[data-testid="stRadio"] label{
white-space:nowrap!important;
text-align:center!important;
font-size:12px;
}

/* HEADER STICKY */
.table-header{
position:sticky;
top:70px;
z-index:90;
background:#212529;
color:white;
padding:6px;
border-radius:6px;
margin-bottom:6px;
text-align:center;
}

/* BUTTON */
button{
border-radius:999px!important;
}

</style>
""", unsafe_allow_html=True)

# ==========================================
# DATE PICKER (CORRECT 2 ROWS)
# ==========================================
today=datetime.now().date()
dates=[today+timedelta(days=i) for i in range(14)]

labels=[]
for i,d in enumerate(dates):
    if i==0:
        labels.append("Today")
    elif i==1:
        labels.append("Tomorrow")
    else:
        labels.append(d.strftime("%a %d"))

selected = st.radio("", labels, horizontal=True)
selected_date = dates[labels.index(selected)]

# ==========================================
# GRID
# ==========================================
st.title("RESERVE TABLE")

df = load_bookings()

HOURS = [f"{h:02d}:{m}" for h in range(8,24) for m in ("00","30")]

cols = st.columns(3)

for i, col in enumerate(cols):
    col.markdown(f"<div class='table-header'>Table {i+1}</div>", unsafe_allow_html=True)

    for t in HOURS:
        booked = df[
            (df.Table==f"Table {i+1}") &
            (df.Time==t) &
            (df.Date==str(selected_date))
        ]

        key=f"{i}_{t}"

        if not booked.empty:
            owner = booked.iloc[0]["User"]
            name_display = booked.iloc[0]["Name"]

            # YOUR SLOT
            if owner == st.session_state.user:
                if col.button(f"{t} ❌ {name_display}", key=key, type="primary"):
                    df = df.drop(booked.index)
                    save_bookings(df)
                    st.rerun()

            # LOCKED
            else:
                col.button(f"{t} 🔒 {name_display}", key=key, disabled=True)

        else:
            # FREE SLOT
            if col.button(f"{t} 🟢", key=key):
                new = pd.DataFrame([[
                    st.session_state.user,
                    st.session_state.name,  # 💥 FIX: STORE NAME
                    str(selected_date),
                    f"Table {i+1}",
                    t
                ]], columns=["User","Name","Date","Table","Time"])

                save_bookings(pd.concat([df,new],ignore_index=True))
                st.rerun()

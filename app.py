import os
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

st.set_page_config(page_title="Poolhall Reservations", layout="wide")

# ==========================================
# FILE SETUP (FIXED + SAFE)
# ==========================================
USERS_FILE = "users.csv"
BOOKINGS_FILE = "bookings.csv"

def load_users():
    if os.path.exists(USERS_FILE):
        df = pd.read_csv(USERS_FILE)
        if not df.empty:
            df["Email"] = df["Email"].astype(str).str.strip().str.lower()
            df["Password"] = df["Password"].astype(str).str.strip()
        return df
    return pd.DataFrame(columns=["Email","Name","Password","Role"])

def save_users(df):
    df.to_csv(USERS_FILE, index=False)

def load_bookings():
    if os.path.exists(BOOKINGS_FILE):
        return pd.read_csv(BOOKINGS_FILE)
    return pd.DataFrame(columns=["User","Date","Table","Time"])

def save_bookings(df):
    df.to_csv(BOOKINGS_FILE, index=False)

# create files if missing
if not os.path.exists(USERS_FILE):
    pd.DataFrame(columns=["Email","Name","Password","Role"]).to_csv(USERS_FILE,index=False)

if not os.path.exists(BOOKINGS_FILE):
    pd.DataFrame(columns=["User","Date","Table","Time"]).to_csv(BOOKINGS_FILE,index=False)

# ==========================================
# SESSION STATE
# ==========================================
if "user" not in st.session_state:
    st.session_state.user = None

# ==========================================
# AUTH SYSTEM (FIXED)
# ==========================================
st.sidebar.title("🔐 Access")

mode = st.sidebar.radio("Choose", ["Login","Register"])

email = st.sidebar.text_input("Email")
password = st.sidebar.text_input("Password", type="password")
name = st.sidebar.text_input("Name") if mode == "Register" else ""

users = load_users()

if st.sidebar.button("Go"):
    email = email.strip().lower()
    password = password.strip()

    # REGISTER
    if mode == "Register":
        name = name.strip()

        if email in users["Email"].values:
            st.sidebar.error("User already exists")
        elif len(email) < 5 or "@" not in email:
            st.sidebar.error("Invalid email")
        elif len(name) < 2:
            st.sidebar.error("Enter name")
        else:
            role = "admin" if users.empty else "user"

            new_user = pd.DataFrame([[email, name, password, role]],
                                    columns=["Email","Name","Password","Role"])

            users = pd.concat([users, new_user], ignore_index=True)
            save_users(users)

            st.sidebar.success("Registered! Now login.")

    # LOGIN
    else:
        users = load_users()

        u = users[(users["Email"] == email) & (users["Password"] == password)]

        if not u.empty:
            st.session_state.user = email
            st.session_state.name = u.iloc[0]["Name"]
            st.session_state.role = u.iloc[0]["Role"]
            st.rerun()
        else:
            st.sidebar.error("Invalid login")

# stop if not logged in
if st.session_state.user is None:
    st.title("POOL TABLE BOOKING")
    st.info("Login or register from sidebar")
    st.stop()

# ==========================================
# LOGGED IN
# ==========================================
st.sidebar.success(f"Logged in as {st.session_state.name}")

if st.sidebar.button("Logout"):
    st.session_state.user = None
    st.rerun()

# ==========================================
# UI STYLE (YOUR DESIGN, CLEANED)
# ==========================================
st.markdown("""
<style>

/* smooth font */
* { -webkit-font-smoothing: antialiased; }

/* container */
.block-container {
    max-width: 800px !important;
    margin: auto !important;
}

/* table headers */
.table-header {
    text-align: center;
    font-weight: 700;
    font-size: 14px;
    background: #212529;
    color: white;
    border-radius: 6px;
    padding: 6px;
}

/* buttons */
button {
    border-radius: 999px !important;
    transition: all .08s ease !important;
    box-shadow: 0 1px 2px rgba(0,0,0,0.1);
}

/* hover */
button:hover {
    filter: brightness(0.96);
}

/* click */
button:active {
    transform: scale(0.93);
}

/* FREE */
button[kind="secondary"] {
    background: #f1f3f5 !important;
    border: 1px solid #dee2e6 !important;
}

/* YOURS */
button[kind="primary"] {
    background: linear-gradient(180deg,#ff4d4f,#dc3545) !important;
    border: none !important;
    color: white !important;
}

/* LOCKED */
button[disabled] {
    background: #f8d7da !important;
    border: 1px solid #f1aeb5 !important;
    color: #842029 !important;
}

/* mobile fix */
@media (max-width:900px){
    [data-testid="column"]{
        width:32%!important;
        flex:0 0 32%!important;
    }
    button p{
        font-size:8px!important;
    }
}

</style>
""", unsafe_allow_html=True)

# ==========================================
# BOOKING UI
# ==========================================
st.title("RESERVE TABLE")

today = datetime.now().date()
dates = [today + timedelta(days=i) for i in range(7)]
selected_date = st.selectbox("Select date", dates)

df = load_bookings()

HOURS = [f"{h:02d}:{m}" for h in range(8,24) for m in ("00","30")]

cols = st.columns(3)

for i, col in enumerate(cols):
    col.markdown(f"<div class='table-header'>Table {i+1}</div>", unsafe_allow_html=True)

    for t in HOURS:
        booked = df[(df.Table == f"Table {i+1}") &
                    (df.Time == t) &
                    (df.Date == str(selected_date))]

        key = f"{i}_{t}"

        if not booked.empty:
            owner = booked.iloc[0]["User"]

            if owner == st.session_state.user:
                if col.button(f"{t} ❌ Yours", key=key, type="primary"):
                    df = df[~((df.Table == f"Table {i+1}") &
                              (df.Time == t) &
                              (df.Date == str(selected_date)))]
                    save_bookings(df)
                    st.rerun()
            else:
                col.button(f"{t} 🔒", key=key, disabled=True)

        else:
            if col.button(f"{t} 🟢 Free", key=key, type="secondary"):
                new = pd.DataFrame([[st.session_state.user,
                                     str(selected_date),
                                     f"Table {i+1}",
                                     t]],
                                   columns=["User","Date","Table","Time"])

                save_bookings(pd.concat([df, new], ignore_index=True))
                st.rerun()

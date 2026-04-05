import os
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import smtplib
from email.mime.text import MIMEText

st.set_page_config(page_title="Poolhall Reservations", layout="wide")

# ==========================================
# EMAIL CONFIG
# ==========================================
EMAIL_SENDER = "tomazbratina@gmail.com"
EMAIL_PASSWORD = "xwkdekpieajdhkwl"
ADMIN_EMAIL = "tomazbratina@gmail.com"

def send_pending_email(new_user_email):
    try:
        msg = MIMEText(f"New user pending approval:\n\n{new_user_email}")
        msg["Subject"] = "New User Pending Approval"
        msg["From"] = EMAIL_SENDER
        msg["To"] = ADMIN_EMAIL

        server = smtplib.SMTP_SSL("smtp.gmail.com", 465)
        server.login(EMAIL_SENDER, EMAIL_PASSWORD)
        server.send_message(msg)
        server.quit()
    except Exception as e:
        print("Email error:", e)

# ==========================================
# FILES
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

if not os.path.exists(USERS_FILE):
    pd.DataFrame(columns=["Email","Name","Password","Role"]).to_csv(USERS_FILE,index=False)

if not os.path.exists(BOOKINGS_FILE):
    pd.DataFrame(columns=["User","Date","Table","Time"]).to_csv(BOOKINGS_FILE,index=False)

# ==========================================
# SESSION
# ==========================================
if "user" not in st.session_state:
    st.session_state.user = None

# ==========================================
# AUTH
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
        else:
            role = "admin" if users.empty else "pending"

            new_user = pd.DataFrame([[email, name, password, role]],
                                    columns=["Email","Name","Password","Role"])

            users = pd.concat([users, new_user], ignore_index=True)
            save_users(users)

            if role == "pending":
                send_pending_email(email)

            st.sidebar.success("Registered! Await admin approval.")

    # LOGIN
    else:
        users = load_users()

        u = users[(users["Email"] == email) & (users["Password"] == password)]

        if not u.empty:
            role = u.iloc[0]["Role"]

            if role == "pending":
                st.sidebar.warning("⏳ Awaiting admin approval")
            else:
                st.session_state.user = email
                st.session_state.name = u.iloc[0]["Name"]
                st.session_state.role = role
                st.rerun()
        else:
            st.sidebar.error("Invalid login")

if st.session_state.user is None:
    st.title("POOL TABLE BOOKING")
    st.info("Login or register from sidebar")
    st.stop()

st.sidebar.success(f"Logged in as {st.session_state.name}")

if st.sidebar.button("Logout"):
    st.session_state.user = None
    st.rerun()

# ==========================================
# ADMIN PANEL
# ==========================================
if st.session_state.role == "admin":
    st.sidebar.markdown("---")
    if st.sidebar.checkbox("⚙️ Admin Panel"):

        st.subheader("User Management")
        users = load_users()

        for i, row in users.iterrows():
            c1, c2, c3 = st.columns([3,2,2])

            c1.write(f"{row['Name']} ({row['Email']})")
            c2.write(f"Role: {row['Role']}")

            if row["Role"] == "pending":
                if c3.button("Approve", key=f"a{i}"):
                    users.at[i,"Role"]="user"
                    save_users(users)
                    st.rerun()

            elif row["Role"] == "user":
                if c3.button("Make Admin", key=f"b{i}"):
                    users.at[i,"Role"]="admin"
                    save_users(users)
                    st.rerun()

            elif row["Role"] == "admin" and row["Email"] != st.session_state.user:
                if c3.button("Demote", key=f"c{i}"):
                    users.at[i,"Role"]="user"
                    save_users(users)
                    st.rerun()

# ==========================================
# BOOKING UI
# ==========================================
st.title("RESERVE TABLE")

today = datetime.now().date()
dates = [today + timedelta(days=i) for i in range(14)]

labels = ["Today" if d==today else "Tomorrow" if d==today+timedelta(days=1) else d.strftime("%a %d") for d in dates]
selected = st.radio("Date", labels, horizontal=True, label_visibility="collapsed")
selected_date = dates[labels.index(selected)]

df = load_bookings()
HOURS = [f"{h:02d}:{m}" for h in range(8,24) for m in ("00","30")]

cols = st.columns(3)

for i,col in enumerate(cols):
    col.subheader(f"Table {i+1}")

    for t in HOURS:
        booked = df[(df.Table==f"Table {i+1}") & (df.Time==t) & (df.Date==str(selected_date))]
        key=f"{i}_{t}"

        if not booked.empty:
            owner = booked.iloc[0]["User"]
            name_display = owner.split("@")[0]

            if owner == st.session_state.user:
                if col.button(f"{t} ❌ {name_display}", key=key, type="primary"):
                    df=df[~((df.Table==f"Table {i+1}")&(df.Time==t)&(df.Date==str(selected_date)))]
                    save_bookings(df)
                    st.rerun()

            elif st.session_state.role=="admin":
                if col.button(f"{t} 🔴 {name_display}", key=key, type="primary"):
                    df=df[~((df.Table==f"Table {i+1}")&(df.Time==t)&(df.Date==str(selected_date)))]
                    save_bookings(df)
                    st.rerun()

            else:
                col.button(f"{t} 🔒 {name_display}", key=key, disabled=True)

        else:
            if col.button(f"{t} 🟢 Free", key=key):
                new = pd.DataFrame([[st.session_state.user,str(selected_date),f"Table {i+1}",t]],
                                   columns=["User","Date","Table","Time"])
                save_bookings(pd.concat([df,new],ignore_index=True))
                st.rerun()

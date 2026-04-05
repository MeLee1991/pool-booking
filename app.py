import os
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

st.set_page_config(page_title="Pool Booking", layout="wide")

# =========================
# FILES
# =========================
USERS_FILE = "users.csv"
BOOKINGS_FILE = "bookings.csv"

# =========================
# LOAD / SAVE
# =========================
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

# =========================
# SESSION
# =========================
if "user" not in st.session_state:
    st.session_state.user = None

# =========================
# SIDEBAR
# =========================
st.sidebar.title("🔐 Access")

mode = st.sidebar.radio("Mode", ["Login","Register"])

email = st.sidebar.text_input("Email")
password = st.sidebar.text_input("Password", type="password")
name = st.sidebar.text_input("Name") if mode=="Register" else ""

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

# =========================
# ADMIN
# =========================
if st.session_state.role == "admin":
    st.sidebar.markdown("---")
    admin = st.sidebar.radio("Admin", ["Booking","Users","Stats"])

    if admin == "Users":
        st.title("Users")

        users = load_users()
        edited = st.data_editor(users, num_rows="dynamic", use_container_width=True)

        if st.button("Save"):
            save_users(edited)
            st.success("Saved")

        st.download_button("Export CSV", users.to_csv(index=False), "users.csv")

        uploaded = st.file_uploader("Import CSV")
        if uploaded:
            save_users(pd.read_csv(uploaded))
            st.success("Imported")

        st.stop()

    if admin == "Stats":
        st.title("Stats")
        df = load_bookings()

        if not df.empty:
            st.bar_chart(df["Name"].value_counts())
            st.bar_chart(df["Table"].value_counts())
        else:
            st.info("No data")

        st.stop()

# =========================
# CSS (CLEAN + FIXED)
# =========================
st.markdown("""
<style>

/* ===== SIDEBAR FIX (NO VERTICAL TEXT) ===== */
section[data-testid="stSidebar"] label,
section[data-testid="stSidebar"] div {
    white-space: normal !important;
}

/* FORCE RADIO VERTICAL */
section[data-testid="stSidebar"] div[role="radiogroup"] {
    flex-direction: column !important;
}

/* ===== DATE GRID (2 ROWS) ===== */
[data-testid="stRadio"] > div {
    display: grid !important;
    grid-template-columns: repeat(7,1fr) !important;
    gap: 4px;
}

/* ===== HEADER (FROZEN) ===== */
.header-row {
    position: sticky;
    top: 70px;
    z-index: 10;
    background: #111;
    color: white;
    padding: 6px;
    border-radius: 6px;
    text-align: center;
    font-size: 13px;
}

/* ===== SLOT ROW ===== */
.slot-row {
    display: flex;
    gap: 4px;
    margin-bottom: 2px;
}

/* ===== SLOT ===== */
.slot {
    flex: 1;
    display: flex;
    align-items: center;
    justify-content: space-between;

    padding: 2px 6px;
    height: 28px;

    border-radius: 999px;
    background: #f1f3f5;

    font-size: 11px;
}

/* ===== TIME ===== */
.slot-time {
    width: 45px;
    font-weight: 600;
}

/* ===== STATUS ===== */
.slot-status {
    width: 25px;
    text-align: center;
}

/* ===== NAME ===== */
.slot-name {
    flex: 1;
    text-align: right;

    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}

/* ===== COLORS ===== */
.mine { background: #ffe3e3; }
.locked { background: #f8d7da; }
.free { background: #e6fcf5; }

/* ===== MOBILE ===== */
@media (max-width: 900px) {
    .slot {
        font-size: 9px;
        height: 24px;
    }
}

</style>
""", unsafe_allow_html=True)

# =========================
# DATE PICKER (2 ROWS)
# =========================
today = datetime.now().date()
dates = [today + timedelta(days=i) for i in range(14)]

labels = ["Today","Tomorrow"] + [d.strftime("%a %d") for d in dates[2:]]

selected = st.radio("", labels, horizontal=True)
selected_date = dates[labels.index(selected)]

# =========================
# TIME
# =========================
HOURS = []
for h in list(range(8,24)) + list(range(0,3)):
    for m in ["00","30"]:
        HOURS.append(f"{h:02d}:{m}")

# =========================
# GRID
# =========================
st.title("RESERVE TABLE")

df = load_bookings()

cols = st.columns(3)

for i, col in enumerate(cols):
    col.markdown(f"<div class='table-header'>Table {i+1}</div>", unsafe_allow_html=True)

    for t in HOURS:
        idx = HOURS.index(t)
        row_class = "row1" if (idx//4)%2==0 else "row2"

        booked = df[
            (df["Table"]==f"Table {i+1}") &
            (df["Time"]==t) &
            (df["Date"]==str(selected_date))
        ]

        key = f"{i}_{t}"

        col.markdown(f"<div class='slot {row_class}'>", unsafe_allow_html=True)

        if not booked.empty:
            name = booked.iloc[0]["Name"]

            if booked.iloc[0]["User"] == st.session_state.user:
                if col.button(f"{t} ❌ {name}", key=key):
                    df = df.drop(booked.index)
                    save_bookings(df)
                    st.rerun()
            else:
                col.button(f"{t} 🔒 {name}", key=key, disabled=True)

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

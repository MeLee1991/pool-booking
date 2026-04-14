import streamlit as st
import pandas as pd
import os
from datetime import datetime, timedelta

# Layout set to centered acts better for mobile bounds
st.set_page_config(page_title="Poolhall", layout="centered", initial_sidebar_state="collapsed")

# ===============================
# FILES & INIT
# ===============================
USERS_FILE = "users.csv"
BOOKINGS_FILE = "bookings.csv"
OWNER = "admin@gmail.com"

if not os.path.exists(USERS_FILE):
    pd.DataFrame(columns=["email","name","pw","role"]).to_csv(USERS_FILE,index=False)

if not os.path.exists(BOOKINGS_FILE):
    pd.DataFrame(columns=["user","date","table","time"]).to_csv(BOOKINGS_FILE,index=False)


def load_users():
    try:
        df = pd.read_csv(USERS_FILE)
        # If the file loaded but is missing the email column, return a blank template
        if "email" not in df.columns:
            return pd.DataFrame(columns=["email","name","pw","role"])
        return df
    except pd.errors.EmptyDataError:
        # If the file is completely empty
        return pd.DataFrame(columns=["email","name","pw","role"])

def load_bookings():
    try:
        df = pd.read_csv(BOOKINGS_FILE)
        if "user" not in df.columns:
            return pd.DataFrame(columns=["user","date","table","time"])
        return df
    except pd.errors.EmptyDataError:
        return pd.DataFrame(columns=["user","date","table","time"])

#def load_users(): return pd.read_csv(USERS_FILE)
def save_users(df): df.to_csv(USERS_FILE,index=False)
#def load_bookings(): return pd.read_csv(BOOKINGS_FILE)
def save_bookings(df): df.to_csv(BOOKINGS_FILE,index=False)


# ===============================
# CSS FIX FOR MOBILE PORTRAIT
# ===============================
st.markdown("""
<style>
/* 1. Force Streamlit columns to STAY horizontal on mobile */
[data-testid="stHorizontalBlock"] {
    flex-wrap: nowrap !important;
    gap: 4px !important;
    margin-bottom: 4px !important;
}
[data-testid="column"] {
    min-width: 0 !important;
    padding: 0 !important;
}

/* 2. Remove excess padding from the main container */
.block-container {
    padding-top: 1.5rem;
    padding-bottom: 1rem;
    padding-left: 0.5rem;
    padding-right: 0.5rem;
    max-width: 600px;
}

/* 3. Style standard buttons to act as grid slots */
.stButton > button {
    width: 100%;
    min-height: 40px;
    height: 100%;
    padding: 0 !important;
    border-radius: 6px;
}
.stButton > button p {
    font-size: 12px;
    margin: 0;
    line-height: 1.2;
}

/* 4. Custom Markdown Headers to match your image */
.grid-header {
    background-color: #111;
    color: #fff;
    text-align: center;
    border-radius: 6px;
    padding: 8px 0;
    font-size: 13px;
    font-weight: 600;
    margin-bottom: 4px;
}
.time-cell {
    background-color: #f5f5f7;
    color: #000;
    text-align: center;
    border-radius: 6px;
    padding: 8px 0;
    font-size: 12px;
    font-weight: 500;
    display: flex;
    align-items: center;
    justify-content: center;
    height: 40px;
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

if "selected_date" not in st.session_state:
    st.session_state.selected_date = datetime.now().date()

# ===============================
# LOGIN
# ===============================
if not st.session_state.user:
    st.markdown("<h2 style='text-align:center;'>🎱 Poolhall</h2>", unsafe_allow_html=True)
    email = st.text_input("Email").lower()
    name = st.text_input("Name")
    pw = st.text_input("Password", type="password")

    if st.button("Continue", use_container_width=True):
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
            new = pd.DataFrame([[email,name,pw,role]], columns=["email","name","pw","role"])
            save_users(pd.concat([users,new]))
            st.success("Registered! Press Continue again.")
    st.stop()

# ===============================
# MAIN APP UI
# ===============================
# Top Header
colA, colB = st.columns([3, 1])
with colA:
    st.markdown(f"**👤 {st.session_state.name}** | {st.session_state.selected_date}")
with colB:
    if st.button("Logout", key="logout"):
        st.session_state.clear()
        st.rerun()

if st.button("⚙️ Admin Panel", use_container_width=True):
    st.info("Admin Panel Placeholder")

st.write("") # Spacer

# ===============================
# 14-DAY DATE SELECTOR (2x7 Grid)
# ===============================
today = datetime.now().date()
dates = [today + timedelta(days=i) for i in range(14)]

for r in range(2):
    row_cols = st.columns(7)
    for i in range(7):
        day_idx = r * 7 + i
        d = dates[day_idx]
        
        # Format label (TOD, TOM, or MON, TUE, etc.)
        if d == today:
            lbl = f"TOD {d.day}"
        elif d == today + timedelta(days=1):
            lbl = f"TOM {d.day}"
        else:
            lbl = f"{d.strftime('%a').upper()} {d.day}"
            
        with row_cols[i]:
            btn_type = "primary" if d == st.session_state.selected_date else "secondary"
            if st.button(lbl, key=f"d_{d}", type=btn_type):
                st.session_state.selected_date = d
                st.rerun()

st.write("") # Spacer

# ===============================
# BOOKING GRID (Time-Row Based)
# ===============================
times = [f"{h:02d}:{m}" for h in range(6, 13) for m in ("00","30")] # Adjust range as needed
tables = ["T 1", "T 2", "T 3"]

df = load_bookings()
df_today = df[df["date"] == str(st.session_state.selected_date)]

# Black Header Row
header_cols = st.columns([1.2, 1.5, 1.5, 1.5]) # Time column slightly smaller
with header_cols[0]: st.markdown("<div class='grid-header'>Time</div>", unsafe_allow_html=True)
with header_cols[1]: st.markdown("<div class='grid-header'>T 1</div>", unsafe_allow_html=True)
with header_cols[2]: st.markdown("<div class='grid-header'>T 2</div>", unsafe_allow_html=True)
with header_cols[3]: st.markdown("<div class='grid-header'>T 3</div>", unsafe_allow_html=True)

# Loop through times to create rows
for t in times:
    row_cols = st.columns([1.2, 1.5, 1.5, 1.5])
    
    # 1. Time Column
    with row_cols[0]:
        st.markdown(f"<div class='time-cell'>{t}</div>", unsafe_allow_html=True)

    # 2. Table Columns (T1, T2, T3)
    for idx, table in enumerate(tables):
        with row_cols[idx + 1]:
            slot = df_today[(df_today["table"] == table) & (df_today["time"] == t)]
            
            if not slot.empty:
                u = slot.iloc[0]["user"]
                if u == st.session_state.user:
                    # User's booking (Blue-ish / Primary)
                    if st.button(f"X {st.session_state.name}", key=f"{table}_{t}", type="primary"):
                        data = load_bookings()
                        data = data[~((data["table"]==table) & (data["time"]==t) & (data["date"]==str(st.session_state.selected_date)))]
                        save_bookings(data)
                        st.rerun()
                else:
                    # Someone else's booking (Locked)
                    st.button("🔒", key=f"{table}_{t}", disabled=True)
            else:
                # Free slot (Green-ish / Secondary)
                if st.button("➕", key=f"{table}_{t}", type="secondary"):
                    data = load_bookings()
                    new = pd.DataFrame([[st.session_state.user, str(st.session_state.selected_date), table, t]],
                                       columns=["user","date","table","time"])
                    save_bookings(pd.concat([data, new]))
                    st.rerun()

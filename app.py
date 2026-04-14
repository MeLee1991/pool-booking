import streamlit as st
import pandas as pd
import os
from datetime import datetime, timedelta

st.set_page_config(page_title="Poolhall", layout="centered", initial_sidebar_state="collapsed")

# ===============================
# FILES & BULLETPROOF INIT
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
        if "email" not in df.columns: return pd.DataFrame(columns=["email","name","pw","role"])
        return df
    except pd.errors.EmptyDataError: return pd.DataFrame(columns=["email","name","pw","role"])

def load_bookings():
    try:
        df = pd.read_csv(BOOKINGS_FILE)
        if "user" not in df.columns: return pd.DataFrame(columns=["user","date","table","time"])
        return df
    except pd.errors.EmptyDataError: return pd.DataFrame(columns=["user","date","table","time"])
def save_users(df): df.to_csv(USERS_FILE,index=False)
def save_bookings(df): df.to_csv(BOOKINGS_FILE,index=False)

# ===============================
# AGGRESSIVE ANTI-STACKING CSS
# ===============================
st.markdown("""
<style>
/* 1. Maximize screen space */
.block-container {
    padding-top: 1rem !important;
    padding-bottom: 1rem !important;
    padding-left: 4px !important;
    padding-right: 4px !important;
    max-width: 100% !important;
}

/* 2. FORCE NO STACKING ON ALL COLUMNS */
div[data-testid="stHorizontalBlock"] {
    flex-wrap: nowrap !important;
    gap: 4px !important;
    margin-bottom: 4px !important;
    width: 100% !important;
}

/* 3. ALLOW COLUMNS TO SQUISH INSTEAD OF STACK */
div[data-testid="column"] {
    min-width: 0 !important; /* CRITICAL: removes Streamlit's mobile breakpoint */
    flex: 1 1 0% !important; 
    padding: 0 !important;
}

/* 4. BUTTON FORMATTING (Fixed sizes, truncating text) */
.stButton > button {
    width: 100% !important;
    min-height: 40px !important;
    height: 100% !important;
    padding: 0 2px !important;
    border-radius: 4px !important;
    display: flex !important;
    justify-content: center !important;
    align-items: center !important;
}

.stButton > button p {
    font-size: 11px !important;
    font-weight: 600 !important;
    margin: 0 !important;
    white-space: nowrap !important;
    overflow: hidden !important;
    text-overflow: ellipsis !important; /* Adds "..." if name is too long */
}

/* 5. CUSTOM HEADERS & TIME CELLS */
.grid-header {
    background-color: #111;
    color: #fff;
    text-align: center;
    border-radius: 4px;
    padding: 8px 0;
    font-size: 12px;
    font-weight: 700;
}

.time-cell {
    color: #111;
    text-align: center;
    border-radius: 4px;
    font-size: 12px;
    font-weight: 600;
    display: flex;
    align-items: center;
    justify-content: center;
    height: 100%;
    min-height: 40px;
    width: 100%;
}
/* 4-Hour Block Colors */
.time-bg-white { background-color: #ffffff; border: 1px solid #eee; }
.time-bg-gray { background-color: #f2f4f7; border: 1px solid #eee; }

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
            else: st.error("Wrong password")
        else:
            role = "admin" if email == OWNER else "user"
            new = pd.DataFrame([[email,name,pw,role]], columns=["email","name","pw","role"])
            save_users(pd.concat([users,new]))
            st.success("Registered! Press Continue again.")
    st.stop()

# ===============================
# TOP HEADER
# ===============================
colA, colB = st.columns([3, 1])
with colA: st.markdown(f"**👤 {st.session_state.name}** | {st.session_state.selected_date}")
with colB:
    if st.button("Logout", key="logout"):
        st.session_state.clear()
        st.rerun()

if st.button("⚙️ Admin Panel"):
    pass # Placeholder

st.write("") # Spacer

# ===============================
# DATE SELECTOR (2 Rows of 7)
# ===============================
today = datetime.now().date()
dates = [today + timedelta(days=i) for i in range(14)]

for r in range(2):
    row_cols = st.columns(7)
    for i in range(7):
        d = dates[r * 7 + i]
        
        if d == today: lbl = f"TOD {d.day}"
        elif d == today + timedelta(days=1): lbl = f"TOM {d.day}"
        else: lbl = f"{d.strftime('%a').upper()} {d.day}"
        
        with row_cols[i]:
            if st.button(lbl, key=f"d_{d}", type="primary" if d == st.session_state.selected_date else "secondary"):
                st.session_state.selected_date = d
                st.rerun()
st.write("") # Spacer

# ===============================
# MAIN GRID
# ===============================
times = [f"{h:02d}:{m}" for h in range(6, 24) for m in ("00","30")]
tables = ["T1", "T2", "T3"]

df = load_bookings()
df_today = df[df["date"] == str(st.session_state.selected_date)]

# Strict 4 equal columns for header
header_cols = st.columns(4) 
with header_cols[0]: st.markdown("<div class='grid-header'>Time</div>", unsafe_allow_html=True)
with header_cols[1]: st.markdown("<div class='grid-header'>T1</div>", unsafe_allow_html=True)
with header_cols[2]: st.markdown("<div class='grid-header'>T2</div>", unsafe_allow_html=True)
with header_cols[3]: st.markdown("<div class='grid-header'>T3</div>", unsafe_allow_html=True)

for t in times:
    row_cols = st.columns(4)
    
    # Calculate 4-hour blocks: (Hour - 6) // 4
    hour = int(t[:2])
    block_index = (hour - 6) // 4
    bg_color = "time-bg-white" if block_index % 2 == 0 else "time-bg-gray"
    
    with row_cols[0]:
        st.markdown(f"<div class='time-cell {bg_color}'>{t}</div>", unsafe_allow_html=True)

    for idx, table in enumerate(tables):
        with row_cols[idx + 1]:
            slot = df_today[(df_today["table"] == table) & (df_today["time"] == t)]
            
            if not slot.empty:
                u = slot.iloc[0]["user"]
                display_name = st.session_state.name if u == st.session_state.user else "🔒"
                
                if u == st.session_state.user:
                    if st.button(f"X {display_name}", key=f"{table}_{t}", type="primary"):
                        data = load_bookings()
                        data = data[~((data["table"]==table) & (data["time"]==t) & (data["date"]==str(st.session_state.selected_date)))]
                        save_bookings(data)
                        st.rerun()
                else:
                    st.button("🔒", key=f"{table}_{t}", disabled=True)
            else:
                if st.button("➕", key=f"{table}_{t}", type="secondary"):
                    data = load_bookings()
                    new = pd.DataFrame([[st.session_state.user, str(st.session_state.selected_date), table, t]], columns=["user","date","table","time"])
                    save_bookings(pd.concat([data, new]))
                    st.rerun()

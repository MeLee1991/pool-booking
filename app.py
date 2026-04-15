import streamlit as st
import pandas as pd
import os
from datetime import datetime, timedelta

# ===============================
# CONFIG & FILES
# ===============================
st.set_page_config(page_title="Poolhall", layout="centered", initial_sidebar_state="collapsed")

USERS_FILE = "users.csv"
BOOKINGS_FILE = "bookings.csv"
OWNER_EMAIL = "admin@gmail.com"

# ===============================
# THE REPAIRED CSS
# ===============================
st.markdown("""
<style>
    .block-container { padding: 1rem 5px !important; max-width: 100% !important; }
    
    /* Date Selector - allow horizontal scroll */
    div[data-testid="stHorizontalBlock"]:has(> div:nth-child(7):last-child) {
        display: flex !important;
        flex-wrap: nowrap !important;
        overflow-x: auto !important;
        padding-bottom: 8px !important;
        gap: 6px !important;
    }
    div[data-testid="stHorizontalBlock"]:has(> div:nth-child(7):last-child) > div {
        min-width: 82px !important;
        flex: 0 0 auto !important;
    }

    /* ALL BUTTONS - Center Aligned */
    .stButton > button {
        height: 44px !important; 
        border-radius: 6px !important;
        padding: 0 2px !important;
        display: flex !important;
        justify-content: center !important;
        align-items: center !important;
    }
    .stButton > button p {
        font-size: 11px !important; 
        font-weight: bold !important;
        margin: 0 !important;
        text-align: center !important;
    }

    /* MAIN TABLE BUTTONS - Light Green / Light Red */
    div[data-testid="stHorizontalBlock"]:has(> div:nth-child(4):last-child) button[kind="secondary"] { 
        background-color: #c8e6c9 !important; /* Light Green */
        color: #000 !important; 
        border: 1px solid #a5d6a7 !important;
    }
    div[data-testid="stHorizontalBlock"]:has(> div:nth-child(4):last-child) button[kind="primary"] { 
        background-color: #ffcdd2 !important; /* Light Red */
        color: #000 !important; 
        border: 1px solid #ef9a9a !important;
    }

    /* DATE SELECTOR BUTTONS - Standard Colors */
    div[data-testid="stHorizontalBlock"]:has(> div:nth-child(7):last-child) button[kind="secondary"] {
        background-color: #f1f3f4 !important; color: #000 !important; border: 1px solid #ddd !important;
    }
    div[data-testid="stHorizontalBlock"]:has(> div:nth-child(7):last-child) button[kind="primary"] {
        background-color: #007bff !important; color: white !important; border: none !important;
    }
    
    /* Table Headers */
    .grid-header {
        text-align: center; font-size: 11px; font-weight: bold; 
        height: 44px; line-height: 44px; border-radius: 6px; 
        margin-bottom: 4px !important;
        background-color: #111; color: #fff;
    }
    
    /* Time Column Base Styling */
    .time-label {
        text-align: center; font-size: 11px; font-weight: bold; 
        height: 44px; line-height: 44px; border-radius: 6px; 
        margin-bottom: 4px !important; color: #222;
    }
    
    /* Time Column - 4 Hour Alternating Blocks */
    .time-block-0 { background-color: #e3f2fd; } /* 06:00 - 09:30 (Light Blue) */
    .time-block-1 { background-color: #fff3e0; } /* 10:00 - 13:30 (Light Orange) */
    .time-block-2 { background-color: #e8f5e9; } /* 14:00 - 17:30 (Light Green) */
    .time-block-3 { background-color: #f3e5f5; } /* 18:00 - 21:30 (Light Purple) */
    .time-block-4 { background-color: #fce4ec; } /* 22:00 - 23:30 (Light Pink) */
    
    [data-testid="stHeader"] {display: none;}
</style>
""", unsafe_allow_html=True)

# ===============================
# DATA HELPERS & CALLBACKS
# ===============================
def load_data(file, cols):
    if not os.path.exists(file): 
        pd.DataFrame(columns=cols).to_csv(file, index=False)
    try: 
        return pd.read_csv(file)
    except: 
        return pd.DataFrame(columns=cols)

def save_data(df, file): 
    df.to_csv(file, index=False)

def set_date(new_date):
    st.session_state.sel_date = new_date

def handle_booking(date_str, table, time_str, user_email, role):
    df = load_data(BOOKINGS_FILE, ["user", "date", "table", "time"])
    mask = (df["date"] == date_str) & (df["table"] == table) & (df["time"] == time_str)
    
    if df[mask].empty:
        new_row = pd.DataFrame([[user_email, date_str, table, time_str]], columns=df.columns)
        df = pd.concat([df, new_row], ignore_index=True)
    else:
        owner = df[mask].iloc[0]["user"]
        if owner == user_email or role == "admin":
            df = df[~mask]
            
    save_data(df, BOOKINGS_FILE)

# Initialize files
load_data(USERS_FILE, ["email", "password", "role"])
bookings_df = load_data(BOOKINGS_FILE, ["user", "date", "table", "time"])

# ===============================
# LOGIN SYSTEM
# ===============================
if "user" not in st.session_state:
    st.markdown("<h2 style='text-align:center;'>🎱 Pool Login</h2>", unsafe_allow_html=True)
    email = st.text_input("Email").lower()
    pw = st.text_input("Password", type="password")
    
    if st.button("Continue", use_container_width=True):
        users_df = load_data(USERS_FILE, ["email", "password", "role"])
        
        # Hardcoded admin override for first setup
        if email == OWNER_EMAIL and pw == "1234":
            st.session_state.user = email
            st.session_state.name = "Admin"
            st.session_state.role = "admin"
            st.rerun()
            
        # Check against users.csv
        elif not users_df[(users_df["email"] == email) & (users_df["password"] == pw)].empty:
            user_data = users_df[users_df["email"] == email].iloc[0]
            st.session_state.user = email
            st.session_state.name = email.split('@')[0].capitalize()
            st.session_state.role = user_data["role"]
            st.rerun()
        else:
            st.error("Invalid credentials or user does not exist.")
    st.stop()

# ===============================
# MAIN UI WITH TABS
# ===============================
if "sel_date" not in st.session_state: 
    st.session_state.sel_date = datetime.now().date()

st.markdown(f"**👤 {st.session_state.name}** &nbsp;|&nbsp; {st.session_state.sel_date}")

# Decide if we show tabs (for admin) or just the booking view
if st.session_state.role == "admin":
    tab_booking, tab_admin = st.tabs(["🎱 Bookings", "⚙️ Admin Dashboard"])
else:
    tab_booking, tab_admin = st.tabs(["🎱 Bookings"]), None

# ===============================
# BOOKING TAB
# ===============================
with tab_booking:
    # 14-DAY SELECTOR
    today = datetime.now().date()
    dates = [today + timedelta(days=i) for i in range(14)]

    for row_start in [0, 7]:
        d_cols = st.columns(7)
        for i in range(7):
            d = dates[row_start + i]
            lbl = f"TOD\n{d.day}" if d == today else f"TOM\n{d.day}" if d == today + timedelta(days=1) else f"{d.strftime('%a').upper()}\n{d.day}"
            with d_cols[i]:
                st.button(lbl, key=f"date_{d}", type="primary" if d == st.session_state.sel_date else "secondary", on_click=set_date, args=(d,), use_container_width=True)

    st.divider()

    # MAIN TABLE
    times = [f"{h:02d}:{m}" for h in range(6, 24) for m in ("00","30")]
    tables = ["T1", "T2", "T3"]
    
    # Reload fresh bookings
    bookings = load_data(BOOKINGS_FILE, ["user", "date", "table", "time"])
    date_str = str(st.session_state.sel_date)
    df_day = bookings[bookings["date"] == date_str]

    # TABLE HEADER
    h_cols = st.columns(4)
    for title in ["Time", "T1", "T2", "T3"]:
        with h_cols[["Time", "T1", "T2", "T3"].index(title)]:
            st.markdown(f"<div class='grid-header'>{title}</div>", unsafe_allow_html=True)

    # TABLE DATA
    for t in times:
        r_cols = st.columns(4)
        
        # Calculate which 4-hour block this time belongs to
        hour = int(t.split(":")[0])
        block_idx = (hour - 6) // 4
        
        with r_cols[0]:
            st.markdown(f"<div class='time-label time-block-{block_idx}'>{t}</div>", unsafe_allow_html=True)
            
        for i, table in enumerate(tables):
            with r_cols[i+1]:
                match = df_day[(df_day["table"] == table) & (df_day["time"] == t)]
                btn_key = f"btn_{date_str}_{table}_{t}" 
                
                if not match.empty:
                    owner = match.iloc[0]["user"]
                    is_me_or_admin = (owner == st.session_state.user) or (st.session_state.role == "admin")
                    display_name = owner.split("@")[0].capitalize()[:6] if is_me_or_admin else ""
                    label = f"X {display_name}" if is_me_or_admin else "🔒"
                    st.button(label, key=btn_key, type="primary", on_click=handle_booking, args=(date_str, table, t, st.session_state.user, st.session_state.role), use_container_width=True)
                else:
                    st.button("➕", key=btn_key, type="secondary", on_click=handle_booking, args=(date_str, table, t, st.session_state.user, st.session_state.role), use_container_width=True)

# ===============================
# ADMIN TAB
# ===============================
if tab_admin:
    with tab_admin:
        st.subheader("Manage Users")
        users_df = load_data(USERS_FILE, ["email", "password", "role"])
        
        edited_users = st.data_editor(
            users_df, 
            num_rows="dynamic", 
            use_container_width=True,
            key="user_editor"
        )
        if st.button("Save User Changes", use_container_width=True):
            save_data(edited_users, USERS_FILE)
            st.success("Users updated successfully!")

        st.divider()

        st.subheader("Booking Statistics")
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Bookings", len(bookings))
        
        if not bookings.empty:
            top_table = bookings["table"].mode()[0]
            busiest_day = bookings["date"].mode()[0]
        else:
            top_table = "N/A"
            busiest_day = "N/A"
            
        col2.metric("Most Popular Table", top_table)
        col3.metric("Busiest Day", busiest_day)

        st.divider()

        st.subheader("Download History")
        with open(BOOKINGS_FILE, "rb") as file:
            st.download_button(
                label="📥 Download Bookings CSV",
                data=file,
                file_name="poolhall_history.csv",
                mime="text/csv",
                use_container_width=True
            )

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
# THE FIX: COLOR SCHEME CSS
# ===============================
st.markdown("""
<style>
    .block-container { padding: 1rem 5px !important; max-width: 100% !important; }
    
    /* Booking Grid Styling */
    /* Free Slots: Light Green */
    div[data-testid="stButton"] > button[kind="secondary"] {
        background-color: #e8f5e9 !important; /* Light Green */
        color: #2e7d32 !important;
        border: 1px solid #c8e6c9 !important;
    }
    
    /* Booked Slots: Light Red */
    div[data-testid="stButton"] > button[kind="primary"] {
        background-color: #ffebee !important; /* Light Red */
        color: #c62828 !important;
        border: 1px solid #ffcdd2 !important;
    }

    /* Column alignment for mobile */
    div[data-testid="stHorizontalBlock"]:has(> div:nth-child(4):last-child) {
        display: grid !important; grid-template-columns: repeat(4, 1fr) !important;
        gap: 4px !important; margin-bottom: 4px !important;
    }
    .stButton > button {
        height: 44px !important; border-radius: 6px !important;
        width: 100% !important; font-size: 11px !important; font-weight: bold !important;
    }
    .grid-header {
        text-align: center; font-size: 11px; font-weight: bold; 
        height: 44px; line-height: 44px; border-radius: 6px; 
        background-color: #333; color: white;
    }
    .time-label {
        text-align: center; font-size: 11px; font-weight: bold; 
        height: 44px; line-height: 44px; border-radius: 6px; background-color: #f0f2f6;
    }
    [data-testid="stHeader"] {display: none;}
</style>
""", unsafe_allow_html=True)

# ===============================
# DATA ENGINES
# ===============================
USER_COLS = ["email", "password", "role", "approved", "info"]
BOOK_COLS = ["user", "date", "table", "time"]

def load_data(file, cols):
    if not os.path.exists(file) or os.path.getsize(file) == 0:
        df = pd.DataFrame(columns=cols)
        if file == USERS_FILE:
            df = pd.DataFrame([[OWNER_EMAIL, "1234", "admin", "True", ""]], columns=cols)
        df.to_csv(file, index=False)
        return df
    try:
        df = pd.read_csv(file, dtype=str).fillna("")
        for c in cols:
            if c not in df.columns: df[c] = "True" if c == "approved" else ""
        return df[cols]
    except:
        return pd.DataFrame(columns=cols)

def save_data(df, file):
    df.to_csv(file, index=False)

def handle_booking(date_str, table, time_str):
    target = st.session_state.get("admin_target_user", st.session_state.user)
    df = load_data(BOOKINGS_FILE, BOOK_COLS)
    mask = (df["date"] == str(date_str)) & (df["table"] == str(table)) & (df["time"] == str(time_str))
    
    if df[mask].empty:
        new_row = pd.DataFrame([[target, date_str, table, time_str]], columns=BOOK_COLS)
        df = pd.concat([df, new_row], ignore_index=True)
    else:
        owner = str(df[mask].iloc[0]["user"])
        if owner.lower() == st.session_state.user.lower() or st.session_state.role == "admin": 
            df = df[~mask]
    save_data(df, BOOKINGS_FILE)

# ===============================
# LOGIN
# ===============================
if "user" not in st.session_state:
    st.markdown("<h3 style='text-align:center;'>🎱 Pool Login</h3>", unsafe_allow_html=True)
    l_user = st.text_input("User").lower().strip()
    l_pw = st.text_input("Password", type="password").strip()
    if st.button("Log In", use_container_width=True):
        u_df = load_data(USERS_FILE, USER_COLS)
        match = u_df[(u_df["email"] == l_user) & (u_df["password"] == l_pw)]
        if not match.empty:
            st.session_state.user = l_user
            st.session_state.role = match.iloc[0]["role"]
            st.rerun()
        else: st.error("Invalid credentials.")
    st.stop()

# ===============================
# UI
# ===============================
if "sel_date" not in st.session_state: st.session_state.sel_date = datetime.now().date()
tab_booking, tab_admin = st.tabs(["🎱 Bookings", "⚙️ Admin"]) if st.session_state.role == "admin" else (st.tabs(["🎱 Bookings"])[0], None)

with tab_booking:
    # Date selection logic here...
    st.write(f"**Admin | {st.session_state.sel_date}**")
    
    h_cols = st.columns(4)
    for i, title in enumerate(["Time", "T1", "T2", "T3"]):
        with h_cols[i]: st.markdown(f"<div class='grid-header'>{title}</div>", unsafe_allow_html=True)

    times = [f"{h:02d}:{m}" for h in range(6, 24) for m in ("00","30")]
    bookings = load_data(BOOKINGS_FILE, BOOK_COLS)
    df_day = bookings[bookings["date"] == str(st.session_state.sel_date)]

    for t in times:
        r_cols = st.columns(4)
        with r_cols[0]: st.markdown(f"<div class='time-label'>{t}</div>", unsafe_allow_html=True)
        for i, table in enumerate(["T1", "T2", "T3"]):
            with r_cols[i+1]:
                match = df_day[(df_day["table"] == table) & (df_day["time"] == t)]
                if not match.empty:
                    owner = str(match.iloc[0]["user"]).split('@')[0].capitalize()
                    st.button(owner, key=f"{table}{t}", type="primary", on_click=handle_booking, args=(str(st.session_state.sel_date), table, t))
                else:
                    st.button("➕", key=f"{table}{t}", type="secondary", on_click=handle_booking, args=(str(st.session_state.sel_date), table, t))

if tab_admin:
    with tab_admin:
        u_df = load_data(USERS_FILE, USER_COLS)
        st.subheader("👥 User Management")
        
        # SPREADSHEET VIEW RESTORED
        u_df["approved"] = u_df["approved"].astype(str).str.lower().isin(["true", "1", "yes"])
        edited_df = st.data_editor(
            u_df, 
            num_rows="dynamic", 
            use_container_width=True, 
            key="user_editor",
            column_config={
                "approved": st.column_config.CheckboxColumn("Approve"),
                "info": st.column_config.TextColumn("Info (Text/Links)")
            }
        )
        
        if st.button("💾 Save User Changes", use_container_width=True):
            save_data(edited_df, USERS_FILE)
            st.success("Users Updated!")
            st.rerun()

        st.divider()
        st.session_state.admin_target_user = st.selectbox("Book for user:", u_df["email"].tolist())

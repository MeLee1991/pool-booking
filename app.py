import streamlit as st
import pandas as pd
import os
from datetime import datetime

# ===============================
# CONFIG & FILES
# ===============================
st.set_page_config(page_title="Poolhall", layout="centered", initial_sidebar_state="collapsed")

USERS_FILE = "users.csv"
BOOKINGS_FILE = "bookings.csv"
OWNER_EMAIL = "admin@gmail.com"

# ===============================
# RESTORED & CORRECTED CSS
# ===============================
st.markdown("""
<style>
    /* Center the main container */
    .block-container { 
        padding: 1rem 10px !important; 
        max-width: 500px !important; 
        margin: auto !important; 
    }
    
    /* 4-Column Grid Layout */
    div[data-testid="stHorizontalBlock"] {
        display: grid !important; 
        grid-template-columns: repeat(4, 1fr) !important;
        gap: 6px !important; 
        margin-bottom: 6px !important;
        align-items: center !important;
    }

    /* Headers (T1, T2, T3) */
    .grid-header {
        text-align: center; font-size: 12px; font-weight: 800; 
        background-color: #333333 !important; color: white !important; 
        border-radius: 8px; height: 45px; line-height: 45px;
    }

    /* Time Labels (Left Column) */
    .time-label {
        text-align: center; font-size: 11px; font-weight: 700; 
        background-color: #f1f3f6 !important; color: #333 !important; 
        border-radius: 8px; height: 45px; line-height: 45px;
    }

    /* Slot Buttons */
    .stButton > button {
        height: 45px !important; width: 100% !important; 
        border-radius: 8px !important; font-weight: bold !important;
        border: 1px solid rgba(0,0,0,0.05) !important;
    }

    /* Light Green: Available */
    div[data-testid="stHorizontalBlock"] button[kind="secondary"] { 
        background-color: #e8f5e9 !important; color: #2e7d32 !important; 
    }
    
    /* Light Red: Booked */
    div[data-testid="stHorizontalBlock"] button[kind="primary"] { 
        background-color: #ffebee !important; color: #c62828 !important; 
    }

    [data-testid="stHeader"] {display: none;}
</style>
""", unsafe_allow_html=True)

# ===============================
# DATA ENGINE
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
    df = pd.read_csv(file, dtype=str).fillna("")
    return df[cols]

def save_data(df, file):
    df.astype(str).to_csv(file, index=False)

def handle_booking(date_str, table, time_str):
    target = st.session_state.get("admin_target_user", st.session_state.user)
    df = load_data(BOOKINGS_FILE, BOOK_COLS)
    mask = (df["date"] == str(date_str)) & (df["table"] == str(table)) & (df["time"] == str(time_str))
    if df[mask].empty:
        df = pd.concat([df, pd.DataFrame([[target, date_str, table, time_str]], columns=BOOK_COLS)], ignore_index=True)
    else:
        df = df[~mask]
    save_data(df, BOOKINGS_FILE)

# ===============================
# UI LOGIC
# ===============================
if "user" not in st.session_state:
    st.markdown("<h3 style='text-align:center;'>🎱 Pool Login</h3>", unsafe_allow_html=True)
    u = st.text_input("User").strip().lower()
    p = st.text_input("Password", type="password").strip()
    if st.button("Log In", use_container_width=True):
        u_df = load_data(USERS_FILE, USER_COLS)
        match = u_df[(u_df["email"] == u) & (u_df["password"] == p)]
        if not match.empty:
            st.session_state.user, st.session_state.role = u, match.iloc[0]["role"]
            st.rerun()
    st.stop()

if "sel_date" not in st.session_state: st.session_state.sel_date = datetime.now().date()
tabs = st.tabs(["🎱 Bookings", "⚙️ Admin"]) if st.session_state.role == "admin" else [st.tabs(["🎱 Bookings"])[0]]

with tabs[0]:
    st.markdown(f"<p style='text-align:center;'><b>{st.session_state.user}</b> | {st.session_state.sel_date}</p>", unsafe_allow_html=True)
    
    # Header Row
    cols = st.columns(4)
    titles = ["Time", "T1", "T2", "T3"]
    for i, t in enumerate(titles):
        cols[i].markdown(f"<div class='grid-header'>{t}</div>", unsafe_allow_html=True)

    # Booking Grid
    times = [f"{h:02d}:{m}" for h in range(6, 24) for m in ("00","30")]
    bookings = load_data(BOOKINGS_FILE, BOOK_COLS)
    df_day = bookings[bookings["date"] == str(st.session_state.sel_date)]

    for t in times:
        cols = st.columns(4)
        cols[0].markdown(f"<div class='time-label'>{t}</div>", unsafe_allow_html=True)
        for i, table in enumerate(["T1", "T2", "T3"]):
            match = df_day[(df_day["table"] == table) & (df_day["time"] == t)]
            if not match.empty:
                name = match.iloc[0]["user"].split('@')[0]
                cols[i+1].button(name, key=f"{table}{t}", type="primary", on_click=handle_booking, args=(str(st.session_state.sel_date), table, t))
            else:
                cols[i+1].button("＋", key=f"{table}{t}", type="secondary", on_click=handle_booking, args=(str(st.session_state.sel_date), table, t))

if st.session_state.role == "admin":
    with tabs[1]:
        u_df = load_data(USERS_FILE, USER_COLS)
        u_df["approved"] = u_df["approved"].astype(str).str.lower().isin(["true", "1", "yes"])
        edited = st.data_editor(u_df, num_rows="dynamic", use_container_width=True, key="admin_table")
        if st.button("💾 Save Changes"):
            save_data(edited, USERS_FILE)
            st.rerun()
        st.session_state.admin_target_user = st.selectbox("Book for:", u_df["email"].tolist())

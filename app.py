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
# THE "STRICT GRID" CSS
# ===============================
st.markdown("""
<style>
    .block-container { padding: 1rem 5px !important; max-width: 100% !important; }
    
    /* 1. DATE SELECTOR - NARROW BUTTONS */
    div[data-testid="stHorizontalBlock"]:has(> div:nth-child(7):last-child) {
        display: flex !important; flex-wrap: nowrap !important;
        overflow-x: auto !important; gap: 4px !important;
    }
    div[data-testid="stHorizontalBlock"]:has(> div:nth-child(7):last-child) button {
        max-width: 65px !important; min-width: 65px !important;
        padding: 0px !important;
    }

    /* 2. MAIN TABLE - FORCED 4 COLUMNS */
    div[data-testid="stHorizontalBlock"]:has(> div:nth-child(4):last-child) {
        display: grid !important;
        grid-template-columns: repeat(4, 1fr) !important;
        gap: 4px !important;
        margin-bottom: 4px !important;
    }
    div[data-testid="stHorizontalBlock"]:has(> div:nth-child(4):last-child) > div {
        width: 100% !important; min-width: 0 !important;
    }

    /* 3. BUTTON STYLING */
    .stButton > button {
        height: 44px !important; border-radius: 6px !important;
        display: flex !important; justify-content: center !important; align-items: center !important;
        width: 100% !important;
    }
    .stButton > button p {
        font-size: 11px !important; font-weight: bold !important;
        text-align: center !important; margin: 0 !important;
    }

    /* 4. HEADERS & LABELS */
    .grid-header {
        text-align: center; font-size: 11px; font-weight: bold; 
        height: 44px; line-height: 44px; border-radius: 6px; 
        background-color: #6c757d; color: white;
    }
    .time-label {
        text-align: center; font-size: 11px; font-weight: bold; 
        height: 44px; line-height: 44px; border-radius: 6px; color: #333;
    }
    
    /* LIGHT COLORS FOR TIME BLOCKS */
    .time-block-0 { background-color: #fff9c4 !important; } 
    .time-block-1 { background-color: #ffe0b2 !important; } 
    .time-block-2 { background-color: #e3f2fd !important; } 
    .time-block-3 { background-color: #f1f8e9 !important; } 
    .time-block-4 { background-color: #efebe9 !important; } 
    
    [data-testid="stHeader"] {display: none;}
</style>
""", unsafe_allow_html=True)

# ===============================
# DATA HELPERS
# ===============================
USER_COLS = ["email", "password", "role", "approved"]
BOOK_COLS = ["user", "date", "table", "time"]

def load_data(file, cols):
    if not os.path.exists(file):
        df = pd.DataFrame(columns=cols)
        if file == USERS_FILE:
            df = pd.DataFrame([[OWNER_EMAIL, "1234", "admin", True]], columns=cols)
        df.to_csv(file, index=False)
        return df
    df = pd.read_csv(file)
    if list(df.columns) != cols:
        df = pd.DataFrame(columns=cols)
        if file == USERS_FILE: df = pd.DataFrame([[OWNER_EMAIL, "1234", "admin", True]], columns=cols)
        df.to_csv(file, index=False)
    return df

def save_data(df, file): df.to_csv(file, index=False)

# ===============================
# AUTH SYSTEM
# ===============================
if "user" not in st.session_state:
    mode = st.radio("M", ["Login", "Register"], horizontal=True, label_visibility="collapsed")
    if mode == "Login":
        st.markdown("<h3 style='text-align:center;'>🎱 Pool Login</h3>", unsafe_allow_html=True)
        l_email = st.text_input("Email").lower()
        l_pw = st.text_input("Password", type="password")
        if st.button("Log In", use_container_width=True):
            u_df = load_data(USERS_FILE, USER_COLS)
            match = u_df[(u_df["email"] == l_email) & (u_df["password"].astype(str) == str(l_pw))]
            if not match.empty:
                if match.iloc[0]["approved"]:
                    st.session_state.user, st.session_state.role = l_email, match.iloc[0]["role"]
                    st.session_state.name = l_email.split('@')[0].capitalize()
                    st.rerun()
                else: st.warning("Pending approval.")
            else: st.error("Incorrect credentials.")
    else:
        st.markdown("<h3 style='text-align:center;'>🎱 Register</h3>", unsafe_allow_html=True)
        r_email = st.text_input("Email").lower()
        r_pw = st.text_input("Password", type="password")
        if st.button("Register", use_container_width=True):
            u_df = load_data(USERS_FILE, USER_COLS)
            if r_email in u_df["email"].values: st.error("Exists.")
            else:
                new_u = pd.DataFrame([[r_email, r_pw, "user", False]], columns=USER_COLS)
                save_data(pd.concat([u_df, new_u]), USERS_FILE)
                st.success("Wait for admin approval.")
    st.stop()

# ===============================
# TABS
# ===============================
t_names = ["🎱 Bookings", "👤 Profile"]
if st.session_state.role == "admin": t_names.append("⚙️ Admin")
tabs = st.tabs(t_names)

if "sel_date" not in st.session_state: st.session_state.sel_date = datetime.now().date()

with tabs[0]:
    today = datetime.now().date()
    tomorrow = today + timedelta(days=1)
    dates = [today + timedelta(days=i) for i in range(14)]
    for row_start in [0, 7]:
        d_cols = st.columns(7)
        for i in range(7):
            d = dates[row_start + i]
            lbl = "TOD" if d == today else "TOM" if d == tomorrow else d.strftime('%a').upper()
            lbl += f"\n{d.day}"
            with d_cols[i]:
                if st.button(lbl, key=f"d_{d}", type="primary" if d == st.session_state.sel_date else "secondary"):
                    st.session_state.sel_date = d
                    st.rerun()

    st.divider()

    h_cols = st.columns(4)
    for i, title in enumerate(["Time", "T1", "T2", "T3"]):
        with h_cols[i]: st.markdown(f"<div class='grid-header'>{title}</div>", unsafe_allow_html=True)

    bookings = load_data(BOOKINGS_FILE, BOOK_COLS)
    df_day = bookings[bookings["date"] == str(st.session_state.sel_date)]
    times = [f"{h:02d}:{m}" for h in range(6, 24) for m in ("00","30")]

    for t in times:
        r_cols = st.columns(4)
        block = (int(t.split(":")[0]) - 6) // 4
        with r_cols[0]: st.markdown(f"<div class='time-label time-block-{block}'>{t}</div>", unsafe_allow_html=True)
        for i, table in enumerate(["T1", "T2", "T3"]):
            with r_cols[i+1]:
                match = df_day[(df_day["table"] == table) & (df_day["time"] == t)]
                btn_key = f"b_{st.session_state.sel_date}_{table}_{t}"
                if not match.empty:
                    owner = match.iloc[0]["user"]
                    name = owner.split('@')[0].capitalize()[:7]
                    if st.button(name, key=btn_key, type="primary"):
                        if owner == st.session_state.user or st.session_state.role == "admin":
                            bookings = bookings[~((bookings["date"] == str(st.session_state.sel_date)) & (bookings["table"] == table) & (bookings["time"] == t))]
                            save_data(bookings, BOOKINGS_FILE)
                            st.rerun()
                else:
                    if st.button("➕", key=btn_key, type="secondary"):
                        new_b = pd.DataFrame([[st.session_state.user, str(st.session_state.sel_date), table, t]], columns=BOOK_COLS)
                        save_data(pd.concat([bookings, new_b]), BOOKINGS_FILE)
                        st.rerun()

with tabs[1]:
    st.subheader("Update Password")
    p1 = st.text_input("New Password", type="password")
    if st.button("Save Password", use_container_width=True):
        u_df = load_data(USERS_FILE, USER_COLS)
        u_df.loc[u_df["email"] == st.session_state.user, "password"] = p1
        save_data(u_df, USERS_FILE)
        st.success("Updated!")

if st.session_state.role == "admin":
    with tabs[2]:
        st.subheader("📊 Statistics")
        if not bookings.empty:
            stats = bookings.groupby("user").size().reset_index(name="Total").sort_values("Total", ascending=False)
            st.dataframe(stats, hide_index=True, use_container_width=True)
        
        st.divider()
        st.subheader("👥 Approvals")
        u_df = load_data(USERS_FILE, USER_COLS)
        edited = st.data_editor(u_df, use_container_width=True, column_config={
            "role": st.column_config.SelectboxColumn("Role", options=["user", "admin"]),
            "approved": st.column_config.CheckboxColumn("Approved")
        })
        if st.button("💾 Save All Changes", use_container_width=True):
            save_data(edited, USERS_FILE)
            st.rerun()

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
# RESTORED "AWESOME" DESIGN + FROZEN HEADER
# ===============================
st.markdown("""
<style>
    .block-container { padding: 1rem 5px !important; max-width: 100% !important; }
    
    /* Horizontal Date Selector (Restored) */
    div[data-testid="stHorizontalBlock"]:has(> div:nth-child(7):last-child) {
        display: flex !important; flex-wrap: nowrap !important;
        overflow-x: auto !important; gap: 6px !important;
    }
    div[data-testid="stHorizontalBlock"]:has(> div:nth-child(7):last-child) > div {
        min-width: 85px !important; flex: 0 0 auto !important;
    }

    /* Frozen Header Column Logic */
    div[data-testid="stHorizontalBlock"]:has(.grid-header) {
        position: sticky !important;
        top: 0;
        z-index: 1000;
        background-color: white !important;
        padding-bottom: 10px !important; /* Spacing away from data */
        margin-bottom: 5px !important;
    }

    /* 4-Column Grid */
    div[data-testid="stHorizontalBlock"]:has(> div:nth-child(4):last-child) {
        display: grid !important; grid-template-columns: repeat(4, 1fr) !important;
        gap: 4px !important; margin-bottom: 4px !important;
    }
    div[data-testid="stHorizontalBlock"]:has(> div:nth-child(4):last-child) > div {
        width: 100% !important; min-width: 0 !important;
    }

    /* Buttons */
    .stButton > button {
        height: 44px !important; border-radius: 6px !important;
        display: flex !important; justify-content: center !important; align-items: center !important;
        width: 100% !important;
    }
    .stButton > button p {
        font-size: 11px !important; font-weight: bold !important;
        text-align: center !important; margin: 0 !important;
    }

    /* Colors */
    button[kind="secondary"] { background-color: #e8f5e9 !important; color: #2e7d32 !important; border: 1px solid #c8e6c9 !important; }
    button[kind="primary"] { background-color: #ffebee !important; color: #c62828 !important; border: 1px solid #ffcdd2 !important; }

    .grid-header {
        text-align: center; font-size: 11px; font-weight: bold; 
        height: 44px; line-height: 44px; border-radius: 6px; 
        background-color: #343a40; color: white;
    }
    .time-label {
        text-align: center; font-size: 11px; font-weight: bold; 
        height: 44px; line-height: 44px; border-radius: 6px; color: #333;
    }

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

def load_data(file, cols):
    if not os.path.exists(file):
        df = pd.DataFrame(columns=cols)
        if file == USERS_FILE:
            df = pd.DataFrame([[OWNER_EMAIL, "1234", "admin", "True"]], columns=cols)
        df.to_csv(file, index=False)
    return pd.read_csv(file, dtype=str).fillna("")

def save_data(df, file):
    df.astype(str).to_csv(file, index=False)

def handle_booking(date_str, table, time_str):
    df = load_data(BOOKINGS_FILE, ["user", "date", "table", "time"])
    mask = (df["date"] == str(date_str)) & (df["table"] == str(table)) & (df["time"] == str(time_str))
    
    # Logic: If Admin has "Book for User" selected, use that. Otherwise use current user.
    active_user = st.session_state.get("admin_book_for", st.session_state.user)

    if df[mask].empty:
        new_row = pd.DataFrame([[active_user, date_str, table, time_str]], columns=df.columns)
        df = pd.concat([df, new_row], ignore_index=True)
    else:
        # If Admin, they can delete anyone's booking. Users can only delete their own.
        owner = df[mask].iloc[0]["user"]
        if owner == st.session_state.user or st.session_state.role == "admin":
            df = df[~mask]
    save_data(df, BOOKINGS_FILE)

# ===============================
# AUTHENTICATION
# ===============================
if "user" not in st.session_state:
    st.markdown("<h3 style='text-align:center;'>🎱 Poolhall Login</h3>", unsafe_allow_html=True)
    l_user = st.text_input("Username").strip().lower()
    l_pw = st.text_input("Password", type="password").strip()
    c1, c2 = st.columns(2)
    if c1.button("Login", use_container_width=True):
        u_df = load_data(USERS_FILE, USER_COLS)
        match = u_df[(u_df["email"].str.lower() == l_user) & (u_df["password"].astype(str) == str(l_pw))]
        if not match.empty and str(match.iloc[0]["approved"]).lower() == "true":
            st.session_state.user = l_user
            st.session_state.role = str(match.iloc[0]["role"]).lower()
            st.session_state.name = l_user.split('@')[0].capitalize()
            st.rerun()
        else: st.error("Invalid or Pending Approval.")
    if c2.button("Register", use_container_width=True):
        u_df = load_data(USERS_FILE, USER_COLS)
        if l_user and l_pw:
            new_entry = pd.DataFrame([[l_user, l_pw, "user", "False"]], columns=USER_COLS)
            save_data(pd.concat([u_df, new_entry], ignore_index=True), USERS_FILE)
            st.success("Registered! Wait for Admin.")
    st.stop()

# ===============================
# MAIN INTERFACE
# ===============================
if "sel_date" not in st.session_state: st.session_state.sel_date = datetime.now().date()

# Tab switching
tab_booking, tab_admin = st.tabs(["🎱 Bookings", "⚙️ Admin"]) if st.session_state.role == "admin" else [st.tabs(["🎱 Bookings"])[0], None]

with tab_booking:
    st.write(f"**👤 {st.session_state.name}** | {st.session_state.sel_date}")
    
    # 1. Restored Horizontal Dates
    today = datetime.now().date()
    dates = [today + timedelta(days=i) for i in range(14)]
    d_cols = st.columns(7) # First 7 days
    for i in range(7):
        d = dates[i]
        with d_cols[i]:
            if st.button(f"{d.strftime('%a')}\n{d.day}", key=f"d_{d}", type="primary" if d == st.session_state.sel_date else "secondary", use_container_width=True):
                st.session_state.sel_date = d
                st.rerun()

    st.divider()

    # 2. Frozen Header Row
    h_cols = st.columns(4)
    for i, title in enumerate(["Time", "T1", "T2", "T3"]):
        h_cols[i].markdown(f"<div class='grid-header'>{title}</div>", unsafe_allow_html=True)

    # 3. Grid
    times = [f"{h:02d}:{m}" for h in range(6, 24) for m in ("00","30")]
    bookings = load_data(BOOKINGS_FILE, ["user", "date", "table", "time"])
    df_day = bookings[bookings["date"] == str(st.session_state.sel_date)]

    for t in times:
        r_cols = st.columns(4)
        block_idx = (int(t.split(":")[0]) - 6) // 4
        r_cols[0].markdown(f"<div class='time-label time-block-{block_idx}'>{t}</div>", unsafe_allow_html=True)
        for i, table in enumerate(["T1", "T2", "T3"]):
            match = df_day[(df_day["table"] == table) & (df_day["time"] == t)]
            btn_key = f"btn_{st.session_state.sel_date}_{table}_{t}"
            if not match.empty:
                name = match.iloc[0]["user"].split('@')[0].capitalize()[:7]
                r_cols[i+1].button(name, key=btn_key, type="primary", on_click=handle_booking, args=(str(st.session_state.sel_date), table, t), use_container_width=True)
            else:
                r_cols[i+1].button("➕", key=btn_key, type="secondary", on_click=handle_booking, args=(str(st.session_state.sel_date), table, t), use_container_width=True)

if tab_admin:
    with tab_admin:
        u_df = load_data(USERS_FILE, USER_COLS)
        
        # Stats
        st.subheader("📊 Stats")
        c1, c2 = st.columns(2)
        c1.metric("Total Users", len(u_df))
        c2.metric("Total Bookings", len(load_data(BOOKINGS_FILE, [])))

        # Admin Booking Power
        st.subheader("🎯 Admin Booking Tool")
        user_list = u_df["email"].tolist()
        st.session_state.admin_book_for = st.selectbox("Select user to book for (Go back to Bookings tab after selecting):", user_list, index=user_list.index(st.session_state.user))

        # CSV Upload
        with st.expander("📥 Import Users via CSV"):
            up = st.file_uploader("Upload CSV (email,password,role,approved)")
            if up:
                csv_df = pd.read_csv(up)
                save_data(pd.concat([u_df, csv_df]).drop_duplicates(subset=['email']), USERS_FILE)
                st.success("Imported!")

        # Sortable User Management
        st.subheader("👥 User Management Table")
        u_df["approved"] = u_df["approved"].astype(str).str.lower().isin(["true", "1", "yes"])
        edited = st.data_editor(u_df, use_container_width=True, num_rows="dynamic",
                               column_config={"approved": st.column_config.CheckboxColumn("Approve"),
                                              "role": st.column_config.SelectboxColumn("Role", options=["user", "admin"])})
        
        if st.button("💾 Save All User Changes"):
            save_data(edited, USERS_FILE)
            st.rerun()

        if st.button("🔑 Set All Passwords to '1234'"):
            u_df["password"] = "1234"
            save_data(u_df, USERS_FILE)
            st.rerun()

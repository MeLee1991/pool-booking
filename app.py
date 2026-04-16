import streamlit as st
import pandas as pd
import os
from datetime import datetime, timedelta

# ===============================
# CONFIG & FILES
# ===============================
st.set_page_config(page_title="Poolhall Pro", layout="centered", initial_sidebar_state="collapsed")

USERS_FILE = "users.csv"
BOOKINGS_FILE = "bookings.csv"
OWNER_EMAIL = "admin@gmail.com"

# ===============================
# DESIGN: FROZEN HEADERS & SPACING
# ===============================
st.markdown("""
<style>
    .block-container { padding: 1rem 5px !important; max-width: 100% !important; }
    
    /* Sticky Frozen Header Logic */
    .stHorizontalBlock:has(.grid-header) {
        position: sticky !important;
        top: 0;
        z-index: 999;
        background-color: white;
        padding-bottom: 10px !important; /* Extra distance from data */
    }

    /* Grid Layout */
    div[data-testid="stHorizontalBlock"]:has(> div:nth-child(4):last-child) {
        display: grid !important; grid-template-columns: repeat(4, 1fr) !important;
        gap: 4px !important; margin-bottom: 4px !important;
    }
    
    /* Button Width Fix */
    .stButton > button {
        height: 44px !important; border-radius: 6px !important;
        display: flex !important; justify-content: center !important; align-items: center !important;
        width: 100% !important;
    }
    .stButton > button p {
        font-size: 11px !important; font-weight: bold !important;
        text-align: center !important; margin: 0 !important;
    }

    /* Design Colors */
    button[kind="secondary"] { background-color: #e8f5e9 !important; color: #2e7d32 !important; border: 1px solid #c8e6c9 !important; }
    button[kind="primary"] { background-color: #ffebee !important; color: #c62828 !important; border: 1px solid #ffcdd2 !important; }

    .grid-header {
        text-align: center; font-size: 11px; font-weight: bold; 
        height: 44px; line-height: 44px; border-radius: 6px; 
        background-color: #6c757d; color: white;
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
# DATA LOGIC
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

def handle_booking(date_str, table, time_str, user_email, role):
    df = load_data(BOOKINGS_FILE, ["user", "date", "table", "time"])
    mask = (df["date"] == str(date_str)) & (df["table"] == str(table)) & (df["time"] == str(time_str))
    
    if df[mask].empty:
        # New booking: Always use the logged-in user's name (even if Admin)
        new_row = pd.DataFrame([[user_email, date_str, table, time_str]], columns=df.columns)
        df = pd.concat([df, new_row], ignore_index=True)
    else:
        # Clicked an existing booking
        if role == "admin":
            # Admin can re-assign the name
            st.session_state.rename_target = (date_str, table, time_str)
        else:
            owner = df[mask].iloc[0]["user"]
            if owner == user_email: df = df[~mask]
            
    save_data(df, BOOKINGS_FILE)

# ===============================
# AUTHENTICATION
# ===============================
if "user" not in st.session_state:
    mode = st.radio("M", ["Login", "Register"], horizontal=True, label_visibility="collapsed")
    l_user = st.text_input("User").strip().lower()
    l_pw = st.text_input("Password", type="password").strip()
    
    if st.button("Submit", use_container_width=True):
        u_df = load_data(USERS_FILE, USER_COLS)
        if mode == "Login":
            match = u_df[(u_df["email"].str.lower() == l_user) & (u_df["password"].astype(str) == str(l_pw))]
            if not match.empty and str(match.iloc[0]["approved"]).lower() == "true":
                st.session_state.user = l_user
                st.session_state.role = str(match.iloc[0]["role"]).lower()
                st.session_state.name = l_user.split('@')[0].capitalize()
                st.rerun()
            else: st.error("Access Denied or Not Approved.")
        else:
            new_entry = pd.DataFrame([[l_user, l_pw, "user", "False"]], columns=USER_COLS)
            save_data(pd.concat([u_df, new_entry], ignore_index=True), USERS_FILE)
            st.success("Registered! Ask Admin.")
    st.stop()

# ===============================
# MAIN TABS
# ===============================
tab_booking, tab_admin = st.tabs(["🎱 Bookings", "⚙️ Admin"]) if st.session_state.role == "admin" else [st.tabs(["🎱 Bookings"])[0], None]

with tab_booking:
    # Rename Dialog for Admins
    if "rename_target" in st.session_state:
        d, tb, tm = st.session_state.rename_target
        with st.expander(f"Edit Booking: {tb} at {tm}", expanded=True):
            new_name = st.text_input("Enter New Name/Email")
            c1, c2 = st.columns(2)
            if c1.button("Save Name"):
                df = load_data(BOOKINGS_FILE, ["user", "date", "table", "time"])
                df.loc[(df["date"]==d) & (df["table"]==tb) & (df["time"]==tm), "user"] = new_name
                save_data(df, BOOKINGS_FILE)
                del st.session_state.rename_target
                st.rerun()
            if c2.button("Delete Booking", type="primary"):
                df = load_data(BOOKINGS_FILE, ["user", "date", "table", "time"])
                df = df[~((df["date"]==d) & (df["table"]==tb) & (df["time"]==tm))]
                save_data(df, BOOKINGS_FILE)
                del st.session_state.rename_target
                st.rerun()

    # Date Row
    today = datetime.now().date()
    dates = [today + timedelta(days=i) for i in range(14)]
    if "sel_date" not in st.session_state: st.session_state.sel_date = today
    
    d_cols = st.columns(7)
    for i in range(7):
        d = dates[i]
        with d_cols[i]:
            if st.button(f"{d.strftime('%a')}\n{d.day}", type="primary" if d == st.session_state.sel_date else "secondary", use_container_width=True):
                st.session_state.sel_date = d
                st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)
    
    # Frozen Header Row
    h_cols = st.columns(4)
    for i, title in enumerate(["Time", "T1", "T2", "T3"]):
        h_cols[i].markdown(f"<div class='grid-header'>{title}</div>", unsafe_allow_html=True)

    # Table Grid
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
                r_cols[i+1].button(name, key=btn_key, type="primary", on_click=handle_booking, 
                                  args=(str(st.session_state.sel_date), table, t, st.session_state.user, st.session_state.role), use_container_width=True)
            else:
                r_cols[i+1].button("➕", key=btn_key, type="secondary", on_click=handle_booking, 
                                  args=(str(st.session_state.sel_date), table, t, st.session_state.user, st.session_state.role), use_container_width=True)

if tab_admin:
    u_df = load_data(USERS_FILE, USER_COLS)
    b_df = load_data(BOOKINGS_FILE, ["user", "date", "table", "time"])
    
    # Stats
    c1, c2, c3 = st.columns(3)
    c1.metric("Total Users", len(u_df))
    c2.metric("Total Bookings", len(b_df))
    c3.metric("Pending", len(u_df[u_df["approved"].astype(str).str.lower() == "false"]))

    # Bulk Tools
    with st.expander("🚀 Bulk Actions & CSV Import"):
        up_file = st.file_uploader("Import Users (CSV with email,password,role,approved)")
        if up_file:
            new_users = pd.read_csv(up_file)
            save_data(pd.concat([u_df, new_users]).drop_duplicates(subset=['email']), USERS_FILE)
            st.success("Imported!")
        
        new_pass = st.text_input("Set Universal Password for ALL users")
        if st.button("Update All Passwords"):
            u_df["password"] = new_pass
            save_data(u_df, USERS_FILE)
            st.rerun()

    # Sortable Editor
    u_df["approved"] = u_df["approved"].astype(str).str.lower().isin(["true", "1", "yes"])
    edited = st.data_editor(u_df, use_container_width=True, num_rows="dynamic",
                           column_config={"approved": st.column_config.CheckboxColumn("Approved"),
                                          "role": st.column_config.SelectboxColumn("Role", options=["user", "admin"])})
    if st.button("Save User Table"):
        save_data(edited, USERS_FILE)
        st.rerun()

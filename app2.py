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
# THE REPAIRED CSS (STRICT GRID & WIDTH)
# ===============================
st.markdown("""
<style>
    .block-container { padding: 1rem 5px !important; max-width: 100% !important; }
    
    div[data-testid="stHorizontalBlock"]:has(> div:nth-child(7):last-child) {
        display: flex !important; flex-wrap: nowrap !important;
        overflow-x: auto !important; gap: 6px !important;
    }
    div[data-testid="stHorizontalBlock"]:has(> div:nth-child(7):last-child) > div {
        min-width: 85px !important; flex: 0 0 auto !important;
    }

    /* GRID FIX: Force 4 equal columns */
    div[data-testid="stHorizontalBlock"]:has(> div:nth-child(4):last-child) {
        display: grid !important; 
        grid-template-columns: repeat(4, 1fr) !important;
        gap: 4px !important; 
        margin-bottom: 4px !important;
    }
    div[data-testid="stHorizontalBlock"]:has(> div:nth-child(4):last-child) > div {
        width: 100% !important; 
        min-width: 0 !important;
    }

    /* BUTTON FIX: Force ALL buttons to fill the entire column width */
    .stButton > button {
        height: 44px !important; 
        width: 100% !important; 
        min-width: 100% !important;
        border-radius: 6px !important;
        display: flex !important; 
        justify-content: center !important; 
        align-items: center !important;
        padding: 0 !important;
    }
    
    .stButton > button p {
        font-size: 11px !important; 
        font-weight: bold !important;
        text-align: center !important; 
        margin: 0 !important;
        width: 100% !important;
    }

    /* Colors */
    div[data-testid="stHorizontalBlock"]:has(> div:nth-child(4):last-child) button[kind="secondary"] { 
        background-color: #e8f5e9 !important; color: #2e7d32 !important; border: 1px solid #c8e6c9 !important;
    }
    div[data-testid="stHorizontalBlock"]:has(> div:nth-child(4):last-child) button[kind="primary"] { 
        background-color: #ffebee !important; color: #c62828 !important; border: 1px solid #ffcdd2 !important;
    }

    /* Headers & Labels */
    .grid-header {
        text-align: center; font-size: 11px; font-weight: bold; 
        height: 44px; line-height: 44px; border-radius: 6px; 
        background-color: #6c757d; color: white; width: 100%;
    }
    .time-label {
        text-align: center; font-size: 11px; font-weight: bold; 
        height: 44px; line-height: 44px; border-radius: 6px; color: #333; width: 100%;
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
        return df
    return pd.read_csv(file, dtype=str).fillna("")

def save_data(df, file):
    df.astype(str).to_csv(file, index=False)

def set_date(new_date): st.session_state.sel_date = new_date

def handle_booking(date_str, table, time_str, user_email, role):
    df = load_data(BOOKINGS_FILE, ["user", "date", "table", "time"])
    mask = (df["date"] == str(date_str)) & (df["table"] == str(table)) & (df["time"] == str(time_str))
    if df[mask].empty:
        new_row = pd.DataFrame([[user_email, date_str, table, time_str]], columns=df.columns)
        df = pd.concat([df, new_row], ignore_index=True)
    else:
        owner = df[mask].iloc[0]["user"]
        if owner == user_email or role == "admin": df = df[~mask]
    save_data(df, BOOKINGS_FILE)

# ===============================
# LOGIN & REGISTRATION (LOGIC FIXED)
# ===============================
if "user" not in st.session_state:
    mode = st.radio("M", ["Login", "Register"], horizontal=True, label_visibility="collapsed")
    if mode == "Login":
        st.markdown("<h3 style='text-align:center;'>🎱 Pool Login</h3>", unsafe_allow_html=True)
        l_user = st.text_input("User").strip().lower()
        l_pw = st.text_input("Password", type="password").strip()
        if st.button("Log In", use_container_width=True):
            u_df = load_data(USERS_FILE, USER_COLS)
            match = u_df[(u_df["email"].str.lower() == l_user) & (u_df["password"].astype(str) == str(l_pw))]
            if not match.empty:
                if str(match.iloc[0]["approved"]).lower() in ["true", "1", "yes"]:
                    st.session_state.user = l_user
                    st.session_state.role = str(match.iloc[0]["role"]).lower()
                    st.session_state.name = l_user.split('@')[0].capitalize()
                    st.rerun()
                else: st.warning("Wait for Admin Approval.")
            else: st.error("Invalid credentials.")
    else:
        st.markdown("<h3 style='text-align:center;'>🎱 Register</h3>", unsafe_allow_html=True)
        r_user = st.text_input("New User").strip().lower()
        r_pw = st.text_input("New Password", type="password").strip()
        if st.button("Register", use_container_width=True):
            u_df = load_data(USERS_FILE, USER_COLS)
            if r_user in u_df["email"].values: st.error("Exists.")
            else:
                new_entry = pd.DataFrame([[r_user, r_pw, "user", "False"]], columns=USER_COLS)
                save_data(pd.concat([u_df, new_entry], ignore_index=True), USERS_FILE)
                st.success("Registered! Ask Admin to approve.")
    st.stop()

# ===============================
# MAIN UI
# ===============================
if "sel_date" not in st.session_state: st.session_state.sel_date = datetime.now().date()
st.write(f"**👤 {st.session_state.name}** | {st.session_state.sel_date}")

tab_booking, tab_admin = st.tabs(["🎱 Bookings", "⚙️ Admin"]) if st.session_state.role == "admin" else [st.tabs(["🎱 Bookings"])[0], None]

with tab_booking:
    today = datetime.now().date()
    dates = [today + timedelta(days=i) for i in range(14)]
    for row_start in [0, 7]:
        d_cols = st.columns(7)
        for i in range(7):
            d = dates[row_start + i]
            lbl = f"{'TOD' if d == today else d.strftime('%a').upper()}\n{d.day}"
            with d_cols[i]:
                st.button(lbl, key=f"d_{d}", type="primary" if d == st.session_state.sel_date else "secondary", 
                          on_click=set_date, args=(d,), use_container_width=True)

    st.divider()
    h_cols = st.columns(4)
    for i, title in enumerate(["Time", "T1", "T2", "T3"]):
        h_cols[i].markdown(f"<div class='grid-header'>{title}</div>", unsafe_allow_html=True)

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
            # Logic for Name vs Plus remains the same, but CSS forces identical width
            if not match.empty:
                display_name = match.iloc[0]["user"].split('@')[0].capitalize()[:7]
                r_cols[i+1].button(display_name, key=btn_key, type="primary", on_click=handle_booking, 
                                  args=(str(st.session_state.sel_date), table, t, st.session_state.user, st.session_state.role), use_container_width=True)
            else:
                r_cols[i+1].button("➕", key=btn_key, type="secondary", on_click=handle_booking, 
                                  args=(str(st.session_state.sel_date), table, t, st.session_state.user, st.session_state.role), use_container_width=True)

if tab_admin:
    with tab_admin:
        u_df = load_data(USERS_FILE, USER_COLS)
        u_df["approved"] = u_df["approved"].astype(str).str.lower().isin(["true", "1", "yes"])
        edited = st.data_editor(u_df, num_rows="dynamic", use_container_width=True, key="admin_edit",
                               column_config={"approved": st.column_config.CheckboxColumn("Approved")})
        if st.button("💾 Save User Changes"):
            save_data(edited, USERS_FILE)
            st.rerun()

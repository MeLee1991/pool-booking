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
# THE REPAIRED CSS (STRICT GRID)
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

    div[data-testid="stHorizontalBlock"]:has(> div:nth-child(4):last-child) {
        display: grid !important; grid-template-columns: repeat(4, 1fr) !important;
        gap: 4px !important; margin-bottom: 4px !important;
    }
    div[data-testid="stHorizontalBlock"]:has(> div:nth-child(4):last-child) > div {
        width: 100% !important; min-width: 0 !important;
    }

    .stButton > button {
        height: 44px !important; border-radius: 6px !important;
        display: flex !important; justify-content: center !important; align-items: center !important;
        width: 100% !important;
    }
    .stButton > button p {
        font-size: 11px !important; font-weight: bold !important;
        text-align: center !important; margin: 0 !important;
    }

    div[data-testid="stHorizontalBlock"]:has(> div:nth-child(4):last-child) button[kind="secondary"] { 
        background-color: #e8f5e9 !important; color: #2e7d32 !important; border: 1px solid #c8e6c9 !important;
    }
    div[data-testid="stHorizontalBlock"]:has(> div:nth-child(4):last-child) button[kind="primary"] { 
        background-color: #ffebee !important; color: #c62828 !important; border: 1px solid #ffcdd2 !important;
    }

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
# DATA HELPERS
# ===============================
def load_data(file, cols):
    if not os.path.exists(file):
        df = pd.DataFrame(columns=cols)
        if file == USERS_FILE:
            df = pd.DataFrame([[OWNER_EMAIL, "1234", "admin", True]], columns=cols)
        df.to_csv(file, index=False)
        return df
    df = pd.read_csv(file)
    if list(df.columns) != cols:
        # Migration: If old file doesn't have 'approved', add it
        if "approved" not in df.columns and file == USERS_FILE:
            df["approved"] = True
            df.to_csv(file, index=False)
        else:
            df = pd.DataFrame(columns=cols)
            if file == USERS_FILE:
                df = pd.DataFrame([[OWNER_EMAIL, "1234", "admin", True]], columns=cols)
            df.to_csv(file, index=False)
    return df

def save_data(df, file): df.to_csv(file, index=False)
def set_date(new_date): st.session_state.sel_date = new_date

# ===============================
# AUTH & REGISTRATION
# ===============================
USER_COLS = ["email", "password", "role", "approved"]

if "user" not in st.session_state:
    mode = st.radio("Choose Mode", ["Login", "Register"], horizontal=True, label_visibility="collapsed")
    
    if mode == "Login":
        st.markdown("<h3 style='text-align:center;'>🎱 Pool Login</h3>", unsafe_allow_html=True)
        l_email = st.text_input("Email").lower()
        l_pw = st.text_input("Password", type="password")
        if st.button("Log In", use_container_width=True):
            u_df = load_data(USERS_FILE, USER_COLS)
            match = u_df[(u_df["email"] == l_email) & (u_df["password"].astype(str) == str(l_pw))]
            
            if not match.empty:
                user_data = match.iloc[0]
                if user_data["approved"]:
                    st.session_state.user = l_email
                    st.session_state.role = user_data["role"]
                    st.session_state.name = l_email.split('@')[0].capitalize()
                    st.rerun()
                else:
                    st.warning("Your account is pending admin approval.")
            else: st.error("Invalid credentials.")
            
    else:
        st.markdown("<h3 style='text-align:center;'>🎱 Register</h3>", unsafe_allow_html=True)
        r_email = st.text_input("New Email").lower()
        r_pw = st.text_input("New Password", type="password")
        if st.button("Submit Registration", use_container_width=True):
            u_df = load_data(USERS_FILE, USER_COLS)
            if r_email in u_df["email"].values:
                st.error("Email already exists.")
            elif "@" not in r_email:
                st.error("Please enter a valid email.")
            else:
                new_user = pd.DataFrame([[r_email, r_pw, "user", False]], columns=USER_COLS)
                u_df = pd.concat([u_df, new_user], ignore_index=True)
                save_data(u_df, USERS_FILE)
                st.success("Registration sent! Please wait for admin approval.")
    st.stop()

# ===============================
# MAIN UI
# ===============================
if "sel_date" not in st.session_state: st.session_state.sel_date = datetime.now().date()

# Tab Setup
tabs = ["🎱 Bookings", "👤 Profile"]
if st.session_state.role == "admin": tabs.append("⚙️ Admin Dashboard")
curr_tabs = st.tabs(tabs)

# --- BOOKINGS TAB ---
with curr_tabs[0]:
    st.write(f"**👤 {st.session_state.name}** | {st.session_state.sel_date}")
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
                st.button(lbl, key=f"d_{d}", type="primary" if d == st.session_state.sel_date else "secondary", on_click=set_date, args=(d,))

    st.divider()
    h_cols = st.columns(4)
    for i, title in enumerate(["Time", "T1", "T2", "T3"]):
        with h_cols[i]: st.markdown(f"<div class='grid-header'>{title}</div>", unsafe_allow_html=True)

    times = [f"{h:02d}:{m}" for h in range(6, 24) for m in ("00","30")]
    bookings = load_data(BOOKINGS_FILE, ["user", "date", "table", "time"])
    df_day = bookings[bookings["date"] == str(st.session_state.sel_date)]

    for t in times:
        r_cols = st.columns(4)
        block_idx = (int(t.split(":")[0]) - 6) // 4
        with r_cols[0]: st.markdown(f"<div class='time-label time-block-{block_idx}'>{t}</div>", unsafe_allow_html=True)
        for i, table in enumerate(["T1", "T2", "T3"]):
            with r_cols[i+1]:
                match = df_day[(df_day["table"] == table) & (df_day["time"] == t)]
                btn_key = f"btn_{st.session_state.sel_date}_{table}_{t}"
                if not match.empty:
                    owner_email = match.iloc[0]["user"]
                    display_name = owner_email.split('@')[0].capitalize()[:7]
                    def remove_book(d, tab, tm, u, r):
                        df = load_data(BOOKINGS_FILE, ["user", "date", "table", "time"])
                        mask = (df["date"] == d) & (df["table"] == tab) & (df["time"] == tm)
                        if df[mask].iloc[0]["user"] == u or r == "admin":
                            df = df[~mask]
                            save_data(df, BOOKINGS_FILE)
                    st.button(display_name, key=btn_key, type="primary", on_click=remove_book, args=(str(st.session_state.sel_date), table, t, st.session_state.user, st.session_state.role))
                else:
                    def add_book(d, tab, tm, u):
                        df = load_data(BOOKINGS_FILE, ["user", "date", "table", "time"])
                        new_row = pd.DataFrame([[u, d, tab, tm]], columns=df.columns)
                        df = pd.concat([df, new_row], ignore_index=True)
                        save_data(df, BOOKINGS_FILE)
                    st.button("➕", key=btn_key, type="secondary", on_click=add_book, args=(str(st.session_state.sel_date), table, t, st.session_state.user))

# --- PROFILE TAB ---
with curr_tabs[1]:
    st.subheader("Update Password")
    new_pw = st.text_input("New Password", type="password")
    confirm_pw = st.text_input("Confirm New Password", type="password")
    if st.button("Change Password"):
        if new_pw == confirm_pw and len(new_pw) > 0:
            u_df = load_data(USERS_FILE, USER_COLS)
            u_df.loc[u_df["email"] == st.session_state.user, "password"] = new_pw
            save_data(u_df, USERS_FILE)
            st.success("Password updated!")
        else: st.error("Passwords do not match.")

# --- ADMIN TAB ---
if st.session_state.role == "admin":
    with curr_tabs[2]:
        st.subheader("📊 User Rankings")
        all_b = load_data(BOOKINGS_FILE, ["user", "date", "table", "time"])
        if not all_b.empty:
            stats = all_b.groupby("user").size().reset_index(name="Total").sort_values("Total", ascending=False)
            st.dataframe(stats, hide_index=True, use_container_width=True)

        st.divider()
        st.subheader("👥 Manage & Approve Users")
        u_df = load_data(USERS_FILE, USER_COLS)
        edited = st.data_editor(u_df, num_rows="dynamic", use_container_width=True,
                               column_config={"role": st.column_config.SelectboxColumn("Role", options=["user", "admin"]),
                                              "approved": st.column_config.CheckboxColumn("Approved")})
        if st.button("💾 Save User Changes"):
            save_data(edited, USERS_FILE)
            st.rerun()

        st.divider()
        with open(BOOKINGS_FILE, "rb") as f:
            st.download_button("📥 History CSV", f, "history.csv", "text/csv")

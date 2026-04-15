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
# RESTORED STRICT CSS
# ===============================
st.markdown("""
<style>
    .block-container { padding: 1rem 5px !important; max-width: 100% !important; }
    
    /* DATE SELECTOR - NARROW */
    div[data-testid="stHorizontalBlock"]:has(> div:nth-child(7):last-child) {
        display: flex !important; flex-wrap: nowrap !important;
        overflow-x: auto !important; gap: 4px !important;
    }
    div[data-testid="stHorizontalBlock"]:has(> div:nth-child(7):last-child) button {
        max-width: 65px !important; min-width: 65px !important;
    }

    /* MAIN TABLE - 4 COLUMNS FORCED */
    div[data-testid="stHorizontalBlock"]:has(> div:nth-child(4):last-child) {
        display: grid !important;
        grid-template-columns: repeat(4, 1fr) !important;
        gap: 4px !important; margin-bottom: 4px !important;
    }
    div[data-testid="stHorizontalBlock"]:has(> div:nth-child(4):last-child) > div {
        width: 100% !important; min-width: 0 !important;
    }

    .stButton > button {
        height: 44px !important; border-radius: 6px !important;
        width: 100% !important;
    }
    .stButton > button p { font-size: 11px !important; font-weight: bold !important; margin: 0 !important; }

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
# AUTH & REGISTRATION
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
                    st.session_state.user = l_email
                    st.session_state.role = match.iloc[0]["role"]
                    st.session_state.name = l_email.split('@')[0].capitalize()
                    st.rerun()
                else: st.warning("Pending approval.")
            else: st.error("Incorrect credentials.")
    else:
        st.markdown("<h3 style='text-align:center;'>🎱 Register</h3>", unsafe_allow_html=True)
        r_email = st.text_input("Email").lower()
        r_pw = st.text_input("Password", type="password")
        if st.button("Submit", use_container_width=True):
            u_df = load_data(USERS_FILE, USER_COLS)
            if r_email in u_df["email"].values: st.error("Exists.")
            else:
                new_u = pd.DataFrame([[r_email, r_pw, "user", False]], columns=USER_COLS)
                u_df = pd.concat([u_df, new_u], ignore_index=True)
                save_data(u_df, USERS_FILE)
                st.success("Wait for approval!")
    st.stop()

# ===============================
# MAIN BOOKING UI (NO TABS)
# ===============================
if "sel_date" not in st.session_state: st.session_state.sel_date = datetime.now().date()
st.write(f"**👤 {st.session_state.name}** | {st.session_state.sel_date}")

today, tomorrow = datetime.now().date(), datetime.now().date() + timedelta(days=1)
dates = [today + timedelta(days=i) for i in range(14)]
for rs in [0, 7]:
    d_cols = st.columns(7)
    for i in range(7):
        d = dates[rs + i]
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
                disp = owner.split('@')[0].capitalize()[:7]
                if st.button(disp, key=btn_key, type="primary"):
                    if owner == st.session_state.user or st.session_state.role == "admin":
                        bookings = bookings[~((bookings["date"] == str(st.session_state.sel_date)) & (bookings["table"] == table) & (bookings["time"] == t))]
                        save_data(bookings, BOOKINGS_FILE)
                        st.rerun()
            else:
                if st.button("➕", key=btn_key, type="secondary"):
                    new_b = pd.DataFrame([[st.session_state.user, str(st.session_state.sel_date), table, t]], columns=BOOK_COLS)
                    save_data(pd.concat([bookings, new_b], ignore_index=True), BOOKINGS_FILE)
                    st.rerun()

# ===============================
# HIDDEN ADMIN & PROFILE (AT BOTTOM)
# ===============================
st.divider()
with st.expander("👤 My Profile"):
    p1 = st.text_input("New Password", type="password")
    if st.button("Update Password"):
        u_df = load_data(USERS_FILE, USER_COLS)
        u_df.loc[u_df["email"] == st.session_state.user, "password"] = p1
        save_data(u_df, USERS_FILE)
        st.success("Updated!")

if st.session_state.role == "admin":
    with st.expander("⚙️ Admin Dashboard"):
        st.subheader("📊 Statistics")
        if not bookings.empty:
            stats = bookings.groupby("user").size().reset_index(name="Total").sort_values("Total", ascending=False)
            st.dataframe(stats, hide_index=True, use_container_width=True)
        
        st.subheader("👥 User Management")
        u_df = load_data(USERS_FILE, USER_COLS)
        edited = st.data_editor(u_df, use_container_width=True)
        if st.button("💾 Save Changes"):
            save_data(edited, USERS_FILE)
            st.rerun()

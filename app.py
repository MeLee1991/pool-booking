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
# THE DESIGN (STRICTLY PRESERVED)
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
        width: 100% !important; padding: 0 !important;
    }
    .stButton > button p { font-size: 11px !important; font-weight: bold !important; }
    div[data-testid="stHorizontalBlock"]:has(> div:nth-child(4):last-child) button[kind="secondary"] { 
        background-color: #e8f5e9 !important; color: #2e7d32 !important; border: 1px solid #c8e6c9 !important;
    }
    div[data-testid="stHorizontalBlock"]:has(> div:nth-child(4):last-child) button[kind="primary"] { 
        background-color: #ffebee !important; color: #c62828 !important; border: 1px solid #ffcdd2 !important;
    }
    .grid-header {
        text-align: center; font-size: 11px; font-weight: bold; height: 44px; 
        line-height: 44px; border-radius: 6px; background-color: #212121; color: white;
    }
    .time-label {
        text-align: center; font-size: 11px; font-weight: bold; height: 44px; 
        line-height: 44px; border-radius: 6px; color: #333; background-color: #f5f5f5;
    }
    [data-testid="stHeader"] {display: none;}
</style>
""", unsafe_allow_html=True)

# ===============================
# PERSISTENT LOGIC
# ===============================
USER_COLS = ["email", "password", "role", "approved"]

def load_data(file, cols):
    if not os.path.exists(file):
        df = pd.DataFrame(columns=cols)
        if file == USERS_FILE:
            df = pd.DataFrame([[OWNER_EMAIL, "1234", "admin", True]], columns=cols)
        df.to_csv(file, index=False)
        return df
    df = pd.read_csv(file)
    for col in cols:
        if col not in df.columns:
            df[col] = True if col == "approved" else ("user" if col == "role" else "")
    return df[cols]

def save_data(df, file):
    df.to_csv(file, index=False)

def handle_booking(date_str, table, time_str, user_email, role):
    # Admin can book for the person selected in the Dashboard tab
    target = st.session_state.get("admin_target_user", user_email)
    df = load_data(BOOKINGS_FILE, ["user", "date", "table", "time"])
    mask = (df["date"] == date_str) & (df["table"] == table) & (df["time"] == time_str)
    if df[mask].empty:
        new_row = pd.DataFrame([[target, date_str, table, time_str]], columns=df.columns)
        df = pd.concat([df, new_row], ignore_index=True)
    else:
        # Check if current user owns it or is admin
        owner = str(df[mask].iloc[0]["user"])
        if owner == user_email or role == "admin":
            df = df[~mask]
    save_data(df, BOOKINGS_FILE)

# ===============================
# LOGIN
# ===============================
if "user" not in st.session_state:
    m = st.radio("M", ["Login", "Register"], horizontal=True, label_visibility="collapsed")
    if m == "Login":
        st.markdown("<h3 style='text-align:center;'>🎱 Pool Login</h3>", unsafe_allow_html=True)
        u, p = st.text_input("User").lower(), st.text_input("Password", type="password")
        if st.button("Log In", use_container_width=True):
            if u == OWNER_EMAIL and str(p) == "1234":
                st.session_state.user, st.session_state.role, st.session_state.name = u, "admin", "Admin"
                st.rerun()
            udf = load_data(USERS_FILE, USER_COLS)
            match = udf[(udf["email"] == u) & (udf["password"].astype(str) == str(p))]
            if not match.empty and match.iloc[0]["approved"]:
                st.session_state.user, st.session_state.role = u, match.iloc[0]["role"]
                st.session_state.name = u.split('@')[0].capitalize()
                st.rerun()
            else: st.error("Check credentials or approval.")
    else:
        st.markdown("<h3 style='text-align:center;'>🎱 Register</h3>", unsafe_allow_html=True)
        ru, rp = st.text_input("New User").lower(), st.text_input("New Pass", type="password")
        if st.button("Register"):
            udf = load_data(USERS_FILE, USER_COLS)
            if ru not in udf["email"].values:
                save_data(pd.concat([udf, pd.DataFrame([[ru, rp, "user", False]], columns=USER_COLS)]), USERS_FILE)
                st.success("Wait for Admin.")
    st.stop()

# ===============================
# TABS
# ===============================
if "sel_date" not in st.session_state: st.session_state.sel_date = datetime.now().date()
if st.session_state.role == "admin":
    t_book, t_admin = st.tabs(["🎱 Bookings", "⚙️ Admin Dashboard"])
else:
    t_book, t_admin = st.tabs(["🎱 Bookings"])[0], None

if t_admin:
    with t_admin:
        udf = load_data(USERS_FILE, USER_COLS)
        st.subheader("Users")
        edited = st.data_editor(udf, use_container_width=True, column_config={
            "role": st.column_config.SelectboxColumn("Role", options=["user", "admin"]),
            "approved": st.column_config.CheckboxColumn("Approved")
        })
        if st.button("Save Changes"):
            save_data(edited, USERS_FILE)
            st.success("Saved!")
            st.rerun()
        st.divider()
        ulist = udf["email"].tolist()
        st.session_state.admin_target_user = st.selectbox("Admin: Book for who?", ulist, index=ulist.index(st.session_state.user))

with t_book:
    st.write(f"**👤 {st.session_state.name}** | {st.session_state.sel_date}")
    today = datetime.now().date()
    dates = [today + timedelta(days=i) for i in range(14)]
    for start in [0, 7]:
        cols = st.columns(7)
        for i in range(7):
            d = dates[start+i]
            lbl = f"TOD {d.day}" if d == today else f"{d.strftime('%a').upper()} {d.day}"
            with cols[i]:
                st.button(lbl, key=f"d_{d}", type="primary" if d == st.session_state.sel_date else "secondary", on_click=lambda x=d: setattr(st.session_state, 'sel_date', x))

    st.divider()
    hcols = st.columns(4)
    for i, title in enumerate(["Time", "T1", "T2", "T3"]):
        with hcols[i]: st.markdown(f"<div class='grid-header'>{title}</div>", unsafe_allow_html=True)

    times = [f"{h:02d}:{m}" for h in range(6, 24) for m in ("00","30")]
    bdf = load_data(BOOKINGS_FILE, ["user", "date", "table", "time"])
    day_b = bdf[bdf["date"] == str(st.session_state.sel_date)]

    for t in times:
        rcols = st.columns(4)
        with rcols[0]: st.markdown(f"<div class='time-label'>{t}</div>", unsafe_allow_html=True)
        for i, tab in enumerate(["T1", "T2", "T3"]):
            with rcols[i+1]:
                m = day_b[(day_b["table"] == tab) & (day_b["time"] == t)]
                k = f"{st.session_state.sel_date}_{tab}_{t}"
                if not m.empty:
                    owner = str(m.iloc[0]["user"])
                    # Safety: handle non-email strings in user column
                    disp = owner.split('@')[0].capitalize()[:7] if '@' in owner else owner[:7]
                    st.button(f"X {disp}", key=k, type="primary", on_click=handle_booking, args=(str(st.session_state.sel_date), tab, t, st.session_state.user, st.session_state.role))
                else:
                    st.button("➕", key=k, type="secondary", on_click=handle_booking, args=(str(st.session_state.sel_date), tab, t, st.session_state.user, st.session_state.role))

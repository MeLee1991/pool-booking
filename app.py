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
# ORIGINAL DESIGN CSS (Green/Red)
# ===============================
st.markdown("""
<style>
    .block-container { padding: 1rem 5px !important; max-width: 100% !important; }
    div[data-testid="stHorizontalBlock"]:has(> div:nth-child(4):last-child) {
        display: grid !important; grid-template-columns: repeat(4, 1fr) !important;
        gap: 4px !important; margin-bottom: 4px !important;
    }
    /* Light Green for Free Slots */
    div[data-testid="stHorizontalBlock"]:has(> div:nth-child(4):last-child) button[kind="secondary"] { 
        background-color: #e8f5e9 !important; color: #2e7d32 !important; border: 1px solid #c8e6c9 !important;
    }
    /* Light Red for Booked Slots */
    div[data-testid="stHorizontalBlock"]:has(> div:nth-child(4):last-child) button[kind="primary"] { 
        background-color: #ffebee !important; color: #c62828 !important; border: 1px solid #ffcdd2 !important;
    }
    .stButton > button { height: 44px !important; width: 100% !important; }
    .grid-header { text-align: center; font-size: 11px; font-weight: bold; background-color: #333; color: white; border-radius: 6px; height: 44px; line-height: 44px; }
    .time-label { text-align: center; font-size: 11px; font-weight: bold; background-color: #f0f2f6; border-radius: 6px; height: 44px; line-height: 44px; }
    [data-testid="stHeader"] {display: none;}
</style>
""", unsafe_allow_html=True)

# ===============================
# DATA ENGINES (PROTECTED)
# ===============================
USER_COLS = ["email", "password", "role", "approved", "info"]

def load_data(file, cols):
    if not os.path.exists(file) or os.path.getsize(file) == 0:
        df = pd.DataFrame(columns=cols)
        if file == USERS_FILE:
            df = pd.DataFrame([[OWNER_EMAIL, "1234", "admin", "True", ""]], columns=cols)
        df.to_csv(file, index=False)
        return df
    try:
        df = pd.read_csv(file, dtype=str).fillna("")
        # Ensure 'email' exists for everyone or the app crashes on Admin Tab
        df = df[df['email'] != ""] 
        for c in cols:
            if c not in df.columns: df[c] = ""
        return df[cols]
    except Exception:
        return pd.DataFrame(columns=cols)

def save_data(df, file):
    df.to_csv(file, index=False)

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
# ADMIN TAB (PROTECTED)
# ===============================
if "sel_date" not in st.session_state: st.session_state.sel_date = datetime.now().date()
tabs = st.tabs(["🎱 Bookings", "⚙️ Admin"]) if st.session_state.role == "admin" else [st.tabs(["🎱 Bookings"])[0]]

with tabs[0]:
    st.write(f"**{st.session_state.user} | {st.session_state.sel_date}**")
    # (Booking grid code same as before...)

if st.session_state.role == "admin" and len(tabs) > 1:
    with tabs[1]:
        try:
            u_df = load_data(USERS_FILE, USER_COLS)
            st.subheader("👥 All Users Table")
            
            # Spreadsheet view (The "Better" version)
            u_df["approved"] = u_df["approved"].astype(str).str.lower().isin(["true", "1", "yes"])
            edited_df = st.data_editor(
                u_df, 
                num_rows="dynamic", 
                use_container_width=True, 
                key="admin_table_v2",
                column_config={
                    "approved": st.column_config.CheckboxColumn("Approve"),
                    "info": st.column_config.TextColumn("Info/Photos")
                }
            )
            
            if st.button("💾 Save All Changes", use_container_width=True):
                save_data(edited_df, USERS_FILE)
                st.success("Data Saved!")
                st.rerun()

            st.divider()
            # Safety check: ensure dropdown list isn't empty
            emails = u_df["email"].tolist()
            if emails:
                st.session_state.admin_target_user = st.selectbox("🎯 Book on behalf of:", emails)
        except Exception as e:
            st.error("Data error detected in users.csv. Please delete any empty rows in the table above and Save.")

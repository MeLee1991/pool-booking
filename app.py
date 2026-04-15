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
# DESIGN CSS (RESTORING ORIGINAL)
# ===============================
st.markdown("""
<style>
    .block-container { padding: 1rem 5px !important; max-width: 100% !important; }
    
    /* Grid Layout: 4 Columns */
    div[data-testid="stHorizontalBlock"]:has(> div:nth-child(4):last-child) {
        display: grid !important; grid-template-columns: repeat(4, 1fr) !important;
        gap: 4px !important; margin-bottom: 4px !important;
    }

    /* COLORS: Light Green for Free, Light Red for Booked */
    div[data-testid="stHorizontalBlock"]:has(> div:nth-child(4):last-child) button[kind="secondary"] { 
        background-color: #e8f5e9 !important; color: #2e7d32 !important; border: 1px solid #c8e6c9 !important;
    }
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
# STRENGHTENED DATA ENGINE
# ===============================
USER_COLS = ["email", "password", "role", "approved", "info"]

def load_users():
    if not os.path.exists(USERS_FILE) or os.path.getsize(USERS_FILE) == 0:
        df = pd.DataFrame([[OWNER_EMAIL, "1234", "admin", "True", ""]], columns=USER_COLS)
        df.to_csv(USERS_FILE, index=False)
        return df
    try:
        # Crucial: Force everything to be read as string text to prevent 1234 -> 1234.0
        df = pd.read_csv(USERS_FILE, dtype=str).fillna("")
        for col in USER_COLS:
            if col not in df.columns: df[col] = ""
        # Clean up whitespace
        df['email'] = df['email'].str.strip().str.lower()
        df['password'] = df['password'].str.strip()
        return df[USER_COLS]
    except Exception as e:
        st.error(f"Error loading users: {e}")
        return pd.DataFrame(columns=USER_COLS)

def save_users(df):
    # Ensure no decimals or numeric conversion happens during save
    df = df.astype(str)
    df.to_csv(USERS_FILE, index=False)

# ===============================
# LOGIN SCREEN (FIXED MATCHING)
# ===============================
if "user" not in st.session_state:
    st.markdown("<h3 style='text-align:center;'>🎱 Pool Login</h3>", unsafe_allow_html=True)
    l_user = st.text_input("User").lower().strip()
    l_pw = st.text_input("Password", type="password").strip()
    
    if st.button("Log In", use_container_width=True):
        u_df = load_users()
        # Direct comparison of stripped strings
        match = u_df[(u_df["email"] == l_user) & (u_df["password"] == l_pw)]
        
        if not match.empty:
            is_approved = str(match.iloc[0]["approved"]).lower() in ["true", "1", "yes"]
            if is_approved:
                st.session_state.user = l_user
                st.session_state.role = match.iloc[0]["role"]
                st.session_state.name = l_user.split('@')[0].capitalize()
                st.rerun()
            else:
                st.warning("Wait for Admin Approval.")
        else:
            st.error("Invalid credentials. Please check your username and password.")
    st.stop()

# ===============================
# MAIN UI & ADMIN
# ===============================
# (Previous Booking Grid logic goes here)

tab_booking, tab_admin = st.tabs(["🎱 Bookings", "⚙️ Admin"]) if st.session_state.role == "admin" else (st.tabs(["🎱 Bookings"])[0], None)

if tab_admin:
    with tab_admin:
        u_df = load_users()
        st.subheader("👥 All Users Table")
        
        # Convert approved to boolean for the checkbox in the editor
        u_df["approved"] = u_df["approved"].str.lower().isin(["true", "1", "yes"])
        
        edited_df = st.data_editor(
            u_df, 
            num_rows="dynamic", 
            use_container_width=True, 
            key="admin_editor",
            column_config={
                "password": st.column_config.TextColumn("Password"),
                "approved": st.column_config.CheckboxColumn("Approve")
            }
        )
        
        if st.button("💾 Save All User Data", use_container_width=True):
            # Convert boolean back to string 'True' before saving
            edited_df["approved"] = edited_df["approved"].astype(str)
            save_users(edited_df)
            st.success("User list updated! Logins should now work.")
            st.rerun()

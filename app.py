import os
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

# 1. SETUP
st.set_page_config(page_title="Pool Booking", layout="wide", initial_sidebar_state="collapsed")

# 2. DATA
USERS_FILE = "users.csv"
BOOKINGS_FILE = "bookings.csv"

def load_data(file, columns):
    if os.path.exists(file):
        return pd.read_csv(file, dtype=str)
    return pd.DataFrame(columns=columns)

def save_data(df, file):
    df.to_csv(file, index=False)

users = load_data(USERS_FILE, ["Email", "Name", "Password", "Role"])
bookings = load_data(BOOKINGS_FILE, ["User", "Name", "Date", "Table", "Time"])

# 3. SESSION STATE
if "user" not in st.session_state: st.session_state.user = None
if "role" not in st.session_state: st.session_state.role = None
if "name" not in st.session_state: st.session_state.name = None
if "sel_date" not in st.session_state: st.session_state.sel_date = str(datetime.now().date())
if "confirm_delete" not in st.session_state: st.session_state.confirm_delete = None

# 4. COMPACT CSS
st.markdown("""
<style>
/* FORCE COLUMNS TO TOUCH */
[data-testid="stHorizontalBlock"] {
    display: flex !important;
    flex-direction: row !important;
    flex-wrap: nowrap !important;
    justify-content: center !important; /* Centered table */
    gap: 1px !important; /* Micro gap */
}

[data-testid="column"] {
    flex: 0 0 92px !important; /* Tight fixed width */
    min-width: 92px !important;
    max-width: 92px !important;
    padding: 0px !important;
}

/* BUTTON PADDING FIX (Keeps text inside) */
.stButton > button {
    width: 92px !important;
    height: 75px !important;
    font-size: 11px !important;
    padding: 4px !important; /* Added padding to keep name inside */
    margin-bottom: -14px !important;
    border-radius: 6px !important;
    line-height: 1.2 !important;
}

/* COMPACT HEADERS */
.tbl-header {
    background: #000; color: #fff; text-align: center; 
    font-size: 11px; padding: 6px 0; border-radius: 4px; margin-bottom: 12px;
    width: 92px;
}

/* DATE PICKER GRID (Independent narrow columns) */
.date-grid [data-testid="column"] {
    flex: 0 0 42px !important;
    min-width: 42px !important;
}
.date-grid button {
    height: 45px !important;
    width: 42px !important;
    font-size: 10px !important;
    padding: 0px !important;
}
</style>
""", unsafe_allow_html=True)

# 5. AUTH (Simplified)
if st.session_state.user is None:
    st.title("🎱 RESERVE")
    auth = st.radio("", ["Login", "Register"], horizontal=True)
    e = st.text_input("Email").lower().strip()
    p = st.text_input("Pass", type="password")
    if auth == "Login":
        if st.button("Go"):
            m = users[(users["Email"] == e) & (users["Password"] == p)]
            if not m.empty:
                st.session_state.user, st.session_state.name, st.session_state.role = e, m.iloc[0]["Name"], m.iloc[0]["Role"]
                st.rerun()
    else:
        n = st.text_input("Name")
        if st.button("Register"):
            role = "admin" if users.empty else "user"
            save_data(pd.concat([users, pd.DataFrame([{"Email":e,"Name":n,"Password":p,"Role":role}])]), USERS_FILE)
            st.rerun()
    st.stop()

# 6. ADMIN CONFIRMATION DIALOGUE
if st.session_state.confirm_delete:
    idx, b_name = st.session_state.confirm_delete
    st.warning(f"Are you sure you want to cancel {b_name}'s booking?")
    c1, c2 = st.columns(2)
    if c1.button("YES, Cancel"):
        bookings = bookings.drop(idx)
        save_data(bookings, BOOKINGS_FILE)
        st.session_state.confirm_delete = None
        st.rerun()
    if c2.button("NO, Keep it"):
        st.session_state.confirm_delete = None
        st.rerun()
    st.stop()

# 7. MAIN APP
st.sidebar.button("Logout", on_click=lambda: st.session_state.clear())

# DATE PICKER (7x2 Grid)
st.write("### 📅 Select Date")
today_str = str(datetime.now().date())
for row in range(2):
    d_cols = st.columns(7)
    for i in range(7):
        day_idx = i + (row * 7)
        d = datetime.now().date() + timedelta(days=day_idx)
        d_str = str(d)
        with d_cols[i]:
            label = d.strftime("%a\n%d")
            is_today = d_str == today_str
            btn_label = f"⭐\n{label}" if is_today else label
            if st.button(btn_label, key=f"d_{d_str}", type="primary" if st.session_state.sel_date == d_str else "secondary"):
                st.session_state.sel_date = d_str
                st.rerun()

st.divider()

# TABLE GRID
h_cols = st.columns(3)
tables = ["Table 1", "Table 2", "Table 3"]
for i in range(3):
    h_cols[i].markdown(f"<div class='tbl-header'>{tables[i]}</div>", unsafe_allow_html=True)

HOURS = [f"{h:02d}:{m}" for h in (list(range(8, 24)) + list(range(0, 3))) for m in ["00", "30"]]

for t in HOURS:
    t_cols = st.columns(3)
    for i in range(3):
        t_name = tables[i]
        match = bookings[(bookings["Table"] == t_name) & (bookings["Time"] == t) & (bookings["Date"] == st.session_state.sel_date)]
        key = f"b_{i}_{t}_{st.session_state.sel_date}"
        
        with t_cols[i]:
            if not match.empty:
                b_user, b_name = match.iloc[0]["User"], match.iloc[0]["Name"]
                # Admin or Owner can delete
                if st.session_state.role == "admin" or b_user == st.session_state.user:
                    # Uniform display with ❌
                    if st.button(f"{t}\n❌\n{b_name[:8]}", key=key):
                        if st.session_state.role == "admin":
                            st.session_state.confirm_delete = (match.index, b_name)
                            st.rerun()
                        else:
                            bookings = bookings.drop(match.index)
                            save_data(bookings, BOOKINGS_FILE)
                            st.rerun()
                else:
                    st.button(f"{t}\n🔒\n{b_name[:8]}", key=key, disabled=True)
            else:
                if st.button(f"{t}\n🟢\nFree", key=key):
                    new_b = pd.DataFrame([{"User":st.session_state.user, "Name":st.session_state.name, "Date":st.session_state.sel_date, "Table":t_name, "Time":t}])
                    save_data(pd.concat([bookings, new_b]), BOOKINGS_FILE)
                    st.rerun()

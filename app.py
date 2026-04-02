import os

# ==========================================
# 0. THE "KILL DARK MODE" SCRIPT
# ==========================================
if not os.path.exists('.streamlit'):
    os.makedirs('.streamlit')
with open('.streamlit/config.toml', 'w') as f:
    f.write('''
[theme]
base="light"
primaryColor="#dc3545"
backgroundColor="#ffffff"
secondaryBackgroundColor="#f8f9fa"
textColor="#212529"
font="sans serif"
''')

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

st.set_page_config(page_title="Poolhall Reservations", layout="wide")

# ==========================================
# 1. CSS: 2-ROW DATES + SCROLLABLE GRID
# ==========================================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500;700&display=swap');

    html, body, [class*="css"] { font-family: 'Roboto', sans-serif !important; }

    .block-container {
        max-width: 800px !important; 
        margin: 0 auto !important;
        padding-top: 1rem !important;
    }

    /* ---------------------------------------------------
       2-ROW DATE RIBBON (7 Days per row)
       --------------------------------------------------- */
    section[data-testid="stMain"] [data-testid="stRadio"] > div[role="radiogroup"] {
        display: grid !important;
        grid-template-columns: max-content repeat(7, 1fr) !important;
        grid-template-rows: auto auto !important;
        gap: 8px 4px !important;
        padding: 10px 0 !important;
        border-bottom: 1px solid #dee2e6;
        margin-bottom: 10px !important;
    }
    
    section[data-testid="stMain"] [data-testid="stRadio"] > div[role="radiogroup"]::before {
        content: "Week 1:"; grid-column: 1; grid-row: 1; font-weight: 500; font-size: 12px; align-self: center;
    }
    section[data-testid="stMain"] [data-testid="stRadio"] > div[role="radiogroup"]::after {
        content: "Week 2:"; grid-column: 1; grid-row: 2; font-weight: 500; font-size: 12px; align-self: center;
    }

    /* Hide radio dots */
    [data-testid="stRadio"] label span[data-baseweb="radio"] { display: none !important; }
    
    section[data-testid="stMain"] [data-testid="stRadio"] label {
        background-color: #ffffff !important;
        border: 1px solid #ced4da !important;
        border-radius: 4px !important;
        padding: 4px 2px !important;
        text-align: center;
        cursor: pointer;
    }
    
    section[data-testid="stMain"] [data-testid="stRadio"] label[data-checked="true"] {
        background-color: #007bff !important; border-color: #007bff !important;
    }
    section[data-testid="stMain"] [data-testid="stRadio"] label[data-checked="true"] p { color: #ffffff !important; }

    /* ---------------------------------------------------
       STICKY HEADERS & SCROLLABLE GRID
       --------------------------------------------------- */
    .table-header {
        text-align: center !important;
        font-size: 13px !important;
        font-weight: 700 !important;
        color: #ffffff !important; 
        background-color: #343a40 !important; 
        padding: 8px 0;
        border-radius: 4px 4px 0 0;
        margin-bottom: 0px !important; 
    }

    /* The container that actually scrolls */
    .scroll-view {
        height: 60vh;
        overflow-y: auto;
        overflow-x: hidden;
        border: 1px solid #dee2e6;
        border-top: none;
        background: #ffffff;
    }

    [data-testid="column"] { padding: 0 !important; margin: 0 !important; }
    [data-testid="stHorizontalBlock"] { gap: 0 !important; }

    .stButton > button {
        width: 100% !important;
        border-radius: 0px !important; 
        border: 1px solid #f1f3f5 !important; 
        margin: 0 !important;
        min-height: 40px !important;
        font-size: 12px !important;
    }

    /* Hour stripes */
    [data-testid="column"] > div:nth-child(4n), [data-testid="column"] > div:nth-child(4n+1) {
        background-color: #f8f9fa;
    }

    .stButton > button[kind="primary"] {
        background-color: #ff4b4b !important; color: #ffffff !important; border: none !important;
    }
    .stButton > button[kind="primary"] p { color: #ffffff !important; }

    .admin-panel {
        background: #fff5f5; border: 1px solid #ff4b4b; padding: 10px; border-radius: 5px; margin-bottom: 10px;
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 2. DATA
# ==========================================
USERS_FILE, BOOKINGS_FILE = 'users.csv', 'bookings.csv'
if not os.path.exists(USERS_FILE): pd.DataFrame(columns=['Email', 'Name', 'Password', 'Role']).to_csv(USERS_FILE, index=False)
if not os.path.exists(BOOKINGS_FILE): pd.DataFrame(columns=['User', 'Date', 'Table', 'Time']).to_csv(BOOKINGS_FILE, index=False)

def load_u(): return pd.read_csv(USERS_FILE)
def load_b(): return pd.read_csv(BOOKINGS_FILE)
def save_b(df): df.to_csv(BOOKINGS_FILE, index=False)

# ==========================================
# 3. AUTH
# ==========================================
if 'logged_in_user' not in st.session_state: st.session_state.logged_in_user = None
if 'admin_slot' not in st.session_state: st.session_state.admin_slot = None

st.sidebar.title("Login")
if st.session_state.logged_in_user is None:
    em = st.sidebar.text_input("Email").lower()
    pw = st.sidebar.text_input("Password", type="password")
    if st.sidebar.button("Login"):
        df = load_u()
        m = df[(df['Email']==em) & (df['Password']==pw)]
        if not m.empty:
            st.session_state.logged_in_user, st.session_state.user_role = em, m.iloc[0]['Role']
            st.rerun()
    st.stop()

if st.sidebar.button("Logout"): st.session_state.logged_in_user = None; st.rerun()

# ==========================================
# 4. SCHEDULER
# ==========================================
st.markdown("### RESERVE TABLE")

# Date Grid
today = datetime.now().date()
dates = [today + timedelta(days=i) for i in range(14)]
labels = [d.strftime("%a %d") for d in dates]
sel_date = st.radio("D", labels, horizontal=True, label_visibility="collapsed")
view_date = str(dates[labels.index(sel_date)])

b_df = load_b()
relevant = b_df[b_df['Date'] == view_date]
name_map = dict(zip(load_u()['Email'], load_u()['Name']))

# Admin Panel
if st.session_state.admin_slot:
    s = st.session_state.admin_slot
    st.markdown(f"<div class='admin-panel'><b>Slot:</b> {s['Time']} - {s['Table']}</div>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    if c1.button("🗑️ REMOVE"):
        b_df = b_df[~((b_df['Date']==view_date) & (b_df['Table']==s['Table']) & (b_df['Time']==s['Time']))]
        save_b(b_df); st.session_state.admin_slot = None; st.rerun()
    if c2.button("Close"): st.session_state.admin_slot = None; st.rerun()

# Header
h_cols = st.columns(3)
for i in range(3): h_cols[i].markdown(f"<div class='table-header'>Tbl {i+1}</div>", unsafe_allow_html=True)

# Scrolling Area
HOURS = [f"{h:02d}:{m}" for h in range(8, 24) for m in ("00", "30")] 
st.markdown('<div class="scroll-view">', unsafe_allow_html=True)
grid_cols = st.columns(3)
for i in range(3):
    t_name = f"Table {i+1}"
    with grid_cols[i]:
        for ts in HOURS:
            match = relevant[(relevant['Table']==t_name) & (relevant['Time']==ts)]
            if not match.empty:
                usr = match.iloc[0]['User']
                nm = name_map.get(usr, usr)
                if st.session_state.user_role == 'admin' or usr == st.session_state.logged_in_user:
                    if st.button(f"{ts} {nm}", key=f"{t_name}{ts}", type="primary"):
                        st.session_state.admin_slot = {'Table': t_name, 'Time': ts}
                        st.rerun()
                else:
                    st.button(f"{ts} {nm}", key=f"{t_name}{ts}", disabled=True)
            else:
                if st.button(f"{ts} FREE", key=f"{t_name}{ts}"):
                    new = pd.DataFrame([[st.session_state.logged_in_user, view_date, t_name, ts]], columns=['User','Date','Table','Time'])
                    save_b(pd.concat([b_df, new])); st.rerun()
st.markdown('</div>', unsafe_allow_html=True)

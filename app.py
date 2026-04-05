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
backgroundColor="#f8f9fa"
secondaryBackgroundColor="#e9ecef"
textColor="#212529"
font="sans serif"
''')

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import streamlit.components.v1 as components

st.set_page_config(page_title="Poolhall Reservations", layout="wide")

# ==========================================
# 1. DYNAMIC BACKGROUNDS
# ==========================================
HOURS = [f"{h:02d}:{m}" for h in range(8, 24) for m in ("00", "30")] 

BLOCK_STYLES = [
    {"bg": "#fff9c4", "border": "#fbc02d", "text": "#000000"},
    {"bg": "#e3f2fd", "border": "#42a5f5", "text": "#000000"},
    {"bg": "#e8f5e9", "border": "#66bb6a", "text": "#000000"},
    {"bg": "#ffebee", "border": "#ef5350", "text": "#000000"},
    {"bg": "#f3e5f5", "border": "#ab47bc", "text": "#000000"},
    {"bg": "#ffb74d", "border": "#e65100", "text": "#000000"},
    {"bg": "#80cbc4", "border": "#00695c", "text": "#000000"},
    {"bg": "#d7ccc8", "border": "#8d6e63", "text": "#000000"}
]

dynamic_css = "<style>\n"
mobile_css = "@media (max-width: 900px) {\n" 

for idx, time_str in enumerate(HOURS):
    hour = int(time_str[:2])
    is_prime = 18 <= hour <= 22
    
    style = BLOCK_STYLES[idx // 4]
    child_idx = idx + 3
    
    if is_prime:
        height = "38px"
        font_size = "15px"
        font_weight = "900"
        m_height = "30px"
        m_font_size = "10px"
    else:
        height = "26px"
        font_size = "11px"
        font_weight = "500"
        m_height = "22px"
        m_font_size = "8px"

    dynamic_css += f'[data-testid="stMain"] div[data-testid="column"] > div:nth-child({child_idx}) {{height:{height}!important;min-height:{height}!important;max-height:{height}!important;margin-bottom:4px!important;}}\n'
    
    dynamic_css += f'[data-testid="stMain"] div[data-testid="column"] > div:nth-child({child_idx}) button {{background-color:{style["bg"]}!important;border:2px solid {style["border"]}!important;'
    
    if is_prime:
        dynamic_css += f'box-shadow:0 0 0 2px {style["border"]} inset,0 2px 6px rgba(0,0,0,0.15)!important;'
    
    dynamic_css += '}\n'
    
    dynamic_css += f'[data-testid="stMain"] div[data-testid="column"] > div:nth-child({child_idx}) button p {{font-size:{font_size}!important;font-weight:{font_weight}!important;color:{style["text"]}!important;}}\n'

    mobile_css += f'[data-testid="stMain"] div[data-testid="column"] > div:nth-child({child_idx}) {{height:{m_height}!important;margin-bottom:2px!important;}}\n'
    mobile_css += f'[data-testid="stMain"] div[data-testid="column"] > div:nth-child({child_idx}) button p {{font-size:{m_font_size}!important;}}\n'

mobile_css += "}\n</style>"
dynamic_css += mobile_css
st.markdown(dynamic_css, unsafe_allow_html=True)


# ==========================================
# 1.5 UI POLISH
# ==========================================
st.markdown("""
<style>

/* FONT */
html, body { -webkit-font-smoothing: antialiased; }

/* CONTAINER */
.block-container {
    max-width: 760px !important;
    margin: auto !important;
    padding: 1rem !important;
}

/* HEADER */
.table-header {
    text-align: center;
    font-weight: 700;
    font-size: 13px;
    background: #212529;
    color: white;
    border-radius: 6px;
}

/* BUTTON BASE (PILL STYLE) */
[data-testid="stMain"] button {
    border-radius: 999px !important;
    padding: 0 6px !important;
    box-shadow: 0 1px 2px rgba(0,0,0,0.08);
    transition: all 0.08s ease !important;
}

/* HOVER */
[data-testid="stMain"] button:hover {
    filter: brightness(0.96);
    box-shadow: 0 2px 4px rgba(0,0,0,0.12);
}

/* CLICK */
[data-testid="stMain"] button:active {
    transform: scale(0.93);
    box-shadow: inset 0 1px 3px rgba(0,0,0,0.2);
}

/* FREE */
button[kind="secondary"] {
    background: #f1f3f5 !important;
    border: 1px solid #dee2e6 !important;
}
button[kind="secondary"] p { color: #495057 !important; }

/* YOURS */
button[kind="primary"] {
    background: linear-gradient(180deg,#ff4d4f,#dc3545)!important;
    border:none!important;
}
button[kind="primary"] p { color:white!important; }

/* LOCKED */
button[disabled] {
    background:#f8d7da!important;
    border:1px solid #f1aeb5!important;
}
button[disabled] p { color:#842029!important; }

/* MOBILE */
@media (max-width:900px){
.block-container{padding:4px!important;}

[data-testid="stHorizontalBlock"]{
display:flex!important;
gap:2px!important;
}

[data-testid="column"]{
flex:0 0 32%!important;
width:32%!important;
}

.table-header{font-size:9px!important;}

button p{font-size:7.5px!important;}
}

</style>
""", unsafe_allow_html=True)


# ==========================================
# 2. DATABASE (UNCHANGED)
# ==========================================
USERS_FILE, BOOKINGS_FILE, AUDIT_FILE = 'users.csv', 'bookings.csv', 'audit.csv'
HISTORY_FILE = 'history.csv'
OWNER_EMAIL = "tomazbratina@gmail.com"

if not os.path.exists(USERS_FILE):
    pd.DataFrame(columns=['Email','Name','Password','Role','Max_Hours_Day']).to_csv(USERS_FILE,index=False)
if not os.path.exists(BOOKINGS_FILE):
    pd.DataFrame(columns=['User','Date','Table','Time','Duration']).to_csv(BOOKINGS_FILE,index=False)

def load_users(): return pd.read_csv(USERS_FILE)
def save_users(df): df.to_csv(USERS_FILE,index=False)
def load_bookings(): return pd.read_csv(BOOKINGS_FILE)
def save_bookings(df): df.to_csv(BOOKINGS_FILE,index=False)

# ==========================================
# 3. AUTH (UNCHANGED)
# ==========================================
if 'logged_in_user' not in st.session_state:
    st.session_state.logged_in_user=None

if st.session_state.logged_in_user is None:
    email=st.text_input("Email")
    pw=st.text_input("Password",type="password")
    if st.button("Login"):
        users=load_users()
        u=users[(users.Email==email)&(users.Password==pw)]
        if not u.empty:
            st.session_state.logged_in_user=email
            st.rerun()
    st.stop()

# ==========================================
# 6. GRID UI (UNCHANGED LOGIC)
# ==========================================
st.title("RESERVE TABLE")

today=datetime.now().date()
dates=[today+timedelta(days=i) for i in range(7)]
d=st.selectbox("Date",dates)

df=load_bookings()
cols=st.columns(3)

for i,col in enumerate(cols):
    col.markdown(f"<div class='table-header'>Table {i+1}</div>",unsafe_allow_html=True)

    for t in HOURS:
        booked=df[(df.Table==f"Table {i+1}")&(df.Time==t)&(df.Date==str(d))]
        
        if not booked.empty:
            if col.button(f"{t} ❌",key=f"b{i}{t}",type="primary"):
                df=df[~((df.Table==f"Table {i+1}")&(df.Time==t)&(df.Date==str(d)))]
                save_bookings(df)
                st.rerun()
        else:
            if col.button(f"{t} 🟢",key=f"f{i}{t}"):
                new=pd.DataFrame([[st.session_state.logged_in_user,str(d),f"Table {i+1}",t,0.5]],
                columns=['User','Date','Table','Time','Duration'])
                save_bookings(pd.concat([df,new]))
                st.rerun()

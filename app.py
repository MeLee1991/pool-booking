import os
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

st.set_page_config(page_title="Pool Booking", layout="wide")

# ==========================================
# FILES
# ==========================================
USERS_FILE = "users.csv"
BOOKINGS_FILE = "bookings.csv"

def load_users():
    if os.path.exists(USERS_FILE):
        df = pd.read_csv(USERS_FILE)

        # ensure required columns
        for col in ["Email","Name","Password","Role"]:
            if col not in df.columns:
                df[col] = ""

        # CLEAN DATA (THIS FIXES YOUR ISSUE)
        df["Email"] = df["Email"].astype(str).str.strip().str.lower()
        df["Password"] = df["Password"].astype(str).str.strip()
        df["Name"] = df["Name"].astype(str).str.strip()
        df["Role"] = df["Role"].astype(str).str.strip()

        return df

    return pd.DataFrame(columns=["Email","Name","Password","Role"])
def save_users(df): df.to_csv(USERS_FILE,index=False)

def load_bookings():
    if os.path.exists(BOOKINGS_FILE):
        df = pd.read_csv(BOOKINGS_FILE)
        if "Name" not in df.columns:
            df["Name"] = df["User"].astype(str).str.split("@").str[0]
        return df
    return pd.DataFrame(columns=["User","Name","Date","Table","Time"])

def save_bookings(df): df.to_csv(BOOKINGS_FILE,index=False)

# ==========================================
# SESSION
# ==========================================
if "user" not in st.session_state:
    st.session_state.user=None

# ==========================================
# SIDEBAR
# ==========================================
st.sidebar.title("🔐 Access")

mode = st.sidebar.radio("Mode", ["Login","Register"])

email = st.sidebar.text_input("Email")
password = st.sidebar.text_input("Password", type="password")
name = st.sidebar.text_input("Name") if mode=="Register" else ""

users = load_users()

if st.sidebar.button("Go"):
    email=email.strip().lower()
    password=password.strip()

    if mode=="Register":
        if email in users["Email"].values:
            st.sidebar.error("Exists")
        else:
            role="admin" if users.empty else "pending"
            new=pd.DataFrame([[email,name,password,role]],
                             columns=["Email","Name","Password","Role"])
            save_users(pd.concat([users,new],ignore_index=True))
            st.sidebar.success("Registered")
    else:
        u=users[(users.Email==email)&(users.Password==password)]
        if not u.empty:
            st.session_state.user=email
            st.session_state.name=u.iloc[0]["Name"]
            st.session_state.role=u.iloc[0]["Role"]
            st.rerun()
        else:
            st.sidebar.error("Invalid")

if st.session_state.user is None:
    st.title("POOL BOOKING")
    st.stop()

# ==========================================
# ADMIN PANEL
# ==========================================
if st.session_state.role=="admin":
    st.sidebar.markdown("---")
    admin = st.sidebar.radio("Admin",["Booking","Users","Stats"])

    if admin=="Users":
        st.title("Users")
        users = load_users()
        edited = st.data_editor(users, num_rows="dynamic", use_container_width=True)

        if st.button("💾 Save"):
            save_users(edited)
            st.success("Saved")

        st.download_button("⬇ Export CSV", users.to_csv(index=False), "users.csv")

        uploaded = st.file_uploader("Upload CSV")
        if uploaded:
            df = pd.read_csv(uploaded)
            save_users(df)
            st.success("Imported")

        st.stop()

    if admin=="Stats":
        st.title("Stats")

        if st.button("Load"):
            df = load_bookings()
            st.bar_chart(df["Name"].value_counts())
            st.bar_chart(df["Table"].value_counts())

        st.stop()

# ==========================================
# CSS (COMPACT + CLEAN)
# ==========================================
st.markdown("""
<style>

/* GLOBAL */
.block-container{padding-top:0.5rem;max-width:900px}

/* DATE */
[data-testid="stRadio"]{
position:sticky;top:0;background:#fff;z-index:100;padding:4px;
}

/* 2 rows */
[data-testid="stRadio"] > div{
display:grid!important;
grid-template-columns:repeat(7,1fr)!important;
grid-template-rows:auto auto!important;
gap:4px;
}

/* HEADER */
.table-header{
position:sticky;top:55px;
background:#111;color:#fff;
text-align:center;font-size:12px;
padding:4px;border-radius:6px;margin-bottom:4px;
}

/* BUTTON */
button{
border-radius:999px!important;
height:22px!important;
font-size:10px!important;
padding:0!important;
white-space:nowrap!important;
overflow:hidden!important;
text-overflow:ellipsis!important;
}

/* MOBILE */
@media (max-width:900px){
[data-testid="stHorizontalBlock"]{
display:flex!important;flex-wrap:nowrap!important;gap:2px!important;
}
[data-testid="column"]{
width:33%!important;flex:1 1 33%!important;
}
button{font-size:8px!important;height:20px!important;}
}

</style>
""", unsafe_allow_html=True)

# ==========================================
# DATE NAVIGATION
# ==========================================
today=datetime.now().date()

if "date_idx" not in st.session_state:
    st.session_state.date_idx=0

c1,c2,c3=st.columns([1,4,1])

if c1.button("◀"):
    st.session_state.date_idx=max(0,st.session_state.date_idx-1)

if c3.button("▶"):
    st.session_state.date_idx=min(13,st.session_state.date_idx+1)

dates=[today+timedelta(days=i) for i in range(14)]
selected_date=dates[st.session_state.date_idx]

c2.markdown(f"### {selected_date.strftime('%A %d %b')}")

# ==========================================
# TIME RANGE
# ==========================================
HOURS=[]
for h in list(range(8,24))+list(range(0,3)):
    for m in ["00","30"]:
        HOURS.append(f"{h:02d}:{m}")

# ==========================================
# GRID
# ==========================================
st.title("RESERVE TABLE")

df=load_bookings()

COLORS=["#f8f9fa","#eef7ff","#eefaf0","#fff5f5"]

cols=st.columns(3)

for i,col in enumerate(cols):
    col.markdown(f"<div class='table-header'>Table {i+1}</div>",unsafe_allow_html=True)

    for t in HOURS:
        idx=HOURS.index(t)
        bg=COLORS[(idx//4)%4]

        booked=df[
            (df.Table==f"Table {i+1}")&
            (df.Time==t)&
            (df.Date==str(selected_date))
        ]

        key=f"{i}_{t}"

        col.markdown(f"<div style='background:{bg};padding:1px;border-radius:6px;'>",unsafe_allow_html=True)

        if not booked.empty:
            name=booked.iloc[0]["Name"]

            if booked.iloc[0]["User"]==st.session_state.user:
                if col.button(f"{t} ❌ {name}",key=key):
                    df=df.drop(booked.index)
                    save_bookings(df)
                    st.rerun()
            else:
                col.button(f"{t} 🔒 {name}",disabled=True,key=key)
        else:
            if col.button(f"{t} 🟢",key=key):
                new=pd.DataFrame([[st.session_state.user,st.session_state.name,str(selected_date),f"Table {i+1}",t]],
                                 columns=["User","Name","Date","Table","Time"])
                save_bookings(pd.concat([df,new],ignore_index=True))
                st.rerun()

        col.markdown("</div>",unsafe_allow_html=True)

import os
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

# 1. NASTAVITEV STRANI
st.set_page_config(page_title="Pool Booking", layout="wide", initial_sidebar_state="collapsed")

# 2. PODATKI
USERS_FILE = "users.csv"
BOOKINGS_FILE = "bookings.csv"

def load_data(file, columns):
    if os.path.exists(file): return pd.read_csv(file, dtype=str)
    return pd.DataFrame(columns=columns)

def save_data(df, file): df.to_csv(file, index=False)

users = load_data(USERS_FILE, ["Email", "Name", "Password", "Role"])
bookings = load_data(BOOKINGS_FILE, ["User", "Name", "Date", "Table", "Time"])

# 3. STANJE SEJE
if "user" not in st.session_state: st.session_state.user = None
if "name" not in st.session_state: st.session_state.name = None
if "role" not in st.session_state: st.session_state.role = None
if "sel_date" not in st.session_state: st.session_state.sel_date = str(datetime.now().date())
if "pending_cancel" not in st.session_state: st.session_state.pending_cancel = None

# 4. FIKSNI CSS (PREPREČI ZLAGANJE V EN STOLPEC)
st.markdown("""
<style>
/* DATUMI: Prisili 7 stolpcev v vrsti */
.date-grid [data-testid="stHorizontalBlock"] {
    display: grid !important;
    grid-template-columns: repeat(7, 1fr) !important;
    gap: 2px !important;
    width: 100% !important;
}

/* TABELA: Prisili 4 stolpce (Ura + 3 Mize) */
.data-grid [data-testid="stHorizontalBlock"] {
    display: grid !important;
    grid-template-columns: 50px 1fr 1fr 1fr !important;
    gap: 1px !important;
    width: 100% !important;
    align-items: center;
}

/* GUMBI IN NAPISI */
.stButton > button {
    width: 100% !important;
    height: 45px !important;
    padding: 0px !important;
    margin-bottom: -15px !important;
    border-radius: 4px !important;
    font-size: 10px !important;
}

.time-label { font-size: 12px; font-weight: bold; text-align: center; }
.header-box { background: #000; color: #fff; text-align: center; font-size: 9px; padding: 4px 0; border-radius: 4px; }

/* BARVE */
div.stButton > button:not(:disabled) { background-color: #f6ffed !important; color: #389e0d !important; border: 1px solid #b7eb8f !important; }
div.stButton > button:disabled { background-color: #fff1f0 !important; color: #cf1322 !important; border: 1px solid #ffa39e !important; opacity: 1 !important; }

/* ODSTRANI ODVEČEN PROSTOR */
[data-testid="stAppViewBlockContainer"] { padding: 1rem 0.2rem !important; }
</style>
""", unsafe_allow_html=True)

# 5. PRIJAVA (Login)
if st.session_state.user is None:
    st.title("🎱 REZERVACIJA")
    e = st.text_input("Email").lower().strip()
    p = st.text_input("Geslo", type="password")
    if st.button("Prijava"):
        m = users[(users["Email"] == e) & (users["Password"] == p)]
        if not m.empty:
            st.session_state.user, st.session_state.name, st.session_state.role = e, m.iloc[0]["Name"], m.iloc[0]["Role"]
            st.rerun()
    st.stop()

# 6. POTRDITEV PREKLICA (Admin/User)
if st.session_state.pending_cancel:
    idx, b_name = st.session_state.pending_cancel
    st.warning(f"Prekliči rezervacijo: {b_name}?")
    if st.button("DA, PREKLIČI"):
        bookings = bookings.drop(idx)
        save_data(bookings, BOOKINGS_FILE)
        st.session_state.pending_cancel = None
        st.rerun()
    if st.button("Nazaj"):
        st.session_state.pending_cancel = None
        st.rerun()
    st.stop()

# 7. DATUMSKI IZBIRNIK (2 vrstici po 7 dni)
st.write("### 📅 Izberi datum")
today = datetime.now().date()
for row_idx in range(2):
    st.markdown('<div class="date-grid">', unsafe_allow_html=True)
    cols = st.columns(7)
    for i in range(7):
        d = today + timedelta(days=i + (row_idx * 7))
        d_str = str(d)
        with cols[i]:
            lbl = d.strftime("%a\n%d")
            if d_str == str(today): lbl = f"Danes\n{d.day}"
            is_sel = (st.session_state.sel_date == d_str)
            if st.button(lbl, key=f"d_{d_str}", type="primary" if is_sel else "secondary"):
                st.session_state.sel_date = d_str
                st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

st.divider()

# 8. TABELA REZERVACIJ (Ura | Miza 1 | Miza 2 | Miza 3)
st.markdown('<div class="data-grid">', unsafe_allow_html=True)
h_cols = st.columns(4)
t_names = ["Miza 1", "Miza 2", "Miza 3"]
for i in range(3):
    h_cols[i+1].markdown(f'<div class="header-box">{t_names[i]}</div>', unsafe_allow_html=True)

# Urnik od 08:00 naprej
HOURS = [f"{h:02d}:{m}" for h in (list(range(8, 24)) + list(range(0, 3))) for m in ["00", "30"]]

for t in HOURS:
    r_cols = st.columns(4)
    r_cols[0].markdown(f'<div class="time-label">{t}</div>', unsafe_allow_html=True)
    for i in range(3):
        t_n = f"Table {i+1}"
        match = bookings[(bookings["Table"] == t_n) & (bookings["Time"] == t) & (bookings["Date"] == st.session_state.sel_date)]
        with r_cols[i+1]:
            if not match.empty:
                b_user, b_name = match.iloc[0]["User"], match.iloc[0]["Name"]
                # Če je admin ali lastnik, lahko kliče
                if st.session_state.role == "admin" or b_user == st.session_state.user:
                    if st.button(f"❌ {b_name[:5]}", key=f"b_{t}_{i}"):
                        st.session_state.pending_cancel = (match.index, b_name)
                        st.rerun()
                else:
                    st.button(f"🔒 {b_name[:5]}", key=f"b_{t}_{i}", disabled=True)
            else:
                if st.button("🟢 Prosto", key=f"b_{t}_{i}"):
                    new_b = pd.DataFrame([{"User":st.session_state.user, "Name":st.session_state.name, "Date":st.session_state.sel_date, "Table":t_n, "Time":t}])
                    save_data(pd.concat([bookings, new_b]), BOOKINGS_FILE)
                    st.rerun()
st.markdown('</div>', unsafe_allow_html=True)

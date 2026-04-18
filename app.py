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
BACKUP_DIR = "backups"

# ===============================
# THE PROTECTED DESIGN (CSS)
# ===============================
st.markdown("""
<style>
    .block-container { padding: 1rem 5px !important; max-width: 100% !important; }
    
    /* Narrow Date Row with Scroll */
    div[data-testid="stHorizontalBlock"]:has(> div:nth-child(7):last-child) {
        display: flex !important; flex-wrap: nowrap !important;
        overflow-x: auto !important; gap: 4px !important;
        padding-bottom: 8px !important;
    }
    div[data-testid="stHorizontalBlock"]:has(> div:nth-child(7):last-child) > div {
        min-width: 60px !important; flex: 0 0 60px !important;
    }

    /* Frozen Header with Spacing */
    div[data-testid="stHorizontalBlock"]:has(.grid-header) {
        position: sticky !important; top: 0; z-index: 1000;
        background-color: var(--background-color) !important; 
        padding-bottom: 25px !important;
        margin-bottom: 5px !important;
    }

    /* 4-Column Grid */
    div[data-testid="stHorizontalBlock"]:has(> div:nth-child(4):last-child) {
        display: grid !important; grid-template-columns: repeat(4, 1fr) !important;
        gap: 4px !important; margin-bottom: 4px !important;
    }
    
    .stButton > button {
        height: 44px !important; border-radius: 6px !important;
        display: flex !important; justify-content: center !important; align-items: center !important;
        width: 100% !important;
    }
    .stButton > button p {
        font-size: 10px !important; font-weight: bold !important;
        text-align: center !important; margin: 0 !important; white-space: pre-line !important;
    }

    /* Colors */
    button[kind="secondary"] { background-color: #e8f5e9 !important; color: #2e7d32 !important; border: 1px solid #c8e6c9 !important; }
    button[kind="primary"] { background-color: #ffebee !important; color: #c62828 !important; border: 1px solid #ffcdd2 !important; }

    /* Grid Headers */
    .grid-header {
        text-align: center; font-size: 11px; font-weight: bold; 
        height: 44px; line-height: 44px; border-radius: 6px; 
        background-color: var(--secondary-background-color); 
        color: var(--text-color);
    }
    .time-label {
        text-align: center; font-size: 11px; font-weight: bold; 
        height: 44px; line-height: 44px; border-radius: 6px; 
        color: #222 !important; 
    }

    .time-block-0 { background-color: #fff9c4 !important; } 
    .time-block-1 { background-color: #ffe0b2 !important; } 
    .time-block-2 { background-color: #e3f2fd !important; } 
    .time-block-3 { background-color: #f1f8e9 !important; } 
    .time-block-4 { background-color: #efebe9 !important; } 
</style>
""", unsafe_allow_html=True)

# ===============================
# DATA HELPERS
# ===============================
USER_COLS = ["email", "password", "role", "approved", "Notes"]

def load_data(file, cols):
    if not os.path.exists(file):
        df = pd.DataFrame(columns=cols)
        if file == USERS_FILE:
            df = pd.DataFrame([[OWNER_EMAIL, "1234", "admin", "True", ""]], columns=cols)
        df.to_csv(file, index=False)
        return df
    
    try:
        df = pd.read_csv(file, dtype=str)
        if df.empty:
            return pd.DataFrame(columns=cols)
            
        for col in cols:
            if col not in df.columns:
                df[col] = ""
                
        return df.fillna("")[cols]
    except Exception:
        return pd.DataFrame(columns=cols)

def save_data(df, file):
    df.astype(str).to_csv(file, index=False)
    try:
        os.makedirs(BACKUP_DIR, exist_ok=True)
        today_str = datetime.now().strftime('%Y-%m-%d')
        base_name = os.path.basename(file)
        backup_filename = os.path.join(BACKUP_DIR, f"{today_str}_{base_name}")
        df.astype(str).to_csv(backup_filename, index=False)
    except Exception:
        pass 

def handle_booking(date_str, table, time_str):
    df = load_data(BOOKINGS_FILE, ["user", "date", "table", "time"])
    mask = (df["date"] == str(date_str)) & (df["table"] == str(table)) & (df["time"] == str(time_str))
    
    if df[mask].empty:
        new_row = pd.DataFrame([[st.session_state.user, date_str, table, time_str]], columns=df.columns)
        df = pd.concat([df, new_row], ignore_index=True)
    else:
        owner = df[mask].iloc[0]["user"]
        if st.session_state.role == "admin":
            st.session_state.rename_mode = (date_str, table, time_str, owner)
        elif owner == st.session_state.user:
            df = df[~mask]
    save_data(df, BOOKINGS_FILE)

# ===============================
# AUTH
# ===============================
if "user" not in st.session_state:
    st.markdown("<h2 style='text-align:center;'>🎱 Poolhall</h2>", unsafe_allow_html=True)
    l_user = st.text_input("User").strip().lower()
    l_pw = st.text_input("Pass", type="password").strip()
    c1, c2 = st.columns(2)
    u_df = load_data(USERS_FILE, USER_COLS)
    
    if c1.button("Login", use_container_width=True):
        match = u_df[(u_df["email"].str.lower() == l_user) & (u_df["password"].astype(str) == str(l_pw))]
        if not match.empty:
            approved_status = str(match.iloc[0]["approved"]).strip().lower()
            if approved_status in ["true", "1", "yes"]:
                st.session_state.user = l_user
                st.session_state.role = str(match.iloc[0]["role"]).strip().lower()
                st.session_state.name = l_user.split('@')[0].capitalize()
                st.rerun()
            else: 
                st.error("Access Denied. Check credentials or wait for approval.")
        else:
            st.error("Invalid user or password.")
            
    if c2.button("Register", use_container_width=True):
        if l_user and l_pw:
            if not u_df[u_df["email"].str.lower() == l_user].empty:
                st.warning("User already exists.")
            else:
                save_data(pd.concat([u_df, pd.DataFrame([[l_user, l_pw, "user", "False", ""]], columns=USER_COLS)]), USERS_FILE)
                st.success("Awaiting Admin Approval.")
    st.stop()

# ===============================
# SIDEBAR (SETTINGS & THEME)
# ===============================
with st.sidebar:
    st.markdown(f"👤 **Logged in as:** {st.session_state.name}")
    if st.button("🚪 Logout", use_container_width=True):
        st.session_state.clear()
        st.rerun()
    
    st.divider()
    st.markdown("### 🎨 Appearance")
    st.info("To switch between Dark/Light Mode, click the ⋮ menu in the top right, select Settings, and change your Theme.")

# ===============================
# MAIN TABS & ROUTING (FIXED AND BULLETPROOF)
# ===============================
if "sel_date" not in st.session_state: 
    st.session_state.sel_date = datetime.now().date()

# Setup Layout Tabs Based on Role strictly
if st.session_state.role == "admin":
    tab_booking, tab_admin = st.tabs(["🎱 Bookings", "⚙️ Admin"])
else:
    tab_booking = st.tabs(["🎱 Bookings"])[0]
    tab_admin = None

# ===============================
# TAB 1: BOOKINGS
# ===============================
with tab_booking:
    try:
        if st.session_state.get("rename_mode"):
            d, tb, tm, current = st.session_state.rename_mode
            with st.expander(f"Edit Booking: {tm} {tb}", expanded=True):
                new_name = st.text_input("Change name to:", value=current)
                col_a, col_b = st.columns(2)
                if col_a.button("Save Name"):
                    df = load_data(BOOKINGS_FILE, ["user", "date", "table", "time"])
                    df.loc[(df["date"]==d) & (df["table"]==tb) & (df["time"]==tm), "user"] = new_name
                    save_data(df, BOOKINGS_FILE)
                    del st.session_state.rename_mode
                    st.rerun()
                if col_b.button("Delete Booking", type="primary"):
                    df = load_data(BOOKINGS_FILE, ["user", "date", "table", "time"])
                    df = df[~((df["date"]==d) & (df["table"]==tb) & (df["time"]==tm))]
                    save_data(df, BOOKINGS_FILE)
                    del st.session_state.rename_mode
                    st.rerun()

        today = datetime.now().date()
        dates = [today + timedelta(days=i) for i in range(14)]
        for row in range(2):
            d_cols = st.columns(7)
            for i in range(7):
                d = dates[row * 7 + i]
                if d == today: lbl = f"TOD\n{d.day}"
                elif d == today + timedelta(days=1): lbl = f"TOM\n{d.day}"
                else: lbl = f"{d.strftime('%a').upper()}\n{d.day}"
                with d_cols[i]:
                    if st.button(lbl, key=f"d_{d}", type="primary" if d == st.session_state.sel_date else "secondary", use_container_width=True):
                        st.session_state.sel_date = d
                        st.rerun()

        st.markdown("<div style='height:15px'></div>", unsafe_allow_html=True)

        h_cols = st.columns(4)
        for i, title in enumerate(["Time", "T1", "T2", "T3"]):
            h_cols[i].markdown(f"<div class='grid-header'>{title}</div>", unsafe_allow_html=True)

        times = [f"{h:02d}:{m}" for h in range(6, 24) for m in ("00","30")]
        bookings = load_data(BOOKINGS_FILE, ["user", "date", "table", "time"])
        df_day = bookings[bookings["date"] == str(st.session_state.sel_date)]

        for t in times:
            r_cols = st.columns(4)
            block_idx = (int(t.split(":")[0]) - 6) // 4
            r_cols[0].markdown(f"<div class='time-label time-block-{block_idx}'>{t}</div>", unsafe_allow_html=True)
            for i, table in enumerate(["T1", "T2", "T3"]):
                match = df_day[(df_day["table"] == table) & (df_day["time"] == t)]
                btn_key = f"btn_{st.session_state.sel_date}_{table}_{t}"
                if not match.empty:
                    name = match.iloc[0]["user"].split('@')[0].capitalize()[:7]
                    r_cols[i+1].button(name, key=btn_key, type="primary", on_click=handle_booking, args=(str(st.session_state.sel_date), table, t), use_container_width=True)
                else:
                    r_cols[i+1].button("➕", key=btn_key, type="secondary", on_click=handle_booking, args=(str(st.session_state.sel_date), table, t), use_container_width=True)
    except Exception as e:
        st.error(f"Error loading Booking panel: {e}")

# ===============================
# TAB 2: ADMIN PANEL
# ===============================
if st.session_state.role == "admin" and tab_admin is not None:
    with tab_admin:
        try:
            u_df = load_data(USERS_FILE, USER_COLS)
            b_df = load_data(BOOKINGS_FILE, ["user", "date", "table", "time"])
            
            st.subheader("📊 Global Analytics")
            today_for_stats = datetime.now().date()
            dr = st.date_input("Select Period", [today_for_stats - timedelta(days=30), today_for_stats])
            
            if len(dr) == 2:
                s_df = b_df[(b_df["date"] >= str(dr[0])) & (b_df["date"] <= str(dr[1]))].copy()
                if not s_df.empty:
                    s_df['day'] = pd.to_datetime(s_df['date']).dt.day_name()
                    s_df['clean_user'] = s_df['user'].apply(lambda x: x.split('@')[0].capitalize())
                    
                    c1, c2, c3, c4, c5 = st.columns(5)
                    c1.metric("Total Bookings", len(s_df))
                    c2.metric("Unique Players", s_df['user'].nunique())
                    c3.metric("Top Table", s_df['table'].value_counts().idxmax())
                    c4.metric("Peak Hour", s_df['time'].value_counts().idxmax())
                    c5.metric("Busiest Day", s_df['day'].value_counts().idxmax())
                    
                    st.markdown("<br>", unsafe_allow_html=True)
                    
                    colA, colB = st.columns([2, 1])
                    with colA:
                        st.write("**📈 Bookings Timeline**")
                        timeline = s_df.groupby('date').size().reset_index(name='Count').set_index('date')
                        st.area_chart(timeline)
                    with colB:
                        st.write("**🎱 Table Utilization**")
                        table_dist = s_df['table'].value_counts()
                        st.bar_chart(table_dist)
                    
                    st.markdown("<br>", unsafe_allow_html=True)
                    
                    colC, colD = st.columns(2)
                    with colC:
                        st.write("**🏆 Player Leaderboard**")
                        leaderboard = s_df['clean_user'].value_counts().reset_index()
                        leaderboard.columns = ['Player Name', 'Total Sessions']
                        st.dataframe(leaderboard, use_container_width=True, hide_index=True)
                    with colD:
                        st.write("**🕒 Activity by Hour**")
                        time_dist = s_df['time'].value_counts().sort_index()
                        st.bar_chart(time_dist)
                        
                else: 
                    st.info("No data available for this time period.")

            st.divider()
            st.subheader("👥 User Management Table")
            u_df["approved"] = u_df["approved"].astype(str).str.lower().isin(["true", "1", "yes"])
            edited = st.data_editor(u_df, use_container_width=True, num_rows="dynamic",
                                   column_config={"approved": st.column_config.CheckboxColumn("Approve"),
                                                  "role": st.column_config.SelectboxColumn("Role", options=["user", "admin"])})
            if st.button("💾 Save All Changes"):
                save_data(edited, USERS_FILE)
                st.rerun()

            with st.expander("🛠️ Admin Tools & Manual Backups"):
                st.write("Automatic backups are saved daily to the `backups/` folder on the server. You can also download manual copies here:")
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.download_button("💾 Download Users", u_df.to_csv(index=False), "users_backup.csv", "text/csv", use_container_width=True)
                with col2:
                    st.download_button("💾 Download Bookings", b_df.to_csv(index=False), "bookings_backup.csv", "text/csv", use_container_width=True)
                with col3:
                    if st.button("🔑 Reset Passwords to '1234'", use_container_width=True):
                        u_df["password"] = "1234"
                        save_data(u_df, USERS_FILE)
                        st.success("Passwords reset!")
                        st.rerun()
                    
                st.divider()
                
                with st.form("import_users_form", clear_on_submit=True):
                    up = st.file_uploader("📥 Import Users CSV (Merges with existing)", type=["csv"])
                    submitted = st.form_submit_button("Upload and Import")
                    
                    if submitted and up is not None:
                        new_users = pd.read_csv(up, dtype=str)
                        
                        for col in USER_COLS:
                            if col not in new_users.columns:
                                new_users[col] = ""
                        
                        merged = pd.concat([u_df, new_users[USER_COLS]]).drop_duplicates(subset=['email'], keep='last')
                        save_data(merged, USERS_FILE)
                        
                        st.success("Imported successfully! Your data is saved.")
                        st.rerun()
        except Exception as e:
            st.error(f"Error loading Admin Panel: {e}")

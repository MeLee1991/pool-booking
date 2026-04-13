import streamlit as st
import pandas as pd
import os
from datetime import datetime, timedelta

st.set_page_config(layout="centered")

# ================= FILES =================
USERS_FILE = "users.csv"
BOOKINGS_FILE = "bookings.csv"

def load(file, cols):
    if os.path.exists(file):
        return pd.read_csv(file, dtype=str)
    return pd.DataFrame(columns=cols)

def save(df, file):
    df.to_csv(file, index=False)

users = load(USERS_FILE, ["Email","Name","Password","Role"])
bookings = load(BOOKINGS_FILE, ["User","Name","Date","Table","Time"])

# test user
if "tom3@gmail.com" not in users["Email"].values:
    users = pd.concat([users, pd.DataFrame([{
        "Email":"tom3@gmail.com",
        "Name":"Tom",
        "Password":"1234",
        "Role":"admin"
    }])])
    save(users, USERS_FILE)

# ================= SESSION =================
for k in ["user","name","role","date","page"]:
    if k not in st.session_state:
        st.session_state[k] = None

if not st.session_state.date:
    st.session_state.date = str(datetime.now().date())

if not st.session_state.page:
    st.session_state.page = "grid"

# ================= LOGIN =================
if st.session_state.user is None:
    e = st.text_input("Email", value="tom3@gmail.com")
    p = st.text_input("Password", type="password", value="1234")

    if st.button("Login"):
        m = users[(users["Email"]==e)&(users["Password"]==p)]
        if not m.empty:
            st.session_state.user = e
            st.session_state.name = m.iloc[0]["Name"]
            st.session_state.role = m.iloc[0]["Role"]
            st.rerun()
    st.stop()

# ================= ADMIN =================
if st.session_state.page == "admin":
    st.title("Admin panel")

    if st.button("← Back"):
        st.session_state.page = "grid"
        st.rerun()

    st.subheader("Users (editable table)")

    edited = st.data_editor(users, num_rows="dynamic", use_container_width=True)

    if st.button("💾 Save changes"):
        save(edited, USERS_FILE)
        st.success("Saved!")

    st.stop()

# ================= HEADER =================
st.markdown(f"👤 **{st.session_state.name} | {st.session_state.date}**")

if st.session_state.role == "admin":
    if st.button("⚙️ Admin Control", use_container_width=True):
        st.session_state.page = "admin"
        st.rerun()

# ================= DATE PICKER =================
today = datetime.now().date()

cols = st.columns(7)
for i in range(14):
    d = today + timedelta(days=i)
    ds = str(d)

    label = "TOD" if i==0 else ("TOM" if i==1 else d.strftime("%a").upper())

    with cols[i % 7]:
        if st.button(f"{label}\n{d.day}", key=f"d_{ds}"):
            st.session_state.date = ds
            st.rerun()

# ================= TABLE =================
HOURS = [f"{h:02d}:{m}" for h in range(6,24) for m in ["00","30"]]

# header
h = st.columns(4)
h[0].write("Time")
h[1].write("T1")
h[2].write("T2")
h[3].write("T3")

for idx, t in enumerate(HOURS):
    cols = st.columns(4)

    # time color bands
    band = ["#f3f4f6","#e0f2fe","#fef3c7","#ede9fe"][(idx//8)%4]

    with cols[0]:
        st.markdown(f"""
        <div style="background:{band};padding:8px;border-radius:8px;text-align:center;font-size:10px;">
        {t}
        </div>
        """, unsafe_allow_html=True)

    for i in range(3):
        table = f"Table {i+1}"

        match = bookings[
            (bookings["Table"]==table)&
            (bookings["Time"]==t)&
            (bookings["Date"]==st.session_state.date)
        ]

        with cols[i+1]:
            if not match.empty:
                name = match.iloc[0]["Name"][:10]
                user = match.iloc[0]["User"]

                if user == st.session_state.user:
                    if st.button(f"❌ {name}", key=f"{t}_{i}"):
                        bookings = bookings.drop(match.index)
                        save(bookings, BOOKINGS_FILE)
                        st.rerun()
                else:
                    st.markdown(f"""
                    <div style="background:#fecaca;padding:8px;border-radius:8px;text-align:center;font-size:10px;">
                    {name}
                    </div>
                    """, unsafe_allow_html=True)
            else:
                if st.button("+", key=f"{t}_{i}"):
                    bookings = pd.concat([bookings, pd.DataFrame([{
                        "User": st.session_state.user,
                        "Name": st.session_state.name,
                        "Date": st.session_state.date,
                        "Table": table,
                        "Time": t
                    }])])
                    save(bookings, BOOKINGS_FILE)
                    st.rerun()

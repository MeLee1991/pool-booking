# ================= TABLE (FIXED LAYOUT) =================
st.markdown("""
<style>

/* force compact mobile width */
.block-container {
    max-width: 360px !important;
    padding: 0.5rem !important;
}

/* force 4 columns */
div[data-testid="stHorizontalBlock"] {
    display:flex !important;
    flex-wrap:nowrap !important;
    gap:4px !important;
}

/* column width (WIDER) */
[data-testid="column"] {
    flex:1 1 0 !important;
    min-width:0 !important;
}

/* buttons */
.stButton > button {
    width:100% !important;
    height:36px !important;
    font-size:9px !important;
    border-radius:12px !important;
    padding:0 !important;
}

/* FREE */
.free button {
    background:#bbf7d0 !important;
    color:#065f46 !important;
}

/* BOOKED */
.taken button {
    background:#fecaca !important;
    color:#7f1d1d !important;
}

/* MINE */
.mine button {
    background:#fca5a5 !important;
    color:#7f1d1d !important;
    font-weight:bold;
}

/* TIME COLORS (every 4 hours) */
.timeA button { background:#f3f4f6 !important; }
.timeB button { background:#e0f2fe !important; }
.timeC button { background:#fef3c7 !important; }
.timeD button { background:#ede9fe !important; }

</style>
""", unsafe_allow_html=True)

# header
h = st.columns(4)
h[0].markdown("**Time**")
h[1].markdown("**T1**")
h[2].markdown("**T2**")
h[3].markdown("**T3**")

HOURS = [f"{h:02d}:{m}" for h in range(6,24) for m in ["00","30"]]

for idx, t in enumerate(HOURS):
    cols = st.columns(4)

    block = ["timeA","timeB","timeC","timeD"][(idx//8)%4]

    # TIME
    with cols[0]:
        st.markdown(f'<div class="{block}">', unsafe_allow_html=True)
        st.button(t, key=f"time_{t}")
        st.markdown("</div>", unsafe_allow_html=True)

    # TABLES
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
                    st.markdown('<div class="mine">', unsafe_allow_html=True)
                    if st.button(f"✖ {name}", key=f"{t}_{i}"):
                        bookings = bookings.drop(match.index)
                        save(bookings, BOOKINGS_FILE)
                        st.rerun()
                    st.markdown("</div>", unsafe_allow_html=True)
                else:
                    st.markdown('<div class="taken">', unsafe_allow_html=True)
                    st.button(name, key=f"{t}_{i}", disabled=True)
                    st.markdown("</div>", unsafe_allow_html=True)
            else:
                st.markdown('<div class="free">', unsafe_allow_html=True)
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
                st.markdown("</div>", unsafe_allow_html=True)

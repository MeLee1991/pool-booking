# ==========================================
# SETTINGS (you can tweak later)
# ==========================================
TABLES = ["Table 1", "Table 2", "Table 3"]
START_HOUR = 8
END_HOUR = 24
STEP_MIN = 30  # 30 = half hour

# TIME LIST
times = [
    f"{h:02d}:{m:02d}"
    for h in range(START_HOUR, END_HOUR)
    for m in range(0, 60, STEP_MIN)
]

df = pd.read_sql_query(
    "SELECT * FROM bookings WHERE date=?",
    db(), params=(str(date),)
)

# ==========================================
# GRID CSS (IMPORTANT)
# ==========================================
st.markdown("""
<style>
.grid-wrap {
    overflow-x: auto;
}

.grid {
    display: grid;
    grid-template-columns: 70px repeat(3, 90px);
    gap: 6px;
    min-width: 350px;
}

.cell {
    text-align: center;
    font-size: 12px;
}

.header {
    font-weight: 600;
    position: sticky;
    top: 0;
    background: white;
    z-index: 10;
    padding: 4px;
}

.time {
    text-align: right;
    padding-right: 6px;
    color: #666;
}

.slot button {
    width: 100%;
    height: 34px;
    border-radius: 10px;
}

.prime button {
    background: #ff9500 !important;
    color: white !important;
    font-weight: 700;
}
</style>
""", unsafe_allow_html=True)

# ==========================================
# GRID RENDER
# ==========================================
st.markdown('<div class="grid-wrap"><div class="grid">', unsafe_allow_html=True)

# HEADER ROW
st.markdown('<div class="cell header">Time</div>', unsafe_allow_html=True)
for t in TABLES:
    st.markdown(f'<div class="cell header">{t}</div>', unsafe_allow_html=True)

# ROWS
for t in times:

    hour = int(t[:2])
    is_prime = 17 <= hour <= 22

    # TIME CELL
    st.markdown(f'<div class="cell time">{t}</div>', unsafe_allow_html=True)

    for tbl in TABLES:

        slot = df[
            (df["table_name"] == tbl) &
            (df["time"] == t)
        ]

        key = f"{tbl}_{t}"

        # SLOT STYLE
        css_class = "slot prime" if is_prime else "slot"

        st.markdown(f'<div class="cell {css_class}">', unsafe_allow_html=True)

        if not slot.empty:
            u = slot.iloc[0]["user"]

            if u == st.session_state.user:
                if st.button("❌", key=key):
                    db().execute(
                        "DELETE FROM bookings WHERE user=? AND date=? AND table_name=? AND time=?",
                        (u, str(date), tbl, t)
                    )
                    db().commit()
                    st.rerun()
            else:
                st.button("🔒", key=key, disabled=True)

        else:
            if st.button("🟢", key=key):
                db().execute(
                    "INSERT INTO bookings VALUES (?,?,?,?)",
                    (st.session_state.user, str(date), tbl, t)
                )
                db().commit()
                st.rerun()

        st.markdown('</div>', unsafe_allow_html=True)

st.markdown('</div></div>', unsafe_allow_html=True)

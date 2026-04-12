# ================= TABLE (WORKING VERSION) =================
today = datetime.now().date()
HOURS = [f"{h:02d}:{m}" for h in range(6,24) for m in ["00","30"]]

# ===== VISUAL GRID (HTML ONLY) =====
grid_html = '<div class="grid">'
grid_html += '<div class="cell">T</div><div class="cell">1</div><div class="cell">2</div><div class="cell">3</div>'

for idx, t in enumerate(HOURS):
    color = ["tA","tB","tC","tD"][(idx//8)%4]
    grid_html += f'<div class="cell {color}">{t}</div>'

    for i in range(3):
        table = f"Table {i+1}"

        match = st.session_state.bookings[
            (st.session_state.bookings["Table"]==table) &
            (st.session_state.bookings["Time"]==t) &
            (st.session_state.bookings["Date"]==st.session_state.sel_date)
        ]

        if not match.empty:
            name = match.iloc[0]["Name"][:3]
            user = match.iloc[0]["User"]

            if user == st.session_state.user:
                grid_html += f'<div class="cell mine">{name}</div>'
            else:
                grid_html += f'<div class="cell taken">{name}</div>'
        else:
            grid_html += f'<div class="cell free">+</div>'

grid_html += '</div>'

st.markdown(grid_html, unsafe_allow_html=True)


# ===== CLICKABLE LAYER (REAL BUTTONS) =====
for idx, t in enumerate(HOURS):

    cols = st.columns(4)

    # time (no action)
    cols[0].button(t, key=f"time_{t}", disabled=True)

    for i in range(3):
        table = f"Table {i+1}"

        match = st.session_state.bookings[
            (st.session_state.bookings["Table"]==table) &
            (st.session_state.bookings["Time"]==t) &
            (st.session_state.bookings["Date"]==st.session_state.sel_date)
        ]

        if not match.empty:
            user = match.iloc[0]["User"]

            if user == st.session_state.user:
                if cols[i+1].button("❌", key=f"{t}_{i}"):
                    st.session_state.bookings = st.session_state.bookings.drop(match.index)
                    save_data(st.session_state.bookings, BOOKINGS_FILE)
                    st.rerun()
            else:
                cols[i+1].button("X", key=f"{t}_{i}", disabled=True)

        else:
            if cols[i+1].button("+", key=f"{t}_{i}"):
                new = pd.DataFrame([{
                    "User": st.session_state.user,
                    "Name": st.session_state.name,
                    "Date": st.session_state.sel_date,
                    "Table": table,
                    "Time": t
                }])
                st.session_state.bookings = pd.concat([st.session_state.bookings,new])
                save_data(st.session_state.bookings, BOOKINGS_FILE)
                st.rerun()

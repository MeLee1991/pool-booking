st.markdown("""
<style>

/* GLOBAL */
.block-container {
    max-width: 900px;
    padding-top: 1rem;
}

/* DATE BAR */
[data-testid="stRadio"] {
    position: sticky;
    top: 0;
    background: #f8f9fa;
    z-index: 100;
    padding: 6px;
}

/* FORCE 2 ROWS */
[data-testid="stRadio"] > div {
    display: grid !important;
    grid-template-columns: repeat(7,1fr) !important;
    grid-template-rows: auto auto !important;
    gap: 4px;
}

/* HEADERS */
.table-header {
    position: sticky;
    top: 60px;
    background: #1e1e1e;
    color: white;
    text-align: center;
    font-size: 13px;
    padding: 6px;
    border-radius: 8px;
    margin-bottom: 6px;
}

/* BUTTON BASE */
button {
    border-radius: 999px !important;
    height: 26px !important;
    font-size: 11px !important;
    padding: 0 !important;
    transition: all 0.12s ease !important;
}

/* FREE */
button[kind="secondary"] {
    background: #f1f3f5 !important;
    border: 1px solid #dee2e6 !important;
}

/* YOUR SLOT */
button[kind="primary"] {
    background: linear-gradient(180deg,#ff4d4f,#dc3545) !important;
    color: white !important;
}

/* LOCKED */
button[disabled] {
    background: #f8d7da !important;
    color: #842029 !important;
}

/* HOVER */
button:hover {
    filter: brightness(0.95);
}

/* CLICK */
button:active {
    transform: scale(0.95);
}

/* ROW GROUPING (every 4 rows) */
.slot-row-0 { background: #f8f9fa; }
.slot-row-1 { background: #eef7ff; }

/* PRIME TIME */
.prime {
    background: linear-gradient(90deg,#fff3cd,#ffe8a1);
}

/* MOBILE: FORCE 3 COLUMNS */
@media (max-width: 900px) {
    [data-testid="stHorizontalBlock"] {
        display: flex !important;
        flex-wrap: nowrap !important;
        gap: 4px !important;
    }

    [data-testid="column"] {
        width: 33% !important;
        flex: 1 1 33% !important;
    }

    button {
        font-size: 9px !important;
        height: 24px !important;
    }
}

</style>
""", unsafe_allow_html=True)

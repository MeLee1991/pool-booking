import streamlit as st
import pandas as pd
import os
from datetime import datetime, timedelta

st.set_page_config(page_title="Poolhall", layout="centered", initial_sidebar_state="collapsed")

# ===============================
# CONFIG & FILES
# ===============================
BOOKINGS_FILE = "bookings.csv"
OWNER_EMAIL = "admin@gmail.com"

# ===============================
# THE UNBREAKABLE CSS
# ===============================
st.markdown("""
<style>
    /* Prevent overall page padding issues on mobile */
    .block-container { padding: 1rem 5px !important; max-width: 100% !important; }
    
    /* 1. DATE SELECTOR - Horizontal Scroll Only */
    div[data-testid="stHorizontalBlock"]:has(button[key^="date_"]) {
        display: flex !important;
        flex-direction: row !important; /* Force horizontal */
        flex-wrap: nowrap !important;
        overflow-x: auto !important;
        gap: 6px !important;
    }
    div[data-testid="stHorizontalBlock"]:has(button[key^="date_"]) > div {
        min-width: 82px !important; /* 1.5x width */
        flex: 0 0 auto !important;
    }

    /* 2. MAIN TABLE - Prevent 1-Column Collapse */
    .table-wrapper div[data-testid="stHorizontalBlock"] {
        display: flex !important;
        flex-direction: row !important; /* Stop mobile stacking */
        flex-wrap: nowrap !important;
        gap: 4px !important;
        margin-bottom: 4px !important;
        width: 100% !important;
    }
    
    /* Force columns to be exactly 1/4 width */
    .table-wrapper div[data-testid="column"] {
        width: 25% !important;
        flex: 1 1 25% !important;
        min-width: 0 !important;
    }

    /* 3. BUTTONS - Blocky & Same Size as Headers */
    .stButton > button {
        width: 100% !important;
        height: 44px !important; 
        border-radius: 4px !important;
        border: none !important;
        padding: 0 !important;
        margin: 0 !important;
    }
    .stButton > button p {
        font-size: 9px !important; /* 2px smaller */
        font-weight: 800 !important;
    }

    /* 4. COLORS & UI */
    .table-wrapper button[kind="secondary"] { background-color: #28a745 !important; color: white !important; }
    .table-wrapper button[kind="primary"] { background-color: #dc3545 !important; color: white !important; }
    button[key^="date_"][kind="primary"] { background-color: #007bff !important; color: white !important; }

    .grid-header {
        background-color: #111; color: #fff; text-align: center;
        font-size

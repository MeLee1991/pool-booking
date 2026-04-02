{\rtf1\ansi\ansicpg1252\cocoartf2822
\cocoatextscaling0\cocoaplatform0{\fonttbl\f0\fswiss\fcharset0 Helvetica;}
{\colortbl;\red255\green255\blue255;}
{\*\expandedcolortbl;;}
\paperw11900\paperh16840\margl1440\margr1440\vieww11520\viewh8400\viewkind0
\pard\tx720\tx1440\tx2160\tx2880\tx3600\tx4320\tx5040\tx5760\tx6480\tx7200\tx7920\tx8640\pardirnatural\partightenfactor0

\f0\fs24 \cf0 import streamlit as st\
import pandas as pd\
from datetime import datetime, timedelta\
\
st.set_page_config(page_title="Pool Club - 9ft Tables", layout="wide")\
\
# Title and Info\
st.title("\uc0\u55356 \u57265  Table Reservations")\
st.info("Limit: 3 hours per person per day.")\
\
# --- DATA STORAGE ---\
# For a real app, we use a simple CSV to remember bookings\
if 'bookings' not in st.session_state:\
    st.session_state.bookings = pd.DataFrame(columns=['User', 'Date', 'Table', 'Time', 'Duration'])\
\
# --- SIDEBAR: BOOKING FORM ---\
st.sidebar.header("Reserve a Table")\
name = st.sidebar.text_input("Your Name")\
date = st.sidebar.date_input("Date", datetime.now())\
table = st.sidebar.selectbox("Select Table", ["Table 1", "Table 2", "Table 3"])\
time_slot = st.sidebar.selectbox("Start Time", [f"\{h:02d\}:00" for h in range(8, 24)])\
hrs = st.sidebar.number_input("How many hours?", min_value=1, max_value=3, step=1)\
\
if st.sidebar.button("Confirm Booking"):\
    if name:\
        # Check 3-hour limit\
        user_today = st.session_state.bookings[\
            (st.session_state.bookings['User'] == name) & \
            (st.session_state.bookings['Date'] == date)\
        ]['Duration'].sum()\
        \
        if user_today + hrs > 3:\
            st.sidebar.error(f"Cannot book. You already have \{user_today\}h booked for this day.")\
        else:\
            new_data = pd.DataFrame([[name, date, table, time_slot, hrs]], \
                                    columns=['User', 'Date', 'Table', 'Time', 'Duration'])\
            st.session_state.bookings = pd.concat([st.session_state.bookings, new_data], ignore_index=True)\
            st.sidebar.success("Booked successfully!")\
    else:\
        st.sidebar.warning("Please enter a name.")\
\
# --- MAIN DISPLAY: THE SCHEDULE ---\
view_date = st.date_input("View Schedule for:", datetime.now())\
relevant_bookings = st.session_state.bookings[st.session_state.bookings['Date'] == view_date]\
\
# Create 3 columns for 3 tables\
t1, t2, t3 = st.columns(3)\
\
for i, col in enumerate([t1, t2, t3]):\
    t_name = f"Table \{i+1\}"\
    col.subheader(t_name)\
    \
    for hour in range(8, 24):\
        h_str = f"\{hour:02d\}:00"\
        # Check if booked\
        booked = relevant_bookings[(relevant_bookings['Table'] == t_name) & (relevant_bookings['Time'] == h_str)]\
        \
        if not booked.empty:\
            col.error(f"\uc0\u55357 \u56628  \{h_str\} - \{booked.iloc[0]['User']\}")\
        else:\
            col.success(f"\uc0\u55357 \u57314  \{h_str\} - FREE")}
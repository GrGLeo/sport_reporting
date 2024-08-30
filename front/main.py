import streamlit as st
from datetime import datetime
from db_setup import Base, engine, session

st.title("Welcome to the dashboard!")

if 'db_session' not in st.session_state:
    st.session_state.db_engine = engine
    st.session_state.db_session = session
    st.session_state.db_base = Base
    print("Hello")

target_date = datetime(2025, 6, 1)
today = datetime.now()
difference = target_date - today

weeks = difference.days // 7
days = difference.days % 7

st.write(f"IRONMAN HAMBURG Date: {target_date.strftime('%Y-%m-%d')}")
col1, col2 = st.columns(2)
with col1:
    st.write(f"Weeks remaining: {weeks}")
with col2:
    st.write(f"Days remaining: {days}")

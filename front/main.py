import streamlit as st
from datetime import datetime
import pandas as pd
from sqlalchemy import desc
from db_setup import Base, engine, session, Threshold


st.title("Welcome to the dashboard!")

if 'db_session' not in st.session_state:
    st.session_state.db_engine = engine
    st.session_state.db_session = session
    st.session_state.db_base = Base
    st.session_state.db_threshold = Threshold
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

# Threshold query
st.title("Threshold")
threshold = session.query(Threshold).order_by(desc(Threshold.date)).first()
if threshold:
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(label="swim css", value=threshold.swim)
    with col2:
        st.metric(label="bike ftp", value=threshold.ftp)
    with col3:
        st.metric(label="run threshold", value=threshold.run_pace)

# Weekly stats
# Weekly hour, Weekly TSS, time portion per sport
df_week = pd.read_sql('select * from syn_running', engine)
df_week['week'] = df_week['date'].dt.isocalendar().week
df_week = df_week.groupby('week').agg({'tss': 'sum'})
st.write(df_week)



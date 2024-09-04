import streamlit as st
from datetime import datetime, timedelta
import pandas as pd
from sqlalchemy import desc
import plotly.express as px
import plotly.graph_objects as go

from db_setup import Base, engine, session, Threshold
from metrics import calculate_all


st.set_page_config(
    page_title='Training',
    page_icon="🧊",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("Welcome to the dashboard!")

conn = st.connection('postgresql', type='sql')
if 'db_session' not in st.session_state:
    st.session_state.db_engine = engine
    st.session_state.db_session = session
    st.session_state.db_base = Base
    st.session_state.db_threshold = Threshold

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

threshold_col, _ = st.columns([0.2, 0.8])

with threshold_col:
    st.title("Threshold")
    query = """
        SELECT *
        FROM threshold
        ORDER BY date DESC
        LIMIT 1
        """
    threshold = conn.query(query)
    if not threshold.empty:
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric(label="swim css", value=threshold.swim)
        with col2:
            st.metric(label="bike ftp", value=threshold.ftp)
        with col3:
            st.metric(label="run threshold", value=threshold.run_pace)

# TODO Refacto df with all day; join three sport then group by day and week

st.title("Weekly Stats")
df_syn_run = pd.read_sql('select * from syn_running', engine)
df_week = df_syn_run.copy()
df_week['week'] = df_week['date'].dt.isocalendar().week
df_week['hour'] = df_week['duration'].apply(lambda x: x.hour)
df_week['minute'] = df_week['duration'].apply(lambda x: x.minute)
df_week['second'] = df_week['duration'].apply(lambda x: x.second)
df_week['duration'] = df_week['hour'] * 3600 + df_week['minute'] * 60 + df_week['second']
df_week = df_week.groupby('week', as_index=False).agg({'duration': 'sum', 'tss': 'sum'})

col1, col2, col3 = st.columns(3)
with col1:
    fig = px.bar(df_week, x='week', y='tss')
    st.plotly_chart(fig)
with col2:
    fig = px.bar(df_week, x='week', y='duration', orientation='v')
    st.plotly_chart(fig)

# CTL, FORM, FITNESS
end_date = datetime.today()
start_date = end_date - timedelta(days=92)
date_range = pd.date_range(start=start_date, end=end_date)
date_range = date_range.strftime('%Y-%m-%d')
df = pd.DataFrame({'date': date_range})

df_daily = df_syn_run.copy()
df_daily['date'] = df_daily['date'].dt.strftime('%Y-%m-%d')
df_daily = df.merge(df_daily, on='date', how='left')

df_daily = df_daily.groupby('date', as_index=False).agg({'tss': 'sum'})
df_daily = df_daily.sort_values('date')
df_daily = calculate_all(df_daily)

fig = go.Figure()
fig.add_trace(go.Scatter(
    x=df_daily['date'],
    y=df_daily['ctl'],
    fill='tozeroy',
    name='Fitness',
    mode='none',
    fillcolor='rgba(200, 179, 125, 0.9)'
))

fig.add_trace(go.Scatter(
    x=df_daily['date'],
    y=df_daily['atl'],
    fill='tonexty',
    name='Fatigue',
    mode='none'
))

fig.add_trace(go.Scatter(
    x=df_daily['date'],
    y=df_daily['form'],
    name='Form',
))

# Add bar plot for BarValue
fig.add_trace(go.Bar(
    x=df_daily['date'],
    y=df_daily['tss'],
    name='TSS',
    marker=dict(color='rgba(0, 0, 0, 0.8)')
))

fig.update_layout(
    title='Fitness trend',
    xaxis_title='Date',
    yaxis_title='Values',
    barmode='overlay',
    xaxis=dict(
        type='category',  # Treat x-axis as categorical data
        rangeslider=dict(visible=False),  # Show range slider
        fixedrange=False
    )
)

st.plotly_chart(fig)

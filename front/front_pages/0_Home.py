import streamlit as st
from datetime import date
import plotly.express as px
import plotly.graph_objects as go

from utilities.event import create_event
from db_setup import Base, engine, session, Threshold
from metrics import calculate_all
from front.user.user import User


st.title("Welcome to your dashboard!")

conn = st.connection('postgresql', type='sql')
user = User(st.session_state['user_token'], conn)

if 'db_session' not in st.session_state:
    st.session_state.db_engine = engine
    st.session_state.db_session = session
    st.session_state.db_base = Base
    st.session_state.db_threshold = Threshold
    st.session_state.user = user

home_tab, zone_tab = st.tabs(["Home", "Zone"])
with home_tab:
    with st.expander("Add Event"):
        create_event(st.session_state['user_token'])
    today = date.today()

    # Event display
    df_events = user.get_events()
    cols = st.columns(len(df_events))
    for i, row in df_events.iterrows():
        cols[i].subheader(f"{row['name']} Priority: {row.priority}")
        cols[i].write(f"{row.date.strftime('%Y-%m-%d')}")
        cols[i].write(f"Sport: {row.sport}")
        difference = row.date - today
        weeks = difference.days // 7
        cols[i].write(f"Weeks remaining: {weeks}")

    st.header("Weekly Stats")
    total_wkt = user.get_full_workouts()
    df_week = total_wkt.groupby('week', as_index=False).agg({'duration': 'sum', 'tss': 'sum'})

    col1, col2, col3 = st.columns(3)
    with col1:
        fig = px.bar(df_week, x='week', y='tss')
        st.plotly_chart(fig)
    with col2:
        fig = px.bar(df_week, x='week', y='duration', orientation='v')
        st.plotly_chart(fig)

    # CTL, FORM, FITNESS
    df_daily = total_wkt.groupby('date', as_index=False).agg({'tss': 'sum'})
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
            type='category',
            rangeslider=dict(visible=False),
            fixedrange=False
        )
    )

    st.plotly_chart(fig)

with zone_tab:
    threshold_col, _ = st.columns([0.2, 0.8])

    with threshold_col:
        st.header("Threshold")
        threshold = user.get_threshold()
        if not threshold.empty:
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric(label="Swim", value=threshold.swim)
            with col2:
                st.metric(label="Bike", value=threshold.ftp)
            with col3:
                st.metric(label="Run", value=threshold.vma)

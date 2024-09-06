import datetime
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

conn = st.connection('postgresql', type='sql')


def insert_space(number: int):
    for i in range(number):
        st.write("\n")


def time_to_seconds(t):
    h, m, s = t.hour, t.minute, t.second
    time = datetime.timedelta(hours=h, minutes=m, seconds=s).total_seconds()
    return int(time)


st.title("Workout analystics")

db_engine = st.session_state.db_engine

if 'activity_id' not in st.session_state:
    st.error('Please select an activity in the calendar')
    st.stop()

activity_id = st.session_state.activity_id

# Activity specific
col1, col2 = st.columns([0.3, 0.7])
if activity_id:
    params = {'activity_id': activity_id, 'user_id': st.session_state['user_token']}
    query = "SELECT * FROM running.lap where activity_id = :activity_id and user_id = :user_id"
    df = conn.query(query, params=params)

    df = df.drop('activity_id', axis=1)
    df['distance'] = df['distance'] / 1000
    df['distance'] = df['distance'].round(2)

    with col1:
        insert_space(3)
        st.dataframe(df, hide_index=True)

    df['time_seconds'] = df['timer'].apply(time_to_seconds)

    df['start_seconds'] = df['time_seconds'].cumsum() - df['time_seconds']
    df['end_seconds'] = df['start_seconds'] + df['time_seconds']

    df['start_time'] = pd.to_datetime(df['start_seconds'], unit='s')
    df['end_time'] = pd.to_datetime(df['end_seconds'], unit='s')

    fig = px.timeline(df, x_start='start_time', x_end='end_time', y='pace',
                      labels={'start_time': 'Start Time', 'end_time': 'End Time'})

    # Update layout
    fig.update_layout(
        xaxis_title='Activity Duration',
        yaxis_title='Pace',
        yaxis=dict(
            tickvals=df['pace'],
            ticktext=df['pace']
        ),
        xaxis=dict(
            tickformat='%H:%M:%S',
            dtick='360000',
            showgrid=True,
            zeroline=True
        )
    )
    fig.update_yaxes(range=[2, df['pace'].max() + 1])

    with col2:
        st.plotly_chart(fig)

# Record specific
    query = "select * from running.workout where activity_id = :activity_id and user_id = :user_id"
    df = conn.query(query, params=params)

    altitude_min = df['altitude'].min()
    altitude_max = df['altitude'].max()

    margin = 0.1 * (altitude_max - altitude_min)

    altitude_range_min = altitude_min - margin
    altitude_range_max = altitude_max + margin

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df['distance'],
        y=df['altitude'],
        yaxis='y',
        fill='tozeroy',
        name='Altitude',
        mode='none',
        fillcolor='rgba(125, 125, 125, 0.5)',
        hovertemplate='%{y}<extra></extra>'
                  )
    )

    fig.add_trace(go.Scatter(
        x=df['distance'],
        y=df['pace'],
        yaxis='y2',
        name='Pace',
        mode='lines',
        fillcolor='rgba(0, 0, 255, 1)',
        hovertemplate='%{y}<extra></extra>'
                  )
    )

    fig.add_trace(go.Scatter(
        x=df['distance'],
        y=df['hr'],
        yaxis='y3',
        name='Heart rate',
        mode='lines',
        fillcolor='rgba(255, 0, 0, 1)',
        hovertemplate='%{y}<extra></extra>'
                  )
    )

    fig.update_layout(
        title='Altitude, Pace, and Heart Rate Over Time',
        xaxis=dict(title='Distance (km)'),
        yaxis=dict(
            range=[altitude_range_min, altitude_range_max],
            showticklabels=False,
            showgrid=False,
            zeroline=False,
            showline=False
        ),
        yaxis2=dict(
            title='Pace (min/km)',
            titlefont=dict(color='blue'),
            tickfont=dict(color='blue'),
            anchor='free',
            overlaying='y',
            side='left',
        ),
        yaxis3=dict(
            title='Heart Rate (bpm)',
            titlefont=dict(color='red'),
            tickfont=dict(color='red'),
            showgrid=False,
            anchor='free',
            overlaying='y',
            side='right',
            position=1
        )
    )

    st.plotly_chart(fig)

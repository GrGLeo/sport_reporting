import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from utilities.comment import add_comment, write_comment
from utils import time_to_seconds
from user.user import User


conn = st.connection('postgresql', type='sql')


st.title("Workout analystics")

db_engine = st.session_state.db_engine

if 'activity_id' not in st.session_state:
    st.error('Please select an activity in the calendar')
    st.stop()

activity_id, sport, planned = st.session_state.activity_id
user: User = st.session_state.user

if planned:
    st.error('Please select an activity in the calendar')
    st.stop()

# Activity specific
col1, col2, col3 = st.columns([0.30, 0.40, 0.3])
if activity_id:
    df_laps, df_zones, df_records = user.get_analysis(sport, activity_id)
    y = 'pace' if sport == 'running' else 'power'

    with col1:
        st.dataframe(df_laps, hide_index=True)

    with col2:
        st.markdown("""
            <style>
            .bar-container {
                width: 100%;
                margin-bottom: 8px;
            }
            .bar-label {
                font-size: 12px;
                font-weight: bold;
                margin-bottom: 5px;
            }
            .bar {
                height: 25px;
                width: 100%;
                background-color: lightgrey;
                border-radius: 5px;
                overflow: hidden;
                position: relative;
            }
            .bar-filled {
                height: 100%;
                background-color: skyblue;
                text-align: center;
                color: white;
                font-size: 14px;
                line-height: 30px;
                border-radius: 5px;
            }
            </style>
        """, unsafe_allow_html=True)

        df_zones.fillna(0, inplace=True)
        for col in df_zones.columns:
            value = df_zones.iloc[0][col]
            st.markdown(f"""
            <div class="bar-container">
                <div class="bar-label">{col}</div>
                <div class="bar">
                    <div class="bar-filled" style="width: {value}%;">
                        {value}%
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

    with col3:
        st.subheader('Comments')
        write_comment(conn, activity_id)
        add_com = st.button('Comments')
        if add_com:
            add_comment(activity_id)

    record_tab, lap_tab = st.tabs(["Workout", "Laps"])

    # Record specific
    with record_tab:
        altitude_min = df_records['altitude'].min()
        altitude_max = df_records['altitude'].max()

        margin = 0.1 * (altitude_max - altitude_min)

        altitude_range_min = altitude_min - margin
        altitude_range_max = altitude_max + margin

        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=df_records['distance'],
            y=df_records['altitude'],
            yaxis='y',
            fill='tozeroy',
            name='Altitude',
            mode='none',
            fillcolor='rgba(125, 125, 125, 0.5)',
            hovertemplate='%{y}<extra></extra>'
        )
                      )

        fig.add_trace(go.Scatter(
            x=df_records['distance'],
            y=df_records[y],
            yaxis='y2',
            name='Pace',
            mode='lines',
            fillcolor='rgba(0, 0, 255, 1)',
            hovertemplate='%{y}<extra></extra>'
        )
                      )

        fig.add_trace(go.Scatter(
            x=df_records['distance'],
            y=df_records['hr'],
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
                titlefont=dict(color='red'),
                title='Heart Rate (bpm)',
                tickfont=dict(color='red'),
                showgrid=False,
                anchor='free',
                overlaying='y',
                side='right',
                position=1
            )
        )

        st.plotly_chart(fig)

    # Laps tab
    with lap_tab:
        df_laps['timer_seconds'] = df_laps['timer'].apply(time_to_seconds)
        df_laps['cumulative_time'] = df_laps['timer_seconds'].cumsum()

        total_duration = int(df_laps['cumulative_time'].max())
        time_seconds = pd.DataFrame({'second': range(total_duration + 1)})
        time_seconds['pace'] = None
        time_seconds['hr'] = None

        for i, lap in df_laps.iterrows():
            start_time = 0 if i == 0 else df_laps.loc[i - 1, 'cumulative_time']
            end_time = lap['cumulative_time']
            time_seconds.loc[(time_seconds['second'] >= start_time) & (time_seconds['second'] <= end_time), 'pace'] = lap['pace']
            time_seconds.loc[(time_seconds['second'] >= start_time) & (time_seconds['second'] <= end_time), 'hr'] = lap['hr']

        fig = go.Figure()

        fig.add_trace(go.Scatter(
            x=time_seconds['second'],
            y=time_seconds['pace'],
            name='Pace',
            mode='lines',
            line=dict(color='blue'),
            hovertemplate='%{y}<extra></extra>'
        )
                      )
        fig.update_layout(
            title='Pace per lap over time',
            xaxis=dict(title='Time (sec)'),
            yaxis=dict(
                title='Speed km/h',
                range=[0, 22],
            )
        )

        st.plotly_chart(fig)

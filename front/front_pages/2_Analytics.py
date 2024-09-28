import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from utilities.comment import add_comment, write_comment
from front.user.user import User


conn = st.connection('postgresql', type='sql')


st.title("Workout analystics")

db_engine = st.session_state.db_engine

if 'activity_id' not in st.session_state:
    st.error('Please select an activity in the calendar')
    st.stop()

activity_id, sport = st.session_state.activity_id
user: User = st.session_state.user

# Activity specific
col1, col2, col3 = st.columns([0.30, 0.40, 0.3])
if activity_id:
    df_laps, df_zones, df_records = user.get_analysis(sport, activity_id)
    y = 'pace' if sport == 'running' else 'power'

    with col1:
        st.dataframe(df_laps, hide_index=True)

#    df_laps['time_seconds'] = df_laps['timer'].apply(time_to_seconds)
#
#    df_laps['start_seconds'] = df_laps['time_seconds'].cumsum() - df_laps['time_seconds']
#    df_laps['end_seconds'] = df_laps['start_seconds'] + df_laps['time_seconds']
#
#    df_laps['start_time'] = pd.to_datetime(df_laps['start_seconds'], unit='s')
#    df_laps['end_time'] = pd.to_datetime(df_laps['end_seconds'], unit='s')
#
#    fig = px.timeline(df_laps, x_start='start_time', x_end='end_time', y=y,
#                      labels={'start_time': 'Start Time', 'end_time': 'End Time'})
#
#    fig.update_layout(
#        xaxis_title='Activity Duration',
#        yaxis_title='Pace',
#        yaxis=dict(
#            tickvals=df_laps[y],
#            ticktext=df_laps[y]
#        ),
#        xaxis=dict(
#            tickformat='%H:%M:%S',
#            dtick='360000',
#            showgrid=True,
#            zeroline=True
#        )
#    )
#    fig.update_yaxes(range=[2, df_laps[y].max() + 1])

    with col2:
        st.markdown("""
            <style>
            .bar-container {
                width: 100%;
                margin-bottom: 20px;
            }
            .bar-label {
                font-size: 12px;
                font-weight: bold;
                margin-bottom: 5px;
            }
            .bar {
                height: 30px;
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

        for col in df_zones.columns:
            st.markdown(f"""
            <div class="bar-container">
                <div class="bar-label">{col}</div>
                <div class="bar">
                    <div class="bar-filled" style="width: {df_zones.iloc[0][col]}%;">
                        {df_zones.iloc[0][col]}%
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

# Record specific
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

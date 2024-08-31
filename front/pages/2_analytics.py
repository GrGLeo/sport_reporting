import datetime
import streamlit as st
import pandas as pd
import plotly.express as px


def time_to_seconds(t):
    h, m, s = t.hour, t.minute, t.second
    time = datetime.timedelta(hours=h, minutes=m, seconds=s).total_seconds()
    return int(time)


st.title("Workout analystics")

db_engine = st.session_state.db_engine

df = pd.read_sql("SELECT * FROM lap_running", db_engine)
st.write(df)

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

st.plotly_chart(fig)

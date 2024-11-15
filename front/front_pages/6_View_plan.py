import os
import requests
import streamlit as st
import pandas as pd
import plotly.express as px


if 'activity_id' not in st.session_state:
    st.error('Please select a planned activity in the calendar')
    st.stop()


user = st.session_state.user
user_id = st.session_state.user_token
activity_id, sport, planned = st.session_state.activity_id

if not planned:
    st.error('Please select a planned activity in the calendar')
    st.stop()

st.title('Planned Workout')
df_wkt = user.get_programmed_wkt(activity_id)
data = df_wkt['data'].iloc[0]
name = df_wkt['name'].iloc[0]
date = df_wkt['date'].iloc[0]
st.subheader(date)

def extract_data(d: dict, parent_key: str=""):
    rows = []
    for k, v in d.items():
        new_key = f"{parent_key}_{k}" if parent_key else k
        if isinstance(v, dict):
            if 'timer' in v and 'work' in v:
                rows.append(
                    {
                        'key': new_key,
                        'timer': v['timer'],
                        'work': v['work']
                    }
                )
            else:
                rows.extend(extract_data(v, new_key))
    return rows


data = extract_data(data)

df = pd.DataFrame(data, columns=['key', 'timer', 'work'])
df = df.reset_index(drop=True)

df['start_time'] = df['timer'].cumsum() - df['timer']
df['end_time'] = df['timer'].cumsum()

plot_data = []
for _, row in df.iterrows():
    plot_data.append({'time': row['start_time'], 'work': row['work']})
    plot_data.append({'time': row['end_time'], 'work': row['work']})

plot_df = pd.DataFrame(plot_data)

fig = px.line(plot_df, x='time', y='work', title=name)
fig.update_layout(
        xaxis_title='Duration',
        yaxis_title='Speed (km/h)',
        yaxis=dict(range=[0, 21])
)

st.plotly_chart(fig)

# Download associated fit file
API = os.getenv("API_ENDPOINT", "http://127.0.0.1:8000")
response = requests.get(f"{API}/download-file/{name}")

if response.status_code == 200:
    file_content = response.content

st.download_button('Download workout', file_content, file_name=f'{name}.fit', mime="application/stream-octet")

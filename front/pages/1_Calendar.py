import streamlit as st
from streamlit_calendar import calendar
import pandas as pd
from datetime import timedelta


def time_to_timedelta(t):
    return timedelta(hours=t.hour, minutes=t.minute, seconds=t.second)


engine = st.session_state.db_engine
conn = st.connection('postgresql', type='sql')

calendar_options = {
    "editable": "true",
    "selectable": "true",
    "height": 630,
    "headerToolbar": {
        "left": "today prev,next",
        "center": "title",
        "right": "dayGridMonth,listWeek",
    },
    "slotMinTime": "06:00:00",
    "slotMaxTime": "18:00:00",
    "initialView": "dayGridMonth",
    "resources": [
        {"id": "swim", "building": "Swim"},
        {"id": "bike", "building": "Bike"},
        {"id": "run", "building": "Run"},
    ],
}

custom_css = """
    .fc-event-past {
        opacity: 0.8;
    }
    .fc-event-time {
        font-style: italic;
    }
    .fc-event-title {
        font-weight: 700;
    }
    .fc-toolbar-title {
        font-size: 2rem;
    }
"""
cols = ['activity_id', 'date', 'duration']


query = "SELECT * FROM running.syn WHERE user_id = :user_id"
df_run = conn.query(query, params={'user_id': st.session_state['user_token']})
df_run = df_run[cols]
df_run['title'] = 'run'
df_run['end'] = df_run.apply(lambda row: row['date'] + time_to_timedelta(row['duration']), axis=1)

test = df_run.to_dict(orient='records')

calendar_event = [
    {
        'title': d['title'],
        'start': d['date'].strftime('%Y-%m-%dT%H:%M:%S'),
        'end': d['end'].strftime('%Y-%m-%dT%H:%M:%S'),
        'resourceId': d['title'],
        'id': d['activity_id'],
        'backgroundColor': 'red'
    }
    for d in test]

calendar = calendar(events=calendar_event, options=calendar_options, custom_css=custom_css)

upload = st.button('Upload')
if upload:
    st.switch_page('pages/3_Upload.py')

if 'callback' in calendar:
    if calendar['callback'] == "eventClick":
        st.write(calendar['eventClick']['event']['id'])
        st.session_state.activity_id = calendar['eventClick']['event']['id']
        st.switch_page('pages/2_Analytics.py')

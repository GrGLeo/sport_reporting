import streamlit as st
from streamlit_calendar import calendar
from datetime import timedelta


def time_to_timedelta(t):
    return timedelta(hours=t.hour, minutes=t.minute, seconds=t.second)


user = st.session_state['user']

calendar_options = {
    "editable": "true",
    "selectable": "true",
    "firstDay": 1,
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

events = user.get_calendar()
st.write(user.get_futur_wkt())
events = events.to_dict(orient='records')

calendar_event = [
    {
        'title': d['title'],
        'start': d['date'].strftime('%Y-%m-%dT%H:%M:%S'),
        'end': d['end'].strftime('%Y-%m-%dT%H:%M:%S'),
        'resourceId': d['title'],
        'id': d['activity_id'],
        'backgroundColor': 'red'
    }
    for d in events]

calendar = calendar(events=calendar_event, options=calendar_options, custom_css=custom_css)

upload = st.button('Upload')
if upload:
    st.switch_page('front_pages/3_Upload.py')

if 'callback' in calendar:
    if calendar['callback'] == "eventClick":
        st.write(calendar['eventClick']['event']['id'])
        st.session_state.activity_id = (calendar['eventClick']['event']['id'], calendar['eventClick']['event']['title'])
        st.switch_page('front_pages/2_Analytics.py')

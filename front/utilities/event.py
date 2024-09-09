import streamlit as st
import requests


def create_event(user_id):
    with st.form(key="event_form"):
        eventname = st.text_input("Event Name")
        date = st.date_input("Event Date")
        priority = ['A', 'B', 'C']
        priority = st.radio(label="priority", options=priority, horizontal=True)
        sport = ['Swim', 'Bike', 'Run', 'Triathlon']
        sport = st.selectbox("Sport selection", sport)
        submit = st.form_submit_button("Add Event!")
    if submit:
        json = {
            "user_id": user_id,
            "date": date.isoformat(),
            "name": eventname,
            "sport": sport,
            "priority": priority
        }
        requests.post(
            "http://127.0.0.1:8000/post_event",
            json=json
        )

import os
import streamlit as st
import requests
from utils import UnAuthorizeError


API = os.getenv("API_ENDPOINT", "http://127.0.0.1:8000")


def create_event(token):
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
            "date": date.isoformat(),
            "name": eventname,
            "sport": sport,
            "priority": priority
        }
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.post(
            f"{API}/post_event",
            json=json,
            headers=headers
        )

        if response.status_code == 401:
            del st.session_state["user_token"]
            st.rerun()
        elif response.status_code == 200:
            st.toast("Event added successfully", icon=":material/thumb_up:")
        elif response.status_code == 422:
            st.toast("Event can't be a past date")

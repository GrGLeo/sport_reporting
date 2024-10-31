import os
import streamlit as st
import requests


API = os.getenv("API_ENDPOINT", "http://127.0.0.1:8000")


@st.dialog('Add a comment')
def add_comment(activity_id):
    comment = st.text_area("Write your comment here")
    headers = {"Authorization": f"Bearer {st.session_state["user_token"]["access_token"]}"}

    if st.button("Submit"):
        json = {
                    "activity_id": activity_id,
                    "comment_text": comment,
                }
        response = requests.post(
                f"{API}/activity/post_comment",
                json=json,
                headers=headers
        )
        if response.status_code != 200:
            raise Exception(f'Error {response.status_code}')


def write_comment(conn, activity_id):
    response = requests.get(f"{API}/activity/get_comments/?activity_id={activity_id}")
    if response.status_code == 200:
        comments = response.json()['data']
    else:
        comments = [{"comment": "No comments yet"}]

    comment_section = """
        <div style='
            min-height: 100px;
            max-height: 100px;
            padding: 10px;
            border: 1px solid #ccc;
            border-radius: 5px;
            overflow-y: scroll;
            background-color: #f9f9f9;
        '>
    """

    for comment in comments:
        comment_section += f"<div style='padding: 5px; margin-bottom: 5px; border-bottom: 1px solid #ddd;'>{comment['comment']}</div>"

    # Close the scrollable container div
    comment_section += "</div>"

    # Render the entire comment section in one st.markdown call
    st.markdown(comment_section, unsafe_allow_html=True)


def get_rpe(sport, activity_id):
    response = requests.get(f"{API}/activity/{activity_id}/get_rpe/?sport={sport}")
    if response.status_code == 200:
        data = response.json()["data"]
        return data[0]["rpe"]
    else:
        return None


def rpe_setter(key):
    rpe = st.slider(
        "Rate of Perceived Exertion (RPE): 🟢 (1) - 🔴 (10)",
        min_value=1,
        max_value=10,
        value=1,
        step=1,
        key=key+"_slider")
    if st.button("Submit RPE", key=key+"_button"):
        return rpe


def post_rpe(sport, activity_id, rpe):
    json = {"activity_id": activity_id, "sport": sport, "rpe": rpe}
    headers = {"Authorization": f"Bearer {st.session_state["user_token"]["access_token"]}"}
    response = requests.post(f"{API}/activity/post_rpe/", json=json, headers=headers)
    if response.status_code == 200:
        return True


def update_rpe(sport, activity_id, rpe):
    return True
    response = requests.get(f"{API}/activity/{activity_id}/update_rpe/?sport={sport}")
    if response.status_code == 200:
        pass

import os
import streamlit as st
import requests
from utils import handle_unauthorize, UnAuthorizeError


API = os.getenv("API_ENDPOINT", "http://127.0.0.1:8000")
API_GO = os.getenv("API_AUTH", "http://127.0.0.1:8080")


@st.dialog('Add a comment')
def add_comment(activity_id):
    comment = st.text_area("Write your comment here")
    headers = {"Authorization": f'Bearer {st.session_state["user_token"]["token"]}'}

    if st.button("Submit"):
        json = {
                    "comment_text": comment,
                }
        response = requests.post(
                f"{API_GO}/activities/{activity_id}/comments/",
                json=json,
                headers=headers
        )
        if response.status_code != 201:
            raise Exception(f'Error {response.status_code}')


def show_comment(conn, activity_id):
    headers = {"Authorization": f'Bearer {st.session_state["user_token"]["token"]}'}

    response = requests.get(
            f"{API_GO}/activities/{activity_id}/comments/",
            headers=headers
            )

    if response.status_code == 200:
        comments = response.json()[::-1]
    else:
        comments = [{"comment": "No comments yet"}]

    comment_section = """
        <div style='
            min-height: 100px;
            max-height: 200px;
            padding: 10px;
            border: 1px solid #ccc;
            border-radius: 5px;
            overflow-y: scroll;
            background-color: #f9f9f9;
        '>
    """

    for comment in comments:
        comment_section += f"""
            <div style='padding: 5px; margin-bottom: 5px; border-bottom: 1px solid #ddd;'>
                <div style='font-weight: bold; margin-bottom: 2px;'>
                    {comment['username']}
                </div>
                <div>
                    {comment['comment_text']}
                </div>
            </div>
        """

    # Close the scrollable container div
    comment_section += "</div>"

    # Render the entire comment section in one st.markdown call
    st.html(comment_section)


def get_rpe(sport, activity_id):
    response = requests.get(f"{API}/activity/{activity_id}/get_rpe/?sport={sport}")
    if response.status_code == 200:
        data = response.json()["data"]
        return data[0]["rpe"]
    else:
        return None


def rpe_setter(key, sport, activity_id):
    rpe = st.slider(
        "Rate of Perceived Exertion (RPE): 🟢 (1) - 🔴 (10)",
        min_value=1,
        max_value=10,
        value=1,
        step=1,
        key=key+"_slider")
    if st.button("Submit RPE", key=key+"_button"):
        status = post_rpe(sport, activity_id, rpe)
        return status


@handle_unauthorize
def post_rpe(sport, activity_id, rpe):
    json = {"activity_id": activity_id, "sport": sport, "rpe": rpe}
    headers = {"Authorization": f'Bearer {st.session_state["user_token"]["access_token"]}'}
    response = requests.post(f"{API}/activity/post_rpe/", json=json, headers=headers)
    if response.status_code == 401:
        raise UnAuthorizeError()
    elif response.status_code == 200:
        return response.json()["status"]


def update_rpe(sport, activity_id, rpe):
    return True
    response = requests.get(f"{API}/activity/{activity_id}/update_rpe/?sport={sport}")
    if response.status_code == 200:
        pass

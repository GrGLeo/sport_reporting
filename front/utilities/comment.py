import streamlit as st
import requests


def add_comment(activity_id):
    with st.expander("Add a Comment"):
        comment = st.text_area("Write your comment here")

        if st.button("Submit"):
            json = {
                        "activity_id": activity_id,
                        "comment_text": comment,
                        "user_id": st.session_state['user_token']
                    }
            response = requests.post(
                    "http://127.0.0.1:8000/post_comment",
                    json=json
            )


def write_comment(conn, activity_id):
    query = "select * from param.comment where activity_id = :activity_id"
    comments = conn.query(query, params={'activity_id': activity_id})
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

    for _, comment in comments.iterrows():
        comment_section += f"<div style='padding: 5px; margin-bottom: 5px; border-bottom: 1px solid #ddd;'>{comment.comment}</div>"

    # Close the scrollable container div
    comment_section += "</div>"

    # Render the entire comment section in one st.markdown call
    st.markdown(comment_section, unsafe_allow_html=True)

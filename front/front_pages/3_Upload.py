import os
import requests
import streamlit as st


API = os.getenv("API_ENDPOINT")


st.title("Fit File Upload")

uploaded_file = st.file_uploader("Choose a file", type=['fit', 'fits'])

app_type = ["application/fit", "application/fits"]

if uploaded_file is not None:
    user_id = str(st.session_state['user_token'])
    if uploaded_file.type in app_type:
        with st.spinner("Uploading file..."):
            file = {"file": uploaded_file.getvalue()}
            response = requests.post(
                f"{API}/uploadfile/",
                files=file,
                data={'user_id': user_id}
            )
            if response.status_code == 200:
                st.switch_page('front_pages/1_Calendar.py')
            else:
                st.toast('Upload failed, try again later')
    else:
        st.toast("Uploaded file is not a fit file")

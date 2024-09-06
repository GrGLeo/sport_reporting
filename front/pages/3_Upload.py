import requests
import streamlit as st


st.title("Fit File Upload")

uploaded_file = st.file_uploader("Choose a file", type=['fit', 'fits'])

app_type = ["application/fit", "application/fits"]

if uploaded_file is not None:
    if uploaded_file.type in app_type:
        with st.spinner("Uploading file..."):
            file = {"file": uploaded_file.getvalue()}
            response = requests.post(
                "http://127.0.0.1:8000/uploadfile/",
                files=file
            )
            if response.status_code == 200:
                st.switch_page('pages/1_Calendar.py')
            else:
                st.write('Upload failed, try again later')
    else:
        st.write("Uploaded file is not a fit file")
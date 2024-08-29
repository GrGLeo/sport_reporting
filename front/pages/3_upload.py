import requests
import streamlit as st

st.title("File Upload Example")

uploaded_file = st.file_uploader("Choose a file", type=['fit', 'fits'])

if uploaded_file is not None:
    if uploaded_file.type == "application/fit" or uploaded_file.type == "application/fits":
        with st.spinner("Uploading file..."):
            file = {"file": uploaded_file.getvalue()}
            response = requests.post("http://127.0.0.1:8000/uploadfile/", files=file)
            if response.status_code == 200:
                st.write(response.json()["data"])
            else:
                st.write("error")
    else:
        st.write("Uploaded file is not a fit file")
else:
    st.write("Please upload a file.")

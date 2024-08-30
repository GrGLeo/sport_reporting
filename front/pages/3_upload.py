import requests
import streamlit as st
import pandas as pd


st.title("Fit File Upload")

uploaded_file = st.file_uploader("Choose a file", type=['fit', 'fits'])

if uploaded_file is not None:
    if uploaded_file.type == "application/fit" or uploaded_file.type == "application/fits":
        with st.spinner("Uploading file..."):
            file = {"file": uploaded_file.getvalue()}
            response = requests.post("http://127.0.0.1:8000/uploadfile/", files=file)
            if response.status_code == 200:
                df = pd.DataFrame(response.json()["data"])
                st.session_state['activity'] = df
                st.write(df.columns)
            else:
                st.write("error")
    else:
        st.write("Uploaded file is not a fit file")

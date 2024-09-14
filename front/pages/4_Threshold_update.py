import streamlit as st
from sqlalchemy import text
import datetime

conn = st.connection('postgresql', type='sql')

st.title("Update Threshold")
with st.form(key='threshold_form'):
    col1, col2 = st.columns(2)
    with col1:
        css_minutes = st.slider("CSS Minutes", min_value=0, max_value=3, value=0, step=1)
    with col2:
        css_seconds = st.slider("CSS Seconds", min_value=0, max_value=59, value=0, step=1)

    col1, col2 = st.columns(2)
    with col1:
        run_pace_minutes = st.slider("Running Pace Minutes", min_value=2, max_value=8, value=0, step=1)
    with col2:
        run_pace_seconds = st.slider("Running Pace Seconds", min_value=0, max_value=59, value=0, step=1)

    ftp = st.number_input("Bike FTP", min_value=200, max_value=360, value=200, step=1)

    submit_button = st.form_submit_button(label='Submit')


if submit_button:
    query = """
        INSERT INTO param.user_threshold (swim, ftp, run_pace, date)
        VALUES (:swim, :ftp, :run_pace, :current_date);
        """
    params = {
        'swim': round(css_minutes + (css_seconds / 100), 2),
        'ftp': ftp,
        'run_pace': round(run_pace_minutes + (run_pace_seconds / 100), 2),
        'current_date': datetime.datetime.now()
    }
    with conn.session as session:
        session.execute(text(query), params=params)
        session.commit()
    st.toast('Threshold updated', icon="✅")

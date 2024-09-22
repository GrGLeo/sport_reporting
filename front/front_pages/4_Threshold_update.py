import streamlit as st
from sqlalchemy import text
import datetime

conn = st.connection('postgresql', type='sql')
user = st.session_state['user']

st.title("Update Threshold")
df_threshold = user.get_threshold()
swim_t, ftp_t, run_min, run_sec = 0, 200, 2, 0

if not df_threshold.empty:
    first_row = df_threshold.iloc[0]
    swim_t = first_row.get('swim', swim_t)
    ftp_t = first_row.get('ftp', ftp_t)
    run_t = first_row.get('run_pace', run_min + run_sec / 100)
    run_min = int(run_t)
    run_sec = (run_t - run_min) * 100

with st.form(key='threshold_form'):
    css_seconds = st.number_input("CSS in Seconds", min_value=0, max_value=359, value=swim_t, step=1)
    vma = st.number_input("Maximum Aerobic Speed", min_value=8.0, max_value=22.0, value=run_sec, step=0.01)
    ftp = st.number_input("Bike FTP", min_value=200, max_value=360, value=ftp_t, step=1)

    submit_button = st.form_submit_button(label='Submit')
    threshold = {
        "date": datetime.date.today().isoformat(),
        "swim": css_seconds,
        "ftp": ftp,
        "vma": vma
    }


if submit_button:
    user.update_threshold(threshold)
    st.toast('Threshold updated', icon="✅")

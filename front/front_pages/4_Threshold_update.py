import streamlit as st
from sqlalchemy import text
import datetime

conn = st.connection('postgresql', type='sql')
user = st.session_state['user']

st.title("Update Threshold")
df_threshold = user.get_threshold()
st.write(df_threshold)
swim_t, ftp_t, run_min, run_sec = 0, 200, 2, 0

if not df_threshold.empty:
    first_row = df_threshold.iloc[0]
    swim_t = first_row.get('swim', swim_t)
    ftp_t = first_row.get('ftp', ftp_t)
    run_t = first_row.get('run_pace', run_min + run_sec / 100)
    run_min = int(run_t)
    run_sec = int((run_t - run_min) * 100)

with st.form(key='threshold_form'):
    css_seconds = st.slider("CSS in Seconds", min_value=0, max_value=359, value=swim_t, step=1)

    col1, col2 = st.columns(2)
    with col1:
        run_pace_minutes = st.slider("Running Pace Minutes", min_value=2, max_value=8, value=run_min, step=1)
    with col2:
        run_pace_seconds = st.slider("Running Pace Seconds", min_value=0, max_value=59, value=run_sec, step=1)

    ftp = st.number_input("Bike FTP", min_value=200, max_value=360, value=ftp_t, step=1)

    submit_button = st.form_submit_button(label='Submit')


if submit_button:
    query = """
        INSERT INTO param.user_threshold (user_id, swim, ftp, run_pace, date)
        VALUES (:user_id, :swim, :ftp, :run_pace, :current_date);
        """
    params = {
        'user_id': st.session_state['user_token'],
        'swim': css_seconds,
        'ftp': ftp,
        'run_pace': round(run_pace_minutes + (run_pace_seconds / 100), 2),
        'current_date': datetime.datetime.now()
    }
    with conn.session as session:
        session.execute(text(query), params=params)
        session.commit()
    st.toast('Threshold updated', icon="✅")

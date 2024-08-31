import st
import datetime

Threshold = st.session_state.db_threshold
session = st.session_state.db_session

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
    new_threshold = Threshold(
        swim=round(css_minutes + (css_seconds / 100), 2),
        ftp=ftp,
        run_pace=round(run_pace_minutes + (run_pace_seconds / 100), 2),
        date=datetime.now()
    )
    session.add(new_threshold)
    session.commit()
    st.success('Threshold updated', icon="✅")

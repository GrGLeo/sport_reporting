import streamlit as st
from login import login_page, create_user_page


st.set_page_config(layout="wide")

home = st.Page(
        "front_pages/0_Home.py",
        title="Home",
        icon="🏠"
)

calendar = st.Page(
        "front_pages/1_Calendar.py",
        title="Calendar",
        icon="🗓"
)

analytics = st.Page(
        "front_pages/2_Analytics.py",
        title="Analytics",
        icon="📈"
)

upload = st.Page(
        "front_pages/3_Upload.py",
        title="Upload",
        icon="📄"
)

threshold = st.Page(
        "front_pages/4_Threshold_update.py",
        title="Threshold update",
        icon="⚙"
)

logged_page = [home, calendar, analytics]


if "user_token" not in st.session_state:
    pg = st.navigation([st.Page(login_page, default=True), st.Page(create_user_page)])
else:
    pg = st.navigation({"Analyze": logged_page} | {"Account": [upload, threshold]})

pg.run()

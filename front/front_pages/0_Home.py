import os
from datetime import date

import streamlit as st
from utilities.event import create_event
from utilities.home_page import write_weekly_stat, write_events, write_zone_time

from user.user import User

st.title("Welcome to your dashboard!")

db_host = os.getenv("DB_HOST", "localhost")
db_port = os.getenv("DB_PORT", "5432")
db_name = os.getenv("DB_NAME", "sporting")
db_user = os.getenv("DB_USER", "leo")
db_password = os.getenv("DB_PASSWORD", "postgres")


conn = st.connection(
    "postgresql",
    type="sql",
    host=db_host,
    port=db_port,
    database=db_name,
    username=db_user,
    password=db_password,
    dialect="postgresql"
)


user = User(st.session_state["user_token"]["token"], conn)

if "conn" not in st.session_state:
    st.session_state.conn = conn
if "user" not in st.session_state:
    st.session_state.user = user

# Force to upload threshold zone
threshold = user.get_threshold()
if threshold.empty:
    st.switch_page("front_pages/4_Threshold_update.py")


home_tab, zone_tab = st.tabs(["Home", "Zone"])
with home_tab:
    with st.expander("Add Event"):
        create_event(st.session_state["user_token"]["token"])
    today = date.today()

    # Event display
    try:
        df_events = user.get_events()
        write_events(df_events)
    except KeyError:
        st.write("No events registered yet!")

    st.header("Weekly Stats")
    try:
        total_wkt = user.get_full_workouts()
        df_week = total_wkt.groupby("week", as_index=False).agg(
            {"duration": "sum", "tss": "sum"}
        )
        write_weekly_stat(total_wkt, df_week)
    except KeyError:
        st.write("No workouts found.\n Upload your first workout.")


with zone_tab:
    st.header("Threshold")
    if not threshold.empty:
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric(label="Swim", value=threshold.swim)
        with col2:
            st.metric(label="Bike", value=threshold.ftp)
        with col3:
            st.metric(label="Run", value=threshold.vma)
    cycling_zone, run_zone = user.get_zones()
    cycling_zone.drop("user_id", axis=1, inplace=True)
    run_zone.drop("user_id", axis=1, inplace=True)
    st.header("Zone")
    swim_col, bike_col, run_col = st.columns(3)
    with swim_col:
        for columns in cycling_zone.columns:
            st.markdown(
                f"""
                <div class="zone-container swim">{columns.capitalize()}: {cycling_zone[columns].iloc[0]} W</b></div>
            """,
                unsafe_allow_html=True,
            )

    with bike_col:
        for columns in cycling_zone.columns:
            st.markdown(
                f"""
                <div class="zone-container bike">{columns.capitalize()}: {cycling_zone[columns].iloc[0]} W</b></div>
            """,
                unsafe_allow_html=True,
            )

    with run_col:
        for columns in run_zone.columns:
            st.markdown(
                f"""
                <div class="zone-container run">{columns.capitalize()}: {round(run_zone[columns].iloc[0], 2)} min/k</b></div>
            """,
                unsafe_allow_html=True,
            )

    st.markdown(
        """
        <style>
        .zone-container {
            padding: 10px;
            border-radius: 8px;
            margin-bottom: 10px;
            text-align: center;
            font-size: 20px;
            color: white;
        }

        /* Blue gradient for swim */
        .swim {
            background: linear-gradient(90deg, #4DD0E1, #26C6DA);  /* Blue */
        }

        /* Orange gradient for bike */
        .bike {
            background: linear-gradient(90deg, #FFECB3, #FF9800);  /* Orange */
        }

        /* Green gradient for run */
        .run {
            background: linear-gradient(90deg, #C8E6C9, #4CAF50);  /* Green */
        }
        </style>
    """,
        unsafe_allow_html=True,
    )

    # Get total time spent in zone
    # TODO don't compute it each time.
    try:
        total_wkt = user.get_full_workouts()
        write_zone_time(total_wkt)
    except KeyError:
        st.write("No workouts found.\n Upload your first workout.")

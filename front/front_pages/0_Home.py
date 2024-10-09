from datetime import date, timedelta

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from db_setup import Base, Threshold, engine, session
from metrics import calculate_all
from utilities.event import create_event

from front.user.user import User

st.title("Welcome to your dashboard!")

conn = st.connection("postgresql", type="sql")
user = User(st.session_state["user_token"], conn)

if "db_session" not in st.session_state:
    st.session_state.db_engine = engine
    st.session_state.db_session = session
    st.session_state.db_base = Base
    st.session_state.db_threshold = Threshold
    st.session_state.user = user

home_tab, zone_tab = st.tabs(["Home", "Zone"])
with home_tab:
    with st.expander("Add Event"):
        create_event(st.session_state["user_token"])
    today = date.today()

    # Event display
    df_events = user.get_events()
    cols = st.columns(len(df_events))
    for i, row in df_events.iterrows():
        cols[i].subheader(f"{row['name']} Priority: {row.priority}")
        cols[i].write(f"{row.date.strftime('%Y-%m-%d')}")
        cols[i].write(f"Sport: {row.sport}")
        difference = row.date - today
        weeks = difference.days // 7
        cols[i].write(f"Weeks remaining: {weeks}")

    st.header("Weekly Stats")
    total_wkt = user.get_full_workouts()
    df_week = total_wkt.groupby("week", as_index=False).agg(
        {"duration": "sum", "tss": "sum"}
    )

    col1, col2, col3 = st.columns(3)
    with col1:
        fig = px.bar(df_week, x="week", y="tss", text="tss", title="TSS/Week")

        # Customize the layout and style
        fig.update_traces(
            # Display TSS values with 2 decimal points
            texttemplate="%{text:.0f}",
            textposition="outside",  # Position the text outside the bar
        )
        # Add custom layout styling
        fig.update_layout(
            title_font_size=18,  # Title font size
            xaxis_title="Week Number",  # X-axis label
            yaxis_title="TSS (Training Stress Score)",  # Y-axis label
            hovermode="x",  # Show hover info on x-axis
        )
        tss_plot = st.plotly_chart(fig, on_select="rerun")
        week_selected = None
        if len(tss_plot["selection"]["points"]) > 0:
            week_selected = tss_plot["selection"]["points"][0]["x"]
    with col2:
        fig = px.bar(
            df_week,
            x="week",
            y="duration",
            text="duration",
            title="Duration/Week",
            orientation="v",
        )
        fig.update_traces(
            textposition="outside",  # Position the text outside the bar
        )
        # Add custom layout styling
        fig.update_layout(
            title_font_size=18,  # Title font size
            xaxis_title="Week Number",  # X-axis label
            yaxis_title="Duration (Minutes)",  # Y-axis label
            hovermode="x",  # Show hover info on x-axis
        )
        duration_plot = st.plotly_chart(fig, on_select="rerun")
        if len(duration_plot["selection"]["points"]) > 0:
            week_selected = duration_plot["selection"]["points"][0]["x"]
    with col3:
        if week_selected:
            df_sport = (
                total_wkt[total_wkt["week"] == week_selected]
                .groupby("sport", as_index=False)
                .agg({"duration": "sum"})
            )
        else:
            df_sport = (
                total_wkt[total_wkt["week"] == total_wkt["week"].max()]
                .groupby("sport", as_index=False)
                .agg({"duration": "sum"})
            )
        fig = px.pie(df_sport, names="sport", values="duration")
        st.plotly_chart(fig)

    # CTL, FORM, FITNESS
    df_daily = total_wkt.groupby("date", as_index=False).agg({"tss": "sum"})
    df_daily = df_daily.sort_values("date")
    df_daily = calculate_all(df_daily)

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=df_daily["date"],
            y=df_daily["ctl"],
            fill="tozeroy",
            name="Fitness",
            mode="none",
            fillcolor="rgba(200, 179, 125, 0.9)",
        )
    )

    fig.add_trace(
        go.Scatter(
            x=df_daily["date"],
            y=df_daily["atl"],
            fill="tonexty",
            name="Fatigue",
            mode="none",
        )
    )

    fig.add_trace(
        go.Scatter(
            x=df_daily["date"],
            y=df_daily["form"],
            name="Form",
        )
    )

    fig.add_trace(
        go.Bar(
            x=df_daily["date"],
            y=df_daily["tss"],
            name="TSS",
            marker=dict(color="rgba(0, 0, 0, 0.8)"),
        )
    )

    fig.update_layout(
        title="Fitness trend",
        xaxis_title="Date",
        yaxis_title="Values",
        barmode="overlay",
        xaxis={},
    )

    fitness_trend = st.plotly_chart(fig)

with zone_tab:
    st.header("Threshold")
    threshold = user.get_threshold()
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
    col1, col2, col3 = st.columns(3)

    with col1:
        view_time = st.slider(
            "Distribution over weeks", min_value=1, max_value=12, value=12
        )
        date_window = date.today() - timedelta(weeks=view_time)
        total_wkt["date"] = pd.to_datetime(total_wkt["date"]).dt.date
        total_zone = total_wkt[total_wkt["date"] >= date_window]
        zone = ["recovery", "endurance", "tempo", "threshold", "vo2max"]
        total_zone = total_zone[zone]
        total_zone["g"] = 1

        total_zone = total_zone.groupby("g", as_index=False).agg(
            {col: "sum" for col in zone}
        )

        long_zone = total_zone.melt(
            id_vars=["g"],
            value_vars=["recovery", "endurance",
                        "tempo", "threshold", "vo2max"],
            var_name="zone",
            value_name="value",
        )

        fig = px.pie(
            long_zone, names="zone", values="value", title="Zones Distribution"
        )

        st.plotly_chart(fig)

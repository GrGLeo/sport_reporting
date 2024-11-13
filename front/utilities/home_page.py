import streamlit as st
from datetime import date, timedelta
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from metrics import calculate_all


def write_weekly_stat(total_wkt, df_week):
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

    st.plotly_chart(fig)


def write_events(df_events):
    for i, row in df_events.iterrows():
        cols = st.columns(len(df_events))
        cols[i].subheader(f"{row['name']} Priority: {row.priority}")
        cols[i].write(f"{row.date.strftime('%Y-%m-%d')}")
        cols[i].write(f"Sport: {row.sport}")
        difference = row.date.date() - date.today()
        weeks = difference.days // 7
        cols[i].write(f"Weeks remaining: {weeks}")


def write_zone_time(total_wkt):
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

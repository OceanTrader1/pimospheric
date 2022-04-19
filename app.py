"""
app.py

Hosts the streamlit.io web application for viewing the
data in a web browser.
"""

import sys

import streamlit as st
from streamlit_autorefresh import st_autorefresh as st_refresh
import pandas as pd
import altair as alt

from libdb import Database
from libbme280 import BME280SENSOR

def space(num_lines=1):
    """Adds empty line"""
    for _ in range(num_lines):
        st.write("")

def table_builder(
    df, x: str, y: str, title: str, x_axis_label: str, y_axis_label: str
    ):
    source = df[[x, y]]
    c = \
        alt.Chart(source, title=title)\
        .mark_line()\
        .encode(
            x=alt.X(
                x, 
                title=x_axis_label,
                axis=alt.Axis(
                    labelAngle=-45,
                    format="%m/%d %H:%M",
                )
            ), 
            y=alt.Y(
                y,
                title=y_axis_label,
                scale=alt.Scale(
                    domain=[
                        df[y].min()-1, df[y].max()+1
                    ]
                )
            ),
            tooltip=[x, y]
        )
    st.altair_chart(c.interactive(), use_container_width=True)


def main():
    """ Main loop
    
    Arguments:
        - ticker: int   The interval at which to collect the data 
                        (e.g. every {ticker} seconds).
    """
    # Polling Rate - The interval at which to collect the data in seconds
    pr = 5 

    # Create sensor
    bme280 = BME280SENSOR()

    # Import database
    d = Database()

    try:
        st.set_page_config(
            layout="centered", page_icon="⛅", page_title="Pimospheric"
        )
        st.title("Weather Data")

        # Implement Refresh (comment out st_refresh to disable refresh)
        # n * (1000) milliseconds
        refresh_rate_in_seconds = lambda r: r * 1000
        st_refresh(
            interval=refresh_rate_in_seconds(pr), key="df"
        )

        # Read data
        df = d.read()

        # Sample data from sensor and write to database
        bme280.update()

        c_to_f = lambda f: (9 / 5) * f + 32
        # Convert temperature from Celsius to Fahrenheit
        df["temperature"] = df["temperature"].apply(c_to_f) 
        # Convert dew point from Celsius to Fahrenheit
        df["dew_point"] = df["dew_point"].apply(c_to_f)
        df = df.round({
            "temperature": 1, "altitude": 1, "humidity": 1, 
            "dew_point": 1,   "pressure": 1,
        })

        # Convert and round tables values
        df["date"] = pd.to_datetime(df.date)
        df["date"] = df.date.round("1s")
        df["date"] = df["date"].dt.tz_localize("US/Central")

        col1, col2, col3, col4, col5 = st.columns(5)
        with col1:
            try:
                st.metric(
                    label="Temperature (F)", 
                    value="{:.1f}".format(df["temperature"].iloc[-1]),
                    delta="{:.2f}".format(
                        df["temperature"].iloc[-1] - df["temperature"].iloc[-60 * 1]
                    ),
                )
            except IndexError:
                st.metric(
                    label="Temperature (F)", 
                    value="0",
                    delta="0",
                )
        with col2:
            try:
                st.metric(
                    label="Pressure (hPa)", 
                    value="{:.1f}".format(df["pressure"].iloc[-1]),
                    delta="{:.2f}".format(
                        df["pressure"].iloc[-1] - df["pressure"].iloc[-60 * 1]
                    ),
                )
            except IndexError:
                st.metric(
                    label="Pressure (hPa)", 
                    value="0",
                    delta="0",
                )
        with col3:
            try:
                st.metric(
                    label="Humidity (%)", 
                    value="{:.1f}".format(df["humidity"].iloc[-1]),
                    delta="{:.2f}".format(
                        df["humidity"].iloc[-1] - df["humidity"].iloc[-60 * 1]
                    ),
                )
            except IndexError:
                st.metric(
                    label="Humidity (%)", 
                    value="0",
                    delta="0",
                )
        with col4:
            try:
                st.metric(
                    label="Altitude (m)", 
                    value="{:.1f}".format(df["altitude"].iloc[-1]),
                    delta="{:.2f}".format(
                        df["altitude"].iloc[-1] - df["altitude"].iloc[-60 * 1]
                    ),
                )
            except IndexError:
                st.metric(
                    label="Altitude (m)", 
                    value="0",
                    delta="0",
                )
        with col5:
            try:
                st.metric(
                    label="Dew Point (F)", 
                    value="{:.1f}".format(df["dew_point"].iloc[-1]),
                    delta="{:.2f}".format(
                        df["dew_point"].iloc[-1] - df["dew_point"].iloc[-60 * 1]
                    ),
                )
            except IndexError:
                st.metric(
                    label="Dew Point (F)", 
                    value="0",
                    delta="0",
                )

        table_builder(
            df, 
            "date", 
            "temperature", 
            "Temperature over Time",
            "Date",
            "Temperature (F)",
        )
        table_builder(
            df, 
            "date", 
            "humidity", 
            "Humidity over Time",
            "Date",
            "Humidity (%)",
        )
        table_builder(
            df, 
            "date", 
            "pressure", 
            "Pressure over Time",
            "Date",
            "Pressure (hPa)",
        )
        table_builder(
            df, 
            "date", 
            "altitude", 
            "Altitude over Time",
            "Date",
            "Altitude (m)",
        )
        table_builder(
            df, 
            "date", 
            "dew_point", 
            "Dew Point over Time",
            "Date",
            "Dew Point (F)",
        )

    except KeyboardInterrupt:
        print(f"Exited via KeyboardInterrupt")
    

if __name__ == "__main__":
    main()


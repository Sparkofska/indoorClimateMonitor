import streamlit as st
import pandas as pd
import datetime

from sensor import ClimateSensor
from database import ClimateData, Database

import plotly.graph_objects as go
from plotly.subplots import make_subplots


@st.cache_resource
def get_sensor(name):
    return ClimateSensor()


@st.cache_resource
def get_database(name):
    return Database('db.sqlite')


@st.cache_data(ttl=60) # invalidate cache after 1 minute
def get_data():
    raw_data = get_database('climatedb').read()
    return pd.DataFrame(raw_data, columns=ClimateData._fields)


def format_datetime(dt):
    return dt.strftime("%d.%m.%Y %H:%M:%S")

st.title('indoor Climate Monitor')


st.subheader('Historic data')

data = get_data()

if not data.empty:
    start, end = data.timestamp.min(), data.timestamp.max()

    st.markdown(f"Measurements from **{format_datetime(start)}** to **{format_datetime(end)}**")

    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(go.Scatter(x=data.timestamp, y=data.temperature, name="temperature"), secondary_y=False)
    fig.add_trace(go.Scatter(x=data.timestamp, y=data.humidity, name="humidity"), secondary_y=True)

    fig.update_yaxes(title_text="°C", secondary_y=False)
    fig.update_yaxes(title_text="%", secondary_y=True)

    st.plotly_chart(fig)

else:
    st.write('No data recorded yet')


st.subheader('Current data')

with st.spinner("Measuring..."):

    sensor = get_sensor('climate')
    temperature, humidity = sensor.read()

    st.markdown(f'Measurement from **{format_datetime(datetime.datetime.now())}**')

    col1, col2, col3 = st.columns(3)
    col1.metric("Temperature", f'{temperature} °C')
    col2.metric("Humidity", f'{humidity} %')
    col3.button("Measure now")




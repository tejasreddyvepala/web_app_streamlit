
import streamlit as st
import numpy as np
import pandas as pd
import pydeck as pdk
import plotly.express as px


DATA_URL = (
    "https://github.com/chairielazizi/streamlit-collision/blob/master/Motor_Vehicle_Collisions_-_Crashes.csv?raw=true"
    )

st.title("Motor Vehicle Collisions in New york City")

@st.cache_data(persist=True)
def load_data(nrows):
    data = pd.read_csv(DATA_URL,nrows = nrows,parse_dates=[['CRASH_DATE','CRASH_TIME']])
    data.dropna(subset=['LATITUDE','LONGITUDE'],inplace=True)
    lowercase = lambda x: str(x).lower()
    data.rename(lowercase,axis='columns',inplace=True)
    data.rename(columns = {'crash_date_crash_time':'date/time'},inplace=True)
    return data

data = load_data(100000)

original_data = data

#visualize data on map
st.header("where are the most poeple injured in new york city")
injured_people = st.slider("number of persons injured",0,19)
st.map(data.query("injured_persons >= @injured_people")[['latitude','longitude']].dropna(how="any"))

st.header("how many collisions occur during a given time of the day?")
hour = st.selectbox("hour to look at", range(0,24),1)
data = data[data['date/time'].dt.hour == hour]

st.markdown("vehicle collisions between %i:00 and %i:00" % (hour,(hour+1)%24))

midpoint = (np.average(data['latitude']),np.average(data['longitude']))

st.write(pdk.Deck(
    map_style = "mapbox://styles/mapbox/light-v9",
    initial_view_state = {
        'latitude':midpoint[0],
        'longitude':midpoint[1],
        "zoom":11,
        "pitch":50,
        },
    layers=[
        pdk.Layer(
            "HexagonLayer",
            data = data[['date/time','latitude','longitude']],
            get_position=['latitude','longitude'],
            radius = 100,
            #extruded = True,
            pickable = True,
            elevation_scale = 4,
            elevation_range = [0,1000],
            ),
        ],
    ))

st.subheader("Breakdown by minute between %i:00 and %i:00" % (hour,(hour+1)%24))

filtered = data[
    (
     data['date/time'].dt.hour>=hour) & (data['date/time'].dt.hour<(hour+1))]

hist = np.histogram(filtered['date/time'].dt.minute,bins=60,range=(0,60))[0]

chart_data = pd.DataFrame({'minute':range(60),'crashes':hist})

fig = px.bar(chart_data,x='minute',y='crashes',hover_data=['minute','crashes'],height=400)

st.write(fig)

st.header("Top 5 dangerous streets by affected type")

select = st.selectbox('Affected type of people',['pedestrians','cyclists','motorists'])

if select == 'pedestrians':
    st.write(original_data.query("injured_pedestrians >= 1")[["on_street_name","injured_pedestrians"]].sort_values(by = ["injured_pedestrians"],ascending = False).dropna(how = "any")[0:5])  
elif select == 'cyclists':
    st.write(original_data.query("injured_cyclists >= 1")[["on_street_name","injured_cyclists"]].sort_values(by = ["injured_cyclists"],ascending = False).dropna(how = "any")[0:5])
else:
    st.write(original_data.query("injured_motorists >= 1")[["on_street_name","injured_motorists"]].sort_values(by = ["injured_motorists"],ascending = False).dropna(how = "any")[0:5])


if st.checkbox("Show Raw Data",False):
    st.subheader("Raw Data")
    st.write(data)
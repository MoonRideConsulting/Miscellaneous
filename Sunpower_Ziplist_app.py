import streamlit as st
from streamlit_gsheets import GSheetsConnection
import geopandas as gpd
import altair as alt
import pandas as pd
import folium
import requests
import os
import plotly.express as px
from geopy.geocoders import Nominatim


st.set_page_config(page_title="SunPower Overview Dash",page_icon="🧑‍🚀",layout="wide")

def password_protection():
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
        
    if not st.session_state.authenticated:
        password = st.text_input("Enter Password:", type="password")
        correct_hashed_password = "Sunpower1234"
        
        if st.button("Login"):
            if password == correct_hashed_password:
                st.session_state.authenticated = True
                main_dashboard()
            else:
                st.error("Incorrect Password. Please try again or contact the administrator.")
    else:
        main_dashboard()

# Initialize the geolocator
geolocator = Nominatim(user_agent="geoapiExercises")

# Define the function to get latitude and longitude
def get_lat_lon(zip_code):
    location = geolocator.geocode(f"{zip_code}, USA")
    if location:
        return location.latitude, location.longitude
    else:
        return None, None

def main_dashboard():
    st.markdown("<h1 style='text-align: center;'>SunPower Tiered Zip List Map</h1>", unsafe_allow_html=True)
    
    # Create a connection object.
    conn = st.connection("gsheets", type=GSheetsConnection)

    df = conn.read(
        worksheet="Zips",
        ttl="10m",
        usecols=[0, 1, 2, 3]
    )

    # Find the index of the first row where the ZIP Code is blank or NaN
    first_blank_index = df[df['ZIP Code'].isnull() | (df['ZIP Code'] == '')].index.min()

    # If there's a blank entry, slice the DataFrame to exclude any rows after the first blank entry
    if pd.notnull(first_blank_index):
        df = df.loc[:first_blank_index - 1]
    
    df['ZIP Code'] = df['ZIP Code'].apply(lambda x: str(int(float(x))).zfill(5))

    # Enable the VegaFusion data transformer
    alt.data_transformers.enable('vegafusion')

    # Identify the unique states in your dataset
    #states = df['State'].unique()

    gdf = pd.read_csv('us_zip_codes_to_longitude_and_latitude.csv')
    
    # Load GeoJSON data for ZIP codes
    gdf['Zip'] = gdf['Zip'].astype(str)
    gdf['Zip'] = gdf['Zip'].apply(lambda x: str(int(float(x))).zfill(5))
    
    # Merge the DataFrame with the GeoJSON data
    merged_data = gdf.merge(df, left_on='Zip', right_on='ZIP Code')

    st.write(df.shape)
    st.write(merged_data.shape)
    
    # Assuming 'df' is your DataFrame and it has 'lat' and 'lng' columns for latitude and longitude
    # and 'New Tier' as the column you want to visualize
    fig = px.scatter_geo(merged_data,
                         lat='Latitude',
                         lon='Longitude',
                         color='New Tier',
                         hover_name='Zip',  # Show ZIP Code in the tooltip
                         hover_data={'Latitude': False, 'Longitude': False, 'New Tier': True},
                         scope='usa',
                         color_continuous_scale='Viridis',
                         title='ZIP Code Data Visualization')
    st.plotly_chart(fig, use_container_width=True)


    # Convert ZIP code columns to string if they are not already
    df['ZIP Code'] = df['ZIP Code'].astype(str)
    merged_data['ZIP'] = merged_data['ZIP'].astype(str)  # Adjust the column name 'ZIP' as per your merged_data

    # Find ZIP codes in df that are not in merged_data
    missing_zips = set(df['ZIP Code']) - set(merged_data['ZIP'])

    # Convert the set to a list
    missing_zip_list = list(missing_zips)
    st.write("Missing ZIP codes:", missing_zip_list)


if __name__ == '__main__':
    password_protection()

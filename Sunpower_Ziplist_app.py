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

    gdf = pd.read_csv('Zip_LatLog.csv')
    
    # Load GeoJSON data for ZIP codes
    gdf['ZIP'] = gdf['ZIP'].astype(str)

    st.write(gdf.columns)
    st.write(df.columns)

    # Merge the DataFrame with the GeoJSON data
    merged_data = gdf.merge(df, left_on='ZIP', right_on='Zip Code')
    
    st.write(df.shape)
    st.write(merged_data.shape)
    st.write(merged_data)



if __name__ == '__main__':
    password_protection()

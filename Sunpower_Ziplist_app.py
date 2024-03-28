import streamlit as st
from streamlit_gsheets import GSheetsConnection
import geopandas as gpd
import altair as alt
import pandas as pd
import folium
import requests
import os
import plotly.express as px

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
    states = df['State'].unique()

    gdf = pd.read_csv('geo_df_allstates(simple.01).csv')
    
    # Load GeoJSON data for ZIP codes
    #zip_geojson = gpd.read_file('ZIP_Codes.geojson')
    gdf['ZCTA5CE10'] = gdf['ZCTA5CE10'].astype(str)

    # Merge the DataFrame with the GeoJSON data
    merged_data = gdf.merge(df, left_on='ZCTA5CE10', right_on='ZIP Code')

    # Convert the 'geometry' column to string to avoid serialization issues
    #merged_data['geometry'] = merged_data['geometry'].astype(str)

    st.write(merged_data.shape)
    st.write(merged_data)
    st.write(merged_data.columns)

    # Generate the choropleth map
    fig = px.choropleth(merged_data,
                    geojson=merged_data.geometry.__geo_interface__,
                    locations='ZCTA5CE10',
                    color="New Tier",  # Adjust with your column name
                    color_continuous_scale="Viridis",
                    featureidkey="properties.ZCTA5CE10",
                    scope="usa",
                    labels={'New Tier': 'Tier Label'}  # Adjust label as needed
                   )

    fig.update_geos(fitbounds="locations", visible=False)
    fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})

    # Display the figure in Streamlit
    st.plotly_chart(fig)


if __name__ == '__main__':
    password_protection()

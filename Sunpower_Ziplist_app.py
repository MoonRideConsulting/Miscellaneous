import streamlit as st
from streamlit_gsheets import GSheetsConnection
import geopandas as gpd
import altair as alt
import pandas as pd
import folium
import requests
import os

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

state_geojson_map = {
    'AL': 'al_alabama_zip_codes_geo.min.json',
    'AK': 'ak_alaska_zip_codes_geo.min.json',
    'AZ': 'az_arizona_zip_codes_geo.min.json',
    'AR': 'ar_arkansas_zip_codes_geo.min.json',
    'CA': 'ca_california_zip_codes_geo.min.json',
    'CO': 'co_colorado_zip_codes_geo.min.json',
    'CT': 'ct_connecticut_zip_codes_geo.min.json',
    'DE': 'de_delaware_zip_codes_geo.min.json',
    'FL': 'fl_florida_zip_codes_geo.min.json',
    'GA': 'ga_georgia_zip_codes_geo.min.json',
    'HI': 'hi_hawaii_zip_codes_geo.min.json',
    'ID': 'id_idaho_zip_codes_geo.min.json',
    'IL': 'il_illinois_zip_codes_geo.min.json',
    'IN': 'in_indiana_zip_codes_geo.min.json',
    'IA': 'ia_iowa_zip_codes_geo.min.json',
    'KS': 'ks_kansas_zip_codes_geo.min.json',
    'KY': 'ky_kentucky_zip_codes_geo.min.json',
    'LA': 'la_louisiana_zip_codes_geo.min.json',
    'ME': 'me_maine_zip_codes_geo.min.json',
    'MD': 'md_maryland_zip_codes_geo.min.json',
    'MA': 'ma_massachusetts_zip_codes_geo.min.json',
    'MI': 'mi_michigan_zip_codes_geo.min.json',
    'MN': 'mn_minnesota_zip_codes_geo.min.json',
    'MS': 'ms_mississippi_zip_codes_geo.min.json',
    'MO': 'mo_missouri_zip_codes_geo.min.json',
    'MT': 'mt_montana_zip_codes_geo.min.json',
    'NE': 'ne_nebraska_zip_codes_geo.min.json',
    'NV': 'nv_nevada_zip_codes_geo.min.json',
    'NH': 'nh_new_hampshire_zip_codes_geo.min.json',
    'NJ': 'nj_new_jersey_zip_codes_geo.min.json',
    'NM': 'nm_new_mexico_zip_codes_geo.min.json',
    'NY': 'ny_new_york_zip_codes_geo.min.json',
    'NC': 'nc_north_carolina_zip_codes_geo.min.json',
    'ND': 'nd_north_dakota_zip_codes_geo.min.json',
    'OH': 'oh_ohio_zip_codes_geo.min.json',
    'OK': 'ok_oklahoma_zip_codes_geo.min.json',
    'OR': 'or_oregon_zip_codes_geo.min.json',
    'PA': 'pa_pennsylvania_zip_codes_geo.min.json',
    'RI': 'ri_rhode_island_zip_codes_geo.min.json',
    'SC': 'sc_south_carolina_zip_codes_geo.min.json',
    'SD': 'sd_south_dakota_zip_codes_geo.min.json',
    'TN': 'tn_tennessee_zip_codes_geo.min.json',
    'TX': 'tx_texas_zip_codes_geo.min.json',
    'UT': 'ut_utah_zip_codes_geo.min.json',
    'VT': 'vt_vermont_zip_codes_geo.min.json',
    'VA': 'va_virginia_zip_codes_geo.min.json',
    'WA': 'wa_washington_zip_codes_geo.min.json',
    'WV': 'wv_west_virginia_zip_codes_geo.min.json',
    'WI': 'wi_wisconsin_zip_codes_geo.min.json',
    'WY': 'wy_wyoming_zip_codes_geo.min.json',
    'DC': 'dc_district_of_columbia_zip_codes_geo.min.json'
}


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

    # Base URL for the GeoJSON files
    base_url = 'https://raw.githubusercontent.com/OpenDataDE/State-zip-code-GeoJSON/master/'

    # Directory to save the GeoJSON files
    geojson_dir = 'geojson_files'
    os.makedirs(geojson_dir, exist_ok=True)

    # Download the necessary GeoJSON files
    for state in states:
        if state in state_geojson_map:
            geojson_filename = state_geojson_map[state]
            geojson_url = f'{base_url}{geojson_filename}'
        
            response = requests.get(geojson_url)
            st.write(response)
            if response.status_code == 200:
                with open(os.path.join(geojson_dir, geojson_filename), 'wb') as f:
                    f.write(response.content)
                print(f'Downloaded {geojson_filename}')
            else:
                print(f'Failed to download {geojson_filename}')
        else:
            print(f'GeoJSON file for {state} not found in the mapping.')
    
    # Load GeoJSON data for ZIP codes
    #zip_geojson = gpd.read_file('ZIP_Codes.geojson')
    #zip_geojson['ZIPCODE'] = zip_geojson['ZIPCODE'].astype(str)

    # Merge the DataFrame with the GeoJSON data
    #merged_data = zip_geojson.merge(df, left_on='ZIPCODE', right_on='ZIP Code')

    # Convert the 'geometry' column to string to avoid serialization issues
    #merged_data['geometry'] = merged_data['geometry'].astype(str)

    #st.write(merged_data)


if __name__ == '__main__':
    password_protection()

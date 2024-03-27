import streamlit as st
from streamlit_gsheets import GSheetsConnection
import geopandas as gpd
import altair as alt
import pandas as pd

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
    
    st.write(df)

    first_blank_index = df[df['ZIP Code'].isnull() | (df['ZIP Code'] == '')].index.min()

    # Enable the VegaFusion data transformer
    alt.data_transformers.enable('vegafusion')

    # Load GeoJSON data for ZIP codes
    zip_geojson = gpd.read_file('ZIP_Codes.geojson')
    st.write(zip_geojson)

    # Merge the DataFrame with the GeoJSON data
    merged_data = zip_geojson.merge(df, left_on='ZIPCODE', right_on='ZIP Code')

    # Convert the 'geometry' column to string to avoid serialization issues
    merged_data['geometry'] = merged_data['geometry'].astype(str)

    # Create the Altair visualization
    chart = alt.Chart(merged_data).mark_geoshape().encode(
        color='New Tier:Q',  # Assuming 'New Tier' is a quantitative measure
        tooltip=['ZIP Code:N', 'State:N', 'New Tier:Q', 'UTILITY EXCEPTION:N']
    ).properties(
        width=500,
        height=300
    )

    # Display in Streamlit
    st.altair_chart(chart, use_container_width=True)

if __name__ == '__main__':
    password_protection()

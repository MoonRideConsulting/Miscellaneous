import streamlit as st
from streamlit_gsheets import GSheetsConnection
import geopandas as gpd
import altair as alt

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

    df['ZIP Code'] = df['ZIP Code'].apply(lambda x: str(int(float(x))).zfill(5))
    
    st.write(df)


    # Enable the VegaFusion data transformer
    alt.data_transformers.enable('vegafusion')

    # Load GeoJSON data for ZIP codes
    geojson_data = gpd.read_file('ZIP_Codes.geojson')

    # Create an Altair chart
    chart = alt.Chart(geojson_data).mark_geoshape().encode(
        color='New Tier:Q',  # Quantitative color scale based on the New Tier values
        tooltip=['ZIP Code:N', 'State:N', 'New Tier:Q', 'UTILITY EXCEPTION:N']  # Tooltip content
    ).transform_lookup(
        lookup='id',
        from_=alt.LookupData(df, 'ZIP Code', ['ZIP Code', 'State', 'New Tier', 'UTILITY EXCEPTION'])
    ).project(
        type='albersUsa'  # Projection type for the USA; change if needed
    ).properties(
        width=800,
        height=400
    )

    # Display the chart in Streamlit
    st.altair_chart(chart, use_container_width=True)


if __name__ == '__main__':
    password_protection()

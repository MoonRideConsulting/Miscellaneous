import streamlit as st
from streamlit_gsheets import GSheetsConnection

st.set_page_config(page_title="SunPower Overview Dash",page_icon="🧑‍🚀",layout="wide")

# Create a connection object.
conn = st.connection("gsheets", type=GSheetsConnection)

df = conn.read(
    worksheet="Zips",
    ttl="10m",
    usecols=[0, 1, 2, 3]
)

st.write(df)


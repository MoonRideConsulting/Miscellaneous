import streamlit as st
from streamlit_gsheets import GSheetsConnection

# Create a connection object.
conn = st.connection("gsheets", type=GSheetsConnection)

df = conn.read(
    worksheet="Zips",
    ttl="10m",
    usecols=[0, 1],
    nrows=3,
)

st.write(df)
